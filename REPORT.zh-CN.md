# 更新的研究代理报告

## 概述

本报告详细介绍了多步骤研究代理，包括其体系结构、组件和操作流程。

## 代理体系结构

### 状态管理

该代理利用状态管理系统来跟踪整个研究过程中的进度和数据。关键状态包括：

*   **OverallState:** (待补充详细信息)
*   **QueryGenerationState:** (待补充详细信息)
*   **WebSearchState:** (待补充详细信息)
*   **ReflectionState:** (待补充详细信息)

### 核心组件

该代理由几个核心组件组成：

*   **图 (`backend/src/agent/graph.py`):** 协调代理的工作流程。
*   **工具和模式 (`backend/src/agent/tools_and_schemas.py`):** 定义代理使用的数据结构和工具。
*   **提示 (`backend/src/agent/prompts.py`):** 包含与 LLM 交互的提示模板。
*   **配置 (`backend/src/agent/configuration.py`):** 管理代理设置和参数。

## 详细组件分解

### 图 (`backend/src/agent/graph.py`)

该图定义了研究过程中的操作序列。

**关键函数：**

*   `generate_query`:
    ```python
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph 节点，根据用户的问题生成搜索查询。

    使用 Gemini 2.0 Flash 创建优化的搜索查询，用于根据用户的问题进行网络研究。

    参数：
        state：包含用户问题的当前图状态
        config：可运行程序的配置，包括 LLM 提供程序设置

    返回：
        包含状态更新的字典，其中包括包含生成的查询的 search_query 键
    """
    configurable = Configuration.from_runnable_config(config)

    # 检查自定义初始搜索查询计数
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    # 初始化 Gemini 2.0 Flash
    llm = ChatGoogleGenerativeAI(
        model=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    structured_llm = llm.with_structured_output(SearchQueryList)

    # 格式化提示
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    # 生成搜索查询
    result = structured_llm.invoke(formatted_prompt)
    return {"query_list": result.query}
    ```
*   `web_research`:
    ```python
def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph 节点，使用本机 Google 搜索 API 工具执行网络研究。

    结合使用本机 Google 搜索 API 工具和 Gemini 2.0 Flash 执行网络搜索。

    参数：
        state：包含搜索查询和研究循环计数的当前图状态
        config：可运行程序的配置，包括搜索 API 设置

    返回：
        包含状态更新的字典，其中包括 sources_gathered、research_loop_count 和 web_research_results
    """
    # 配置
    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )

    # 使用 google genai 客户端，因为 langchain 客户端不返回基础元数据
    response = genai_client.models.generate_content(
        model=configurable.query_generator_model,
        contents=formatted_prompt,
        config={
            "tools": [{"google_search": {}}],
            "temperature": 0,
        },
    )
    # 将 url 解析为短 url 以节省令牌和时间
    resolved_urls = resolve_urls(
        response.candidates[0].grounding_metadata.grounding_chunks, state["id"]
    )
    # 获取引文并将其添加到生成的文本中
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
    """LangGraph 节点，识别知识差距并生成潜在的后续查询。

    分析当前摘要以识别需要进一步研究的领域，并生成潜在的后续查询。使用结构化输出以 JSON 格式提取后续查询。

    参数：
        state：包含正在运行的摘要和研究主题的当前图状态
        config：可运行程序的配置，包括 LLM 提供程序设置

    返回：
        包含状态更新的字典，其中包括包含生成的后续查询的 search_query 键
    """
    configurable = Configuration.from_runnable_config(config)
    # 增加研究循环计数并获取推理模型
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # 格式化提示
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    # 初始化推理模型
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
    """LangGraph 节点，最终确定研究摘要。

    通过对来源进行重复数据删除和格式化来准备最终输出，然后将其与正在运行的摘要相结合，以创建结构良好且带有正确引文的研究报告。

    参数：
        state：包含正在运行的摘要和收集的来源的当前图状态

    返回：
        包含状态更新的字典，其中包括包含格式化的最终摘要和来源的 running_summary 键
    """
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.reasoning_model

    # 格式化提示
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    # 初始化推理模型，默认为 Gemini 2.5 Flash
    llm = ChatGoogleGenerativeAI(
        model=reasoning_model,
        temperature=0,
        max_retries=2,
        api_key=os.getenv("GEMINI_API_KEY"),
    )
    result = llm.invoke(formatted_prompt)

    # 将短 url 替换为原始 url，并将所有使用的 url 添加到 sources_gathered
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

**图定义：**

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


### 工具和模式 (`backend/src/agent/tools_and_schemas.py`)

该模块定义了用于数据验证和序列化的 Pydantic 模型。

**关键 Pydantic 模型：**

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


### 提示 (`backend/src/agent/prompts.py`)

该模块包含用于指导 LLM 行为的提示模板。

**关键提示：**

*   `query_writer_instructions`: 此提示指导 LLM 生成复杂且多样化的网络搜索查询。它强调创建专注于原始问题特定方面的查询，并确保收集最新的信息。
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
*   `reflection_instructions`: 此提示要求 LLM 分析摘要以识别知识差距并生成后续查询。它指示 LLM 专注于技术细节、实施细节或未完全涵盖的新兴趋势。
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
*   `answer_instructions`: 此提示指示 LLM 根据提供的摘要生成对用户问题的高质量回答。它强调正确包括摘要中的所有引文。
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

**提示详情：**

`backend/src/agent/prompts.py` 中的提示旨在指导语言模型在研究过程的不同阶段。它们利用 f 字符串格式插入动态信息，如当前日期和研究主题。

*   `query_writer_instructions`: 此提示对于初始查询生成阶段至关重要。它指示 LLM 充当高级研究工具，生成多样化和特定的查询。JSON 输出格式确保生成的查询及其基本原理可以轻松地被系统解析和使用。
*   `web_searcher_instructions`: (虽然没有明确要求提供代码片段，但它是一个重要的提示) 此提示指导网络搜索过程，指示 LLM 进行有针对性的搜索，整合发现结果，并仔细跟踪来源。
*   `reflection_instructions`: 此提示用于评估收集到的信息并识别任何差距。LLM 被要求确定当前摘要是否足够，如果不够，则生成后续查询。这种迭代过程有助于确保全面的研究。带有 `is_sufficient`、`knowledge_gap` 和 `follow_up_queries` 的 JSON 输出格式允许代理决定是继续研究还是最终确定答案。
*   `answer_instructions`: 此最终提示指导 LLM 将所有收集到的信息和摘要合成为对用户原始问题的连贯且引用充分的回答。它强调了包括所有引文的重要性。

所有提示都包含一个将当前日期 (`{current_date}`) 传递给 LLM 的机制，确保生成的查询和答案考虑到信息的及时性。`{research_topic}` 占位符允许代理将 LLM 的注意力集中在查询的具体主题上。`reflection_instructions` 和 `answer_instructions` 中的 `summaries` 占位符用于向 LLM 提供已收集信息的上下文。


### 配置 (`backend/src/agent/configuration.py`)

该模块定义代理的配置设置。

**配置类：**

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

**配置详情：**

`backend/src/agent/configuration.py` 中的 `Configuration` 类使用 Pydantic 的 `BaseModel` 来定义和管理研究代理的设置。这允许类型验证和清晰的可配置参数文档。

关键配置选项包括：

*   `query_generator_model`: 指定用于生成搜索查询的语言模型 (默认为 "gemini-2.0-flash")。
*   `reflection_model`: 定义用于反思步骤的模型，代理在该步骤中评估信息充分性 (默认为 "gemini-2.5-flash-preview-04-17")。
*   `answer_model`: 设置用于生成最终答案的模型 (默认为 "gemini-2.5-pro-preview-05-06")。
*   `number_of_initial_queries`: 控制第一步中生成的搜索查询数量 (默认为 3)。
*   `max_research_loops`: 确定代理将循环执行网络研究和反思步骤的最大次数 (默认为 2)。

`from_runnable_config` 类方法提供了一种从 `RunnableConfig` 对象创建 `Configuration` 实例的便捷方法，该对象通常用于 LangChain 应用程序中。它优先考虑环境变量进行配置，但也可以使用直接在 `RunnableConfig` 的 `configurable` 字典中传递的值。这为如何在不同环境或用例中配置代理提供了灵活性。


## Pydantic 模型详情

代理依赖于 `backend/src/agent/state.py` 中定义的几个 `TypedDict` 类 (它们在数据结构和清晰度方面与 Pydantic 模型有相似之处) 来管理其在整个研究过程中的状态。这些状态对于在 LangGraph 图中的不同节点之间传递信息至关重要。

*   **`OverallState(TypedDict)`:** 这是在代理运行期间累积信息的主要状态字典。
    *   `messages: Annotated[list, add_messages]`: 用于存储消息 (例如，用户查询、代理响应) 的列表。`add_messages` 注释表明它与 LangGraph 的消息处理一起使用。
    *   `search_query: Annotated[list, operator.add]`: 用于累积在此过程中生成和使用的所有搜索查询的列表。
    *   `web_research_result: Annotated[list, operator.add]`: 用于存储从网络研究中获得的结果的列表。
    *   `sources_gathered: Annotated[list, operator.add]`: 用于跟踪所有找到的唯一来源 (URL、文档) 的列表。
    *   `initial_search_query_count: int`: 最初要生成的搜索查询数。
    *   `max_research_loops: int`: 允许的最大研究迭代次数。
    *   `research_loop_count: int`: 当前执行的研究迭代次数。
    *   `reasoning_model: str`: 用于推理任务 (如反思和最终答案生成) 的特定 LLM 模型。

*   **`QueryGenerationState(TypedDict)`:** 此状态保存查询生成节点的输出。
    *   `query_list: list[Query]`: `Query` 对象的列表，其中每个 `Query` 是另一个包含以下内容的 `TypedDict`：
        *   `query: str`: 搜索查询字符串。
        *   `rationale: str`: 生成该特定查询的基本原理。

*   **`WebSearchState(TypedDict)`:** 此状态用于将信息传递给单个网络研究操作。
    *   `search_query: str`: 要执行的特定搜索查询。
    *   `id: str`: 搜索操作的标识符，可能用于跟踪和组织并行搜索。

*   **`ReflectionState(TypedDict)`:** 此状态保存反思节点的结果，代理在该节点评估收集到的信息。
    *   `is_sufficient: bool`: 一个布尔标志，指示当前收集到的信息是否足以回答用户的问题。
    *   `knowledge_gap: str`: 对信息中任何已识别差距的描述。
    *   `follow_up_queries: Annotated[list, operator.add]`: 为填补已识别知识差距而设计的后续搜索查询列表。
    *   `research_loop_count: int`: 更新的研究迭代次数。
    *   `number_of_ran_queries: int`: 到目前为止已执行的查询总数。

`Annotated[list, operator.add]` 模式用于旨在跨多个图形步骤附加的字段，确保诸如搜索查询和网络结果之类的信息被累积而不是被覆盖。


## 结论

本报告详细介绍了多步骤研究代理的体系结构和组件。该代理利用 LangGraph 来协调一系列步骤，包括查询生成、网络研究、反思和最终答案综合。

主要特点包括：

*   **结构化状态管理：** 在整个研究生命周期中使用 `TypedDict` 进行清晰且健壮的状态处理。
*   **模块化设计：** 图逻辑、Pydantic 模式/TypedDict、LLM 提示和配置等组件被分离到不同的模块中，从而提高了可维护性和可扩展性。
*   **可配置的 LLM 用法：** 允许通过基于 Pydantic 的配置系统为各种任务 (查询生成、反思、答案综合) 指定不同的语言模型。
*   **迭代优化：** 包含一个反思步骤来识别知识差距并生成后续查询，从而实现更全面的研究过程。
*   **引文处理：** 设计用于跟踪并在最终答案中包含来源，确保可验证性。

该代理的设计允许灵活适应不同的研究任务，并且可以通过其他工具和功能进一步增强。