import os

from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from google.genai import Client

from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.configuration import Configuration, LLMProvider
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.chat_models import ChatOllama, ChatOpenAI
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)

load_dotenv()

# Global genai_client for web_research:
# NOTE: This client is initialized ONCE at startup using GEMINI_API_KEY from environment variables.
# It will NOT use any 'gemini_api_key' provided in request-time configurations for the web_research node.
# Web research will only function if a valid GEMINI_API_KEY is set in the environment.
# To make web_research respect request-time API keys, this client would need to be
# instantiated within the web_research node using 'configurable.gemini_api_key'.
_gemini_api_key_env = os.getenv("GEMINI_API_KEY")
genai_client = Client(api_key=_gemini_api_key_env) if _gemini_api_key_env else None
# We allow genai_client to be None if key is not set, web_research will fail if it's used without a key.


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph node that generates a search queries based on the User's question.

    Uses Gemini 2.0 Flash to create an optimized search query for web research based on
    the User's question.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated query
    """
    configurable = Configuration.from_runnable_config(config)

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    # Instantiate the appropriate LLM based on the provider
    if configurable.llm_provider == LLMProvider.OLLAMA:
        if not configurable.ollama_base_url or not configurable.ollama_model_name:
            raise ValueError("Ollama base URL or model name not configured for query generation.")
        llm = ChatOllama(
            base_url=configurable.ollama_base_url,
            model=configurable.ollama_model_name,
            temperature=1.0,
        )
    elif configurable.llm_provider == LLMProvider.LMSTUDIO:
        if not configurable.lmstudio_base_url or not configurable.lmstudio_model_name:
            raise ValueError("LM Studio base URL or model name not configured for query generation.")
        llm = ChatOpenAI(
            base_url=configurable.lmstudio_base_url,
            model_name=configurable.lmstudio_model_name,
            api_key="not-needed",  # LM Studio doesn't require an API key
            temperature=1.0,
            max_retries=2,
        )
    elif configurable.llm_provider == LLMProvider.GEMINI:
        if not configurable.gemini_api_key:
            raise ValueError("Gemini API key not configured for LLMProvider.GEMINI.")
        llm = ChatGoogleGenerativeAI(
            model=configurable.query_generator_model,
            temperature=1.0,
            max_retries=2,
            api_key=configurable.gemini_api_key,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {configurable.llm_provider}")

    structured_llm = llm.with_structured_output(SearchQueryList)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    # Generate the search queries
    result = structured_llm.invoke(formatted_prompt)
    return {"query_list": result.query}


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph node that performs web research using the native Google Search API tool.

    Executes a web search using the native Google Search API tool in combination with Gemini 2.0 Flash.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including search API settings

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """
    # Configure
    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )

    # NOTE: genai_client is initialized globally using GEMINI_API_KEY from environment variables.
    # It does not use request-time 'gemini_api_key' from 'configurable'.
    # Web research will fail if the environment GEMINI_API_KEY was not set at startup.
    if not genai_client:
        raise ValueError(
            "Gemini API key not configured in environment, web research is unavailable."
        )

    # Uses the google genai client as the langchain client doesn't return grounding metadata
    response = genai_client.models.generate_content(
        model=configurable.query_generator_model, # This model should be a Gemini model
        contents=formatted_prompt,
        config={
            "tools": [{"google_search": {}}],
            "temperature": 0,
        },
    )
    # resolve the urls to short urls for saving tokens and time
    resolved_urls = resolve_urls(
        response.candidates[0].grounding_metadata.grounding_chunks, state["id"]
    )
    # Gets the citations and adds them to the generated text
    citations = get_citations(response, resolved_urls)
    modified_text = insert_citation_markers(response.text, citations)
    sources_gathered = [item for citation in citations for item in citation["segments"]]

    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [modified_text],
    }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )

    # Instantiate the appropriate LLM for reflection
    if configurable.llm_provider == LLMProvider.OLLAMA:
        if not configurable.ollama_base_url or not configurable.ollama_model_name:
            raise ValueError("Ollama base URL or model name not configured for reflection.")
        llm = ChatOllama(
            base_url=configurable.ollama_base_url,
            model=configurable.ollama_model_name,
            temperature=1.0,
        )
    elif configurable.llm_provider == LLMProvider.LMSTUDIO:
        if not configurable.lmstudio_base_url or not configurable.lmstudio_model_name:
            raise ValueError("LM Studio base URL or model name not configured for reflection.")
        llm = ChatOpenAI(
            base_url=configurable.lmstudio_base_url,
            model_name=configurable.lmstudio_model_name,
            api_key="not-needed",
            temperature=1.0,
            max_retries=2,
        )
    elif configurable.llm_provider == LLMProvider.GEMINI:
        # Use reflection_model for Gemini, or ollama/lmstudio_model_name for others
        if not configurable.gemini_api_key:
            raise ValueError("Gemini API key not configured for LLMProvider.GEMINI.")
        model_name = configurable.reflection_model
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=1.0,
            max_retries=2,
            api_key=configurable.gemini_api_key,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {configurable.llm_provider}")

    result = llm.with_structured_output(Reflection).invoke(formatted_prompt)

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.

    Args:
        state: Current graph state containing the running summary and sources gathered

    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary with sources
    """
    configurable = Configuration.from_runnable_config(config)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    # Instantiate the appropriate LLM for finalizing the answer
    if configurable.llm_provider == LLMProvider.OLLAMA:
        if not configurable.ollama_base_url or not configurable.ollama_model_name:
            raise ValueError("Ollama base URL or model name not configured for answer finalization.")
        llm = ChatOllama(
            base_url=configurable.ollama_base_url,
            model=configurable.ollama_model_name,
            temperature=0,
        )
    elif configurable.llm_provider == LLMProvider.LMSTUDIO:
        if not configurable.lmstudio_base_url or not configurable.lmstudio_model_name:
            raise ValueError("LM Studio base URL or model name not configured for answer finalization.")
        llm = ChatOpenAI(
            base_url=configurable.lmstudio_base_url,
            model_name=configurable.lmstudio_model_name,
            api_key="not-needed",
            temperature=0,
            max_retries=2,
        )
    elif configurable.llm_provider == LLMProvider.GEMINI:
        # Use answer_model for Gemini, or ollama/lmstudio_model_name for others
        if not configurable.gemini_api_key:
            raise ValueError("Gemini API key not configured for LLMProvider.GEMINI.")
        model_name = configurable.answer_model
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            max_retries=2,
            api_key=configurable.gemini_api_key,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {configurable.llm_provider}")

    result = llm.invoke(formatted_prompt)

    # Replace the short urls with the original urls and add all used urls to the sources_gathered
    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in result.content:
            result.content = result.content.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)

    return {
        "messages": [AIMessage(content=result.content)],
        "sources_gathered": unique_sources,
    }


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
