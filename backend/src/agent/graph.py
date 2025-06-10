import os
import json
import re

from agent.tools_and_schemas import SearchQueryList, Reflection
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.types import Send
from langgraph.graph import StateGraph
from langgraph.graph import START, END
from langchain_core.runnables import RunnableConfig
from volcenginesdkarkruntime import Ark

from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    web_searcher_instructions,
    reflection_instructions,
    answer_instructions,
)
from agent.utils import (
    get_citations,
    get_research_topic,
    insert_citation_markers,
    resolve_urls,
)

load_dotenv()

# 检查豆包API Key
if os.getenv("ARK_API_KEY") is None:
    raise ValueError("ARK_API_KEY is not set")


def create_ark_client(timeout: int = 300) -> Ark:
    """创建豆包客户端"""
    return Ark(
        api_key=os.getenv("ARK_API_KEY"),
        timeout=timeout,
    )


def call_doubao_model(model_name: str, messages: list, temperature: float = 0.0, 
                     structured_output_schema=None, timeout: int = 300):
    """
    调用豆包模型的通用函数
    
    Args:
        model_name: 模型名称
        messages: 消息列表
        temperature: 温度参数
        structured_output_schema: 结构化输出模式
        timeout: 超时时间
    """
    client = create_ark_client(timeout=timeout)
    
    # 格式化消息
    if isinstance(messages, str):
        formatted_messages = [{"role": "user", "content": messages}]
    else:
        formatted_messages = messages
    
    # 对于深度思考模型，添加思考提示
    if "thinking" in model_name and formatted_messages:
        # 确保有思考过程输出
        original_content = formatted_messages[-1]["content"]
        formatted_messages[-1]["content"] = (
            "任何输出都要有思考过程，输出内容必须以 \"<think>\\n\\n嗯\" 开头。"
            "仔细揣摩用户意图，在思考过程之后，提供逻辑清晰且内容完整的回答。\\n\\n"
            f"{original_content}"
        )
    
    # 打印AI调用信息
    print("=" * 80)
    print(f"🤖 [AI调用] 模型: {model_name}")
    print(f"🌡️  [AI调用] 温度: {temperature}")
    print(f"⏱️  [AI调用] 超时: {timeout}秒")
    print(f"📝 [AI调用] 发送消息:")
    for i, msg in enumerate(formatted_messages):
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        # 限制内容长度以便阅读
        display_content = content[:500] + "..." if len(content) > 500 else content
        print(f"   [{i+1}] {role.upper()}: {display_content}")
    print("-" * 80)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=formatted_messages,
            temperature=temperature,
        )
        
        # 打印AI响应信息
        ai_content = response.choices[0].message.content
        if ai_content is not None:
            print(f"✅ [AI响应] 成功接收响应")
            print(f"📊 [AI响应] 响应长度: {len(ai_content)} 字符")
            
            # 显示响应内容（限制长度）
            display_response = ai_content[:800] + "..." if len(ai_content) > 800 else ai_content
            print(f"💬 [AI响应] 内容:\n{display_response}")
        else:
            print(f"⚠️  [AI响应] 内容为空 (None)")
            ai_content = ""  # 设置默认值避免后续错误
        
        # 如果有思考过程，单独显示
        if hasattr(response.choices[0].message, 'reasoning_content'):
            reasoning = response.choices[0].message.reasoning_content
            if reasoning is not None:
                display_reasoning = reasoning[:500] + "..." if len(reasoning) > 500 else reasoning
                print(f"🧠 [AI思考] 推理过程:\n{display_reasoning}")
        
        print("=" * 80)
        
        # 处理结构化输出
        if structured_output_schema:
            content = response.choices[0].message.content
            # 提取思考内容（如果存在）
            reasoning_content = ""
            if hasattr(response.choices[0].message, 'reasoning_content'):
                reasoning_content = response.choices[0].message.reasoning_content
            
            # 尝试解析JSON
            try:
                # 如果内容包含思考过程，提取实际答案部分
                if content.startswith("<think>"):
                    # 找到思考过程结束的位置
                    think_end = content.find("</think>")
                    if think_end != -1:
                        content = content[think_end + 8:].strip()
                
                # 处理markdown代码块包装的JSON
                if "```json" in content:
                    # 提取JSON代码块中的内容
                    json_start = content.find("```json") + 7
                    json_end = content.find("```", json_start)
                    if json_end != -1:
                        json_content = content[json_start:json_end].strip()
                    else:
                        # 如果没有结束标记，取从```json开始的所有内容
                        json_content = content[json_start:].strip()
                elif "```" in content and "{" in content:
                    # 处理其他代码块格式
                    lines = content.split('\n')
                    json_lines = []
                    in_code_block = False
                    for line in lines:
                        if line.strip().startswith('```'):
                            in_code_block = not in_code_block
                            continue
                        if in_code_block or ('{' in line or '}' in line or '"' in line):
                            json_lines.append(line)
                    json_content = '\n'.join(json_lines).strip()
                else:
                    # 尝试从内容中提取JSON
                    json_start = content.find("{")
                    json_end = content.rfind("}") + 1
                    if json_start != -1 and json_end > json_start:
                        json_content = content[json_start:json_end]
                    else:
                        # 如果没找到JSON，尝试直接解析整个内容
                        json_content = content
                
                # 清理可能的尾随逗号
                json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
                
                print(f"🔧 [JSON解析] 提取的JSON: {json_content}")
                
                # 解析JSON
                parsed_data = json.loads(json_content)
                structured_result = structured_output_schema(**parsed_data)
                
                print(f"✅ [JSON解析] 成功解析为: {structured_result}")
                print("=" * 80)
                
                return structured_result
                
            except json.JSONDecodeError as e:
                # 如果JSON解析失败，返回错误信息
                print(f"❌ [JSON解析] 失败: {e}")
                print(f"❌ [JSON解析] 原始内容: {content}")
                print("=" * 80)
                raise ValueError(f"Invalid JSON response: {content}")
        
        return response
        
    except Exception as e:
        print(f"❌ [AI调用] 错误: {e}")
        print("=" * 80)
        raise


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

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    
    # 使用常规模型生成查询，注重速度
    result = call_doubao_model(
        model_name=configurable.query_generator_model,
        messages=formatted_prompt,
        temperature=1.0,
        structured_output_schema=SearchQueryList,
        timeout=configurable.regular_model_timeout
    )
    
    return_value = {"query_list": result.query}
    
    return return_value


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph node that performs web research using Google Search API."""
    configurable = Configuration.from_runnable_config(config)
    
    # 暂时返回固定的模拟搜索结果，确保代码能跑通
    search_query = state["search_query"]
    search_id = state["id"]
    
    # 创建固定的模拟搜索结果
    mock_search_result = f"""
    关于 "{search_query}" 的搜索结果：
    
    这是一个模拟的搜索结果。在实际应用中，这里应该调用真实的搜索API（如Google Search API）来获取最新的信息。
    
    当前搜索查询: {search_query}
    搜索ID: {search_id}
    
    主要发现:
    1. 相关信息点1
    2. 相关信息点2  
    3. 相关信息点3
    
    这个结果包含了与查询相关的基础信息，可以用于后续的分析和总结。
    """
    
    # 创建模拟的引用数据
    citations = [{
        "start_index": 0,
        "end_index": len(mock_search_result),
        "segments": [{
            "label": f"搜索结果 {search_id}",
            "short_url": f"https://example.com/search-{search_id}",
            "value": f"https://example.com/full-search-result-{search_id}"
        }]
    }]
    
    modified_text = insert_citation_markers(mock_search_result, citations)
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
    
    # 使用深度思考模型进行反思，注重推理质量
    result = call_doubao_model(
        model_name=configurable.reflection_model,
        messages=formatted_prompt,
        temperature=1.0,
        structured_output_schema=Reflection,
        timeout=configurable.thinking_model_timeout
    )

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

    # 使用深度思考模型生成最终答案，注重质量
    response = call_doubao_model(
        model_name=configurable.answer_model,
        messages=formatted_prompt,
        temperature=0.0,
        timeout=configurable.thinking_model_timeout
    )
    
    result_content = response.choices[0].message.content
    
    # 打印思考过程（如果存在）
    if hasattr(response.choices[0].message, 'reasoning_content'):
        print("=== 思考过程 ===")
        print(response.choices[0].message.reasoning_content)
        print("=== 思考结束 ===")

    # 处理引用替换
    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in result_content:
            result_content = result_content.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)

    return {
        "messages": [AIMessage(content=result_content)],
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
