import os
from typing import Any, Dict, List, Optional, Tuple

from src.agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from google.genai import Client

from src.agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from src.agent.configuration import Configuration
from src.agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from src.agent.utils.prompt_personality import create_enhanced_prompt, create_system_message, create_intelligent_system_message
from langchain_google_genai import ChatGoogleGenerativeAI
# TODO: Re-enable when utils dependencies are available
# from agent.utils import (
#     get_citations,
#     get_research_topic,
#     insert_citation_markers,
#     resolve_urls,
# )

# Temporary simple implementations
def get_research_topic(messages):
    """Simple implementation to get research topic from messages"""
    if not messages:
        return "research query"

    for msg in reversed(messages):
        if hasattr(msg, 'content') and msg.content:
            return msg.content[:100]  # First 100 chars
    return "research query"

def resolve_urls(grounding_chunks, query_id):
    """Simple implementation for URL resolution"""
    try:
        # This is a placeholder implementation
        # In a real implementation, we would process the grounding_chunks
        # and resolve the URLs
        return [{
            "original_url": "https://example.com/source",
            "short_url": f"[{query_id}]",
            "id": query_id
        }]
    except Exception as e:
        print(f"Error resolving URLs: {str(e)}")
        return []

def get_citations(response, resolved_urls):
    """Simple implementation to get citations"""
    try:
        if hasattr(response, 'candidates') and response.candidates:
            # Try to extract citations from response
            return [{
                "segments": [{
                    "value": "https://example.com/source",
                    "short_url": "[1]",
                    "title": "Example Source",
                    "snippet": "This is a placeholder source for testing."
                }]
            }]
        else:
            print("Warning: Response has no candidates, returning empty citations")
            return []
    except Exception as e:
        print(f"Error in get_citations: {str(e)}")
        return []

def insert_citation_markers(text, citations):
    """Simple implementation for citation markers"""
    try:
        if not text or not citations:
            return text

        # In a real implementation, we would insert citation markers
        # at the appropriate places in the text
        marked_text = text

        # Add a simple citation list at the end if there are citations
        if citations:
            marked_text += "\n\nSources:\n"
            for i, citation in enumerate(citations):
                for segment in citation.get("segments", []):
                    marked_text += f"[{i+1}] {segment.get('title', 'Unknown')} - {segment.get('value', 'No URL')}\n"

        return marked_text
    except Exception as e:
        print(f"Error inserting citation markers: {str(e)}")
        return text

load_dotenv()

# TODO: Re-enable when all LLM providers are available
# # Initialize LLM providers
# def initialize_llm_providers():
#     """Initialize and configure LLM providers"""
#     config_status = configure_llm_providers()
#     print(f"LLM Providers configured: {config_status['providers_configured']}")
#     if config_status['providers_failed']:
#         print(f"LLM Providers failed: {config_status['providers_failed']}")
#     return config_status
#
# # Initialize providers on module load
# llm_config_status = initialize_llm_providers()
#
# # Fallback check for Gemini API key
# if os.getenv("GEMINI_API_KEY") is None and not llm_config_status['providers_configured']:
#     raise ValueError("No LLM providers configured. Please set at least one API key (GEMINI_API_KEY or OPENAI_API_KEY)")

# Simple Gemini API key check
if os.getenv("GEMINI_API_KEY") is None:
    raise ValueError("GEMINI_API_KEY is required")

# Used for Google Search API
genai_client = Client(api_key=os.getenv("GEMINI_API_KEY")) if os.getenv("GEMINI_API_KEY") else None

# Nodes and graph definition will follow...

# Node for generating a simple chat response with intelligent context
async def simple_chat_response_node(state: OverallState, config: RunnableConfig) -> OverallState:
    try:
        configurable = Configuration.from_runnable_config(config)

        # Get API key with graceful fallback
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ GEMINI_API_KEY not set, using fallback response mechanism")
            messages = state.get("messages", [])
            last_message = messages[-1].content if messages else "Hello"
            fallback_content = f"I received your message: '{last_message}'. However, I'm currently in development mode without API access. Please set the GEMINI_API_KEY environment variable for full functionality."
            return {"messages": messages + [AIMessage(content=fallback_content)]}

        # Create LLM client with proper error handling
        try:
            llm = ChatGoogleGenerativeAI(
                model=configurable.chat_model,
                temperature=0.7,
                max_retries=2,
                api_key=api_key,
                convert_system_message_to_human=True,
            )
        except Exception as llm_init_error:
            print(f"⚠️ Failed to initialize Google Generative AI: {str(llm_init_error)}")
            messages = state.get("messages", [])
            return {"messages": messages + [AIMessage(content="Sorry, I'm having trouble connecting to my AI services. Please try again later.")]}

        # Get messages with validation
        messages = state.get("messages", [])
        if not messages:
            # Handle empty messages case with intelligent greeting
            try:
                intelligent_greeting = await create_intelligent_system_message(
                    interaction_type="general_chat",
                    personality_type="proactive",
                    user_message="hola"
                )
                greeting_messages = [
                    {"role": "system", "content": intelligent_greeting},
                    {"role": "user", "content": "Hola"}
                ]
                response = llm.invoke(greeting_messages)
                return {"messages": [AIMessage(content=response.content)]}
            except Exception as e:
                print(f"⚠️ Error generating intelligent greeting: {e}")
                return {"messages": [AIMessage(content="¡Hola! Encantado de ayudarte. Dime, ¿en qué puedo serte útil hoy?")]}

        # Invoke the LLM with the last user message using intelligent context
        try:
            # Make sure we have a valid user message
            if not messages or not hasattr(messages[-1], 'content') or not messages[-1].content:
                return {"messages": messages + [AIMessage(content="I didn't receive a valid message to respond to.")]}

            user_message = messages[-1].content

            # Create intelligent system message based on current system context
            try:
                intelligent_system_message = await create_intelligent_system_message(
                    interaction_type="general_chat",
                    personality_type="proactive",
                    user_message=user_message
                )
            except Exception as context_error:
                print(f"⚠️ Error creating intelligent context, falling back to basic: {context_error}")
                # Fallback to basic system message
                intelligent_system_message = create_system_message(
                    interaction_type="general_chat",
                    personality_type="proactive"
                )

            # Create a messages list with intelligent system message and user message
            prompt_messages = [
                {"role": "system", "content": intelligent_system_message},
                {"role": "user", "content": user_message}
            ]

            # Invoke LLM with system message and user message
            response = llm.invoke(prompt_messages)

            # Validate response
            if response and hasattr(response, 'content') and response.content:
                content = response.content
            else:
                content = "I processed your request but couldn't generate a proper response."

            updated_messages = messages + [AIMessage(content=content)]

        except Exception as e:
            print(f"Error in simple_chat_response_node: {str(e)}")
            error_msg = "Sorry, I encountered an error trying to respond."

            # Provide more specific error messages for common failures
            error_str = str(e).lower()
            if "resource exhausted" in error_str or "429" in error_str:
                error_msg = "I'm currently experiencing high demand. Please try again in a moment."
            elif "invalid api key" in error_str or "authentication" in error_str:
                error_msg = "There's an issue with my API configuration. Please contact support."

            updated_messages = messages + [AIMessage(content=error_msg)]

        return {"messages": updated_messages}

    except Exception as outer_error:
        # Catch-all for any other errors in the node
        print(f"Critical error in simple_chat_response_node: {str(outer_error)}")
        messages = state.get("messages", [])
        return {"messages": messages + [AIMessage(content="I encountered an unexpected error. The system administrator has been notified.")]}

# Placeholder for reflect_on_results and generate_answer if not fully defined
def reflect_on_results(state: OverallState, config: RunnableConfig) -> ReflectionState:
    # Simplified reflection logic
    reflection_text = "Based on the gathered information, the initial assessment is positive."
    reflection = Reflection(reflection=reflection_text, grade="good")
    return {"reflection": reflection, "research_loop_count": state.get("research_loop_count", 0) + 1}

def generate_answer(state: OverallState, config: RunnableConfig) -> OverallState:
    # Simplified answer generation
    final_answer = "This is a summary of the research findings."
    if state.get("messages"):
        # Append to existing messages if they exist
        updated_messages = state["messages"] + [AIMessage(content=final_answer)]
    else:
        updated_messages = [AIMessage(content=final_answer)]
    return {"messages": updated_messages}

def should_continue(state: OverallState) -> str:
    # Simplified decision logic
    research_loop_count = state.get("research_loop_count", 0)
    if research_loop_count < 2: # Max 2 research loops
        return "reflect_on_results"
    return END

def get_agent_executor():
    # Define the graph
    workflow = StateGraph(OverallState)

    # Add nodes
    workflow.add_node("route_task", route_task)
    workflow.add_node("generate_query", generate_query)
    workflow.add_node("web_research", web_research)
    workflow.add_node("reflect_on_results", reflect_on_results)
    workflow.add_node("generate_answer", generate_answer) # This is the original research answer generator placeholder
    workflow.add_node("simple_chat_response", simple_chat_response_node) # New intelligent chat node

    # Define edges
    workflow.add_edge(START, "route_task")

    # Conditional routing based on task_type from route_task
    workflow.add_conditional_edges(
        "route_task",
        lambda x: x.get("task_classification", {}).get("task_type"),
        {
            "chat": "simple_chat_response",
            "research": "generate_query",
            # TODO: Add a fallback or error handling path if task_type is unexpected
        }
    )

    # Edges for the new chat flow
    workflow.add_edge("simple_chat_response", END)

    # Edges for the existing research flow
    workflow.add_conditional_edges(
        "generate_query",
        continue_to_web_research,
    )
    workflow.add_edge("web_research", "reflect_on_results")
    workflow.add_conditional_edges(
        "reflect_on_results",
        should_continue,
        {
            "reflect_on_results": "generate_query", # Loop back for more queries if needed
            END: "generate_answer" # Research flow ends with its specific answer generator
        }
    )
    workflow.add_edge("generate_answer", END)

    # Set the conditional entry point for web_research if continue_to_web_research directs to it
    # This is a bit conceptual as continue_to_web_research uses Send
    # For a simpler direct graph, if not using Send for dynamic spawning:
    # workflow.add_edge("generate_query", "web_research")
    # And then web_research would need to handle a list of queries or a single query

    # Compile the graph
    agent_executor = workflow.compile()
    return agent_executor



# Nodes
def route_task(state: OverallState, config: RunnableConfig) -> OverallState:
    """LangGraph node that routes tasks to appropriate agents based on content analysis.

    Simplified version that always routes to research for now.

    Args:
        state: Current graph state containing the user's messages
        config: Configuration for the runnable

    Returns:
        Dictionary with state update, including agent_type
    """
    # TODO: Re-enable when agent router is available
    # For now, always route to chat to test the chat flow
    return {
        "agent_type": "chat", # Retaining agent_type for now, can be refined
        "task_classification": {
            "task_type": "chat", # This will be used for routing
            "complexity": "low",
            "confidence": 0.9,
            "reasoning": "Default routing to chat node for testing"
        }
    }


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

    # Ensure GEMINI_API_KEY is loaded for ChatGoogleGenerativeAI
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY not set, required for generate_query node")
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
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
    try:
        # Configure
        configurable = Configuration.from_runnable_config(config)
        search_query = state["search_query"]

        print(f"Web research on query: {search_query}")

        # Safety check for search query
        if not isinstance(search_query, str):
            print(f"Warning: search_query is not a string: {type(search_query).__name__}")
            # Try to convert to string if possible
            search_query = str(search_query)

        formatted_prompt = web_searcher_instructions.format(
            current_date=get_current_date(),
            research_topic=search_query,
        )

        # Safely use the google genai client
        try:
            if not genai_client:
                raise ValueError("Google Generative AI client is not initialized")

            response = genai_client.models.generate_content(
                model=configurable.query_generator_model,
                contents=formatted_prompt,
                config={
                    "tools": [{"google_search": {}}],
                    "temperature": 0.7,  # Increased temperature for more diverse and creative responses
                },
            )

            # Add safety checks for response content
            if not hasattr(response, 'candidates') or not response.candidates:
                print("Warning: Response doesn't have candidates")
                modified_text = "No research results available."
                sources_gathered = []
            else:
                # Try to safely resolve URLs and get citations
                try:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'grounding_metadata') and hasattr(candidate.grounding_metadata, 'grounding_chunks'):
                        resolved_urls = resolve_urls(candidate.grounding_metadata.grounding_chunks, state["id"])
                    else:
                        print("Warning: Response structure doesn't include grounding_chunks")
                        resolved_urls = []

                    citations = get_citations(response, resolved_urls)
                    modified_text = insert_citation_markers(response.text, citations) if hasattr(response, 'text') else "No text in response."
                    sources_gathered = [item for citation in citations for item in citation["segments"]]
                except Exception as citation_error:
                    print(f"Error processing citations: {str(citation_error)}")
                    modified_text = response.text if hasattr(response, 'text') else "Error processing response text."
                    sources_gathered = []
        except Exception as api_error:
            print(f"Google API error: {str(api_error)}")
            modified_text = f"Error performing web search: {str(api_error)}"
            sources_gathered = []

        # Return results
        return {
            "sources_gathered": sources_gathered,
            "search_query": [search_query],
            "web_research_result": [modified_text],
        }
    except Exception as e:
        print(f"Web research failed: {str(e)}")
        # Return fallback results
        return {
            "sources_gathered": [],
            "search_query": [state.get("search_query", "unknown query")],
            "web_research_result": [f"Error in web research: {str(e)}"],
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
    # Increment the research loop count and get the reasoning model
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    # Ensure GEMINI_API_KEY is loaded for ChatGoogleGenerativeAI
    if not os.getenv("GEMINI_API_KEY"):
        raise ValueError("GEMINI_API_KEY not set, required for web_search node")
    llm = ChatGoogleGenerativeAI(
        model=configurable.web_search_model,
        temperature=0.7,  # Increased temperature for more diverse and creative responses
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
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


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("route_task", route_task)
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)

def finalize_answer(state: OverallState, config: RunnableConfig):
    """Alias wrapper to maintain backward compatibility."""
    return generate_answer(state, config)

builder.add_node("finalize_answer", finalize_answer)
builder.add_node("generate_answer", generate_answer)
builder.add_node("simple_chat_response", simple_chat_response_node)  # Intelligent chat node

# Set the entrypoint as `route_task`
# This means that this node is the first one called
builder.add_edge(START, "route_task")
# Route based on agent_type: chat vs research
builder.add_conditional_edges(
    "route_task",
    lambda state, config: "simple_chat_response" if state.get("agent_type")=="chat" else "generate_query",
    ["simple_chat_response", "generate_query"],
)
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
# Chat node ends immediately
builder.add_edge("simple_chat_response", END)

graph = builder.compile(name="pro-search-agent")
