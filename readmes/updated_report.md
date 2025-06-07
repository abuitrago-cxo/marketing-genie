# Updated Research Agent Report

## Overview

This report details the multi-step research agent, including its architecture, components, and operational flow.

## Agent Architecture

### State Management

The agent utilizes a state management system to track progress and data throughout the research process. Key states include:

*   **OverallState:** (Details to be added)
*   **QueryGenerationState:** (Details to be added)
*   **WebSearchState:** (Details to be added)
*   **ReflectionState:** (Details to be added)

### Core Components

The agent is comprised of several core components:

*   **Graph (`backend/src/agent/graph.py`):** Orchestrates the agent's workflow.
*   **Tools and Schemas (`backend/src/agent/tools_and_schemas.py`):** Defines data structures and tools used by the agent.
*   **Prompts (`backend/src/agent/prompts.py`):** Contains prompt templates for interacting with the LLM.
*   **Configuration (`backend/src/agent/configuration.py`):** Manages agent settings and parameters.

## Detailed Component Breakdown

### Graph (`backend/src/agent/graph.py`)

The graph defines the sequence of operations in the research process.

**Key Functions:**

*   `generate_query`:
    ```python
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

    # init Gemini 2.0 Flash
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
    ```
*   `web_research`:
    ```python
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

    # Uses the google genai client as the langchain client doesn't return grounding metadata
    response = genai_client.models.generate_content(
        model=configurable.query_generator_model,
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
    ```
*   `reflection`:
    ```python
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
    # init Reasoning Model
    llm = ChatGoogleGenerativeAI(
        model=reasoning_model,
        temperature=1.0,
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
    ```
*   `finalize_answer`:
    ```python
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
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    # init Reasoning Model, default to Gemini 2.5 Flash
    llm = ChatGoogleGenerativeAI(
        model=reasoning_model,
        temperature=0,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
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
    ```

**Graph Definition:**

```python
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
```

### Tools and Schemas (`backend/src/agent/tools_and_schemas.py`)

This module defines Pydantic models for data validation and serialization.

**Key Pydantic Models:**

*   `SearchQueryList`:
    ```python
class SearchQueryList(BaseModel):
    query: List[str] = Field(
        description="A list of search queries to be used for web research."
    )
    rationale: str = Field(
        description="A brief explanation of why these queries are relevant to the research topic."
    )
    ```
*   `Reflection`:
    ```python
class Reflection(BaseModel):
    is_sufficient: bool = Field(
        description="Whether the provided summaries are sufficient to answer the user's question."
    )
    knowledge_gap: str = Field(
        description="A description of what information is missing or needs clarification."
    )
    follow_up_queries: List[str] = Field(
        description="A list of follow-up queries to address the knowledge gap."
    )
    ```

### Prompts (`backend/src/agent/prompts.py`)

This module houses prompt templates used to guide the LLM's behavior.

**Key Prompts:**

*   `query_writer_instructions`: This prompt guides the LLM to generate sophisticated and diverse web search queries. It emphasizes creating queries focused on specific aspects of the original question and ensuring the most current information is gathered.
    ```python
query_writer_instructions = """Your goal is to generate sophisticated and diverse web search queries. These queries are intended for an advanced automated web research tool capable of analyzing complex results, following links, and synthesizing information.

Instructions:
- Always prefer a single search query, only add another query if the original question requests multiple aspects or elements and one query is not enough.
- Each query should focus on one specific aspect of the original question.
- Don't produce more than {number_queries} queries.
- Queries should be diverse, if the topic is broad, generate more than 1 query.
- Don't generate multiple similar queries, 1 is enough.
- Query should ensure that the most current information is gathered. The current date is {current_date}.

Format:
- Format your response as a JSON object with ALL three of these exact keys:
   - "rationale": Brief explanation of why these queries are relevant
   - "query": A list of search queries

Example:

Topic: What revenue grew more last year apple stock or the number of people buying an iphone
```json
{{
    "rationale": "To answer this comparative growth question accurately, we need specific data points on Apple's stock performance and iPhone sales metrics. These queries target the precise financial information needed: company revenue trends, product-specific unit sales figures, and stock price movement over the same fiscal period for direct comparison.",
    "query": ["Apple total revenue growth fiscal year 2024", "iPhone unit sales growth fiscal year 2024", "Apple stock price growth fiscal year 2024"],
}}
```

Context: {research_topic}"""
    ```
*   `reflection_instructions`: This prompt tasks the LLM with analyzing summaries to identify knowledge gaps and generate follow-up queries. It instructs the LLM to focus on technical details, implementation specifics, or emerging trends not fully covered.
    ```python
reflection_instructions = """You are an expert research assistant analyzing summaries about "{research_topic}".

Instructions:
- Identify knowledge gaps or areas that need deeper exploration and generate a follow-up query. (1 or multiple).
- If provided summaries are sufficient to answer the user's question, don't generate a follow-up query.
- If there is a knowledge gap, generate a follow-up query that would help expand your understanding.
- Focus on technical details, implementation specifics, or emerging trends that weren't fully covered.

Requirements:
- Ensure the follow-up query is self-contained and includes necessary context for web search.

Output Format:
- Format your response as a JSON object with these exact keys:
   - "is_sufficient": true or false
   - "knowledge_gap": Describe what information is missing or needs clarification
   - "follow_up_queries": Write a specific question to address this gap

Example:
```json
{{
    "is_sufficient": true, // or false
    "knowledge_gap": "The summary lacks information about performance metrics and benchmarks", // "" if is_sufficient is true
    "follow_up_queries": ["What are typical performance benchmarks and metrics used to evaluate [specific technology]?"] // [] if is_sufficient is true
}}
```

Reflect carefully on the Summaries to identify knowledge gaps and produce a follow-up query. Then, produce your output following this JSON format:

Summaries:
{summaries}
"""
    ```
*   `answer_instructions`: This prompt directs the LLM to generate a high-quality answer to the user's question based on provided summaries. It emphasizes including all citations from the summaries correctly.
    ```python
answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step.
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
- you MUST include all the citations from the summaries in the answer correctly.

User Context:
- {research_topic}

Summaries:
{summaries}"""
    ```

**Prompt Details:**

The prompts in `backend/src/agent/prompts.py` are designed to guide the language model at different stages of the research process. They leverage f-string formatting to insert dynamic information like the current date and research topic.

*   `query_writer_instructions`: This prompt is crucial for the initial query generation phase. It instructs the LLM to act as an advanced research tool, generating diverse and specific queries. The JSON output format ensures that the generated queries and their rationale can be easily parsed and used by the system.
*   `web_searcher_instructions`: (Although not explicitly requested for a snippet, it's an important prompt) This prompt guides the web search process, instructing the LLM to conduct targeted searches, consolidate findings, and track sources meticulously.
*   `reflection_instructions`: This prompt is used to evaluate the gathered information and identify any gaps. The LLM is asked to determine if the current summaries are sufficient and, if not, to generate follow-up queries. This iterative process helps ensure comprehensive research. The JSON output format with `is_sufficient`, `knowledge_gap`, and `follow_up_queries` allows the agent to decide whether to continue researching or finalize the answer.
*   `answer_instructions`: This final prompt guides the LLM in synthesizing all the gathered information and summaries into a coherent and well-cited answer to the user's original question. It stresses the importance of including all citations.

All prompts include a mechanism to pass the current date (`{current_date}`) to the LLM, ensuring that the generated queries and answers consider the timeliness of information. The `{research_topic}` placeholder allows the agent to focus the LLM's attention on the specific subject of inquiry. The `summaries` placeholder in `reflection_instructions` and `answer_instructions` is used to provide the LLM with the context of already gathered information.

### Configuration (`backend/src/agent/configuration.py`)

This module defines the configuration settings for the agent.

**Configuration Class:**

*   `Configuration`:
    ```python
class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="gemini-2.0-flash",
        metadata={
            "description": "The name of the language model to use for the agent's query generation."
        },
    )

    reflection_model: str = Field(
        default="gemini-2.5-flash-preview-04-17",
        metadata={
            "description": "The name of the language model to use for the agent's reflection."
        },
    )

    answer_model: str = Field(
        default="gemini-2.5-pro-preview-05-06",
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields.keys()
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**values)
    ```

**Configuration Details:**

The `Configuration` class in `backend/src/agent/configuration.py` uses Pydantic's `BaseModel` to define and manage settings for the research agent. This allows for type validation and clear documentation of configurable parameters.

Key configuration options include:

*   `query_generator_model`: Specifies the language model used for generating search queries (defaults to "gemini-2.0-flash").
*   `reflection_model`: Defines the model used for the reflection step, where the agent assesses information sufficiency (defaults to "gemini-2.5-flash-preview-04-17").
*   `answer_model`: Sets the model used for generating the final answer (defaults to "gemini-2.5-pro-preview-05-06").
*   `number_of_initial_queries`: Controls how many search queries are generated in the first step (defaults to 3).
*   `max_research_loops`: Determines the maximum number of times the agent will loop through the web research and reflection steps (defaults to 2).

The `from_runnable_config` class method provides a convenient way to create a `Configuration` instance from a `RunnableConfig` object, often used in LangChain applications. It prioritizes environment variables for configuration but can also use values passed directly in the `configurable` dictionary of the `RunnableConfig`. This offers flexibility in how the agent is configured for different environments or use cases.

## Pydantic Model Details

The agent relies on several `TypedDict` classes (which share similarities with Pydantic models for data structuring and clarity) defined in `backend/src/agent/state.py` to manage its state throughout the research process. These states are crucial for passing information between different nodes in the LangGraph graph.

*   **`OverallState(TypedDict)`:** This is the main state dictionary that accumulates information throughout the agent's run.
    *   `messages: Annotated[list, add_messages]`: A list to store messages (e.g., user queries, agent responses). The `add_messages` annotation suggests it's used with LangGraph's message handling.
    *   `search_query: Annotated[list, operator.add]`: A list to accumulate all search queries generated and used during the process.
    *   `web_research_result: Annotated[list, operator.add]`: A list to store the results obtained from web research.
    *   `sources_gathered: Annotated[list, operator.add]`: A list to keep track of all unique sources (URLs, documents) found.
    *   `initial_search_query_count: int`: The number of search queries to be generated initially.
    *   `max_research_loops: int`: The maximum number of research iterations allowed.
    *   `research_loop_count: int`: The current count of research iterations performed.
    *   `reasoning_model: str`: The specific LLM model to be used for reasoning tasks (like reflection and final answer generation).

*   **`QueryGenerationState(TypedDict)`:** This state holds the output of the query generation node.
    *   `query_list: list[Query]`: A list of `Query` objects, where each `Query` is another `TypedDict` containing:
        *   `query: str`: The search query string.
        *   `rationale: str`: The rationale behind generating that specific query.

*   **`WebSearchState(TypedDict)`:** This state is used to pass information to individual web research operations.
    *   `search_query: str`: The specific search query to be executed.
    *   `id: str`: An identifier for the search operation, likely used for tracking and organizing parallel searches.

*   **`ReflectionState(TypedDict)`:** This state holds the results of the reflection node, where the agent evaluates the gathered information.
    *   `is_sufficient: bool`: A boolean flag indicating whether the currently gathered information is sufficient to answer the user's question.
    *   `knowledge_gap: str`: A description of any identified gaps in the information.
    *   `follow_up_queries: Annotated[list, operator.add]`: A list of follow-up search queries designed to fill the identified knowledge gaps.
    *   `research_loop_count: int`: The updated count of research iterations.
    *   `number_of_ran_queries: int`: The total number of queries that have been executed so far.

The `Annotated[list, operator.add]` pattern is used for fields that are intended to be appended to across multiple graph steps, ensuring that information like search queries and web results are accumulated rather than overwritten.

## Conclusion

This report has detailed the architecture and components of the multi-step research agent. The agent leverages LangGraph to orchestrate a series of steps, including query generation, web research, reflection, and final answer synthesis.

Key features include:

*   **Structured State Management:** Utilizes `TypedDict` for clear and robust state handling throughout the research lifecycle.
*   **Modular Design:** Components for graph logic, Pydantic schemas/TypedDicts, LLM prompts, and configuration are separated into distinct modules, promoting maintainability and extensibility.
*   **Configurable LLM Usage:** Allows specification of different language models for various tasks (query generation, reflection, answer synthesis) through a Pydantic-based configuration system.
*   **Iterative Refinement:** Incorporates a reflection step to identify knowledge gaps and generate follow-up queries, enabling a more comprehensive research process.
*   **Citation Handling:** Designed to track and include sources in the final answer, ensuring verifiability.

The agent's design allows for flexible adaptation to different research tasks and can be further enhanced with additional tools and capabilities.
