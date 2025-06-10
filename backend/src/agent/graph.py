import os
import json
import re

from agent.tools_and_schemas import SearchQueryList, Reflection, DatabaseQueryResult
from agent.database_schema import get_full_schema_for_ai
from agent.database_tools import execute_database_query, format_query_result
from agent.vanna_doubao import create_hr_vanna
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
    DatabaseQueryState,
)
from agent.configuration import Configuration
from agent.prompts import (
    get_current_date,
    query_writer_instructions,
    database_query_instructions,
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

# 全局Vanna实例（懒加载）
_vanna_instance = None

def get_vanna_instance():
    """获取全局Vanna实例，实现懒加载"""
    global _vanna_instance
    if _vanna_instance is None:
        print("🚀 初始化Vanna实例...")
        _vanna_instance = create_hr_vanna()
        print("✅ Vanna实例创建完成")
    return _vanna_instance


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


def continue_to_database_query(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the database query node.

    This is used to spawn n number of database query nodes, one for each search query.
    """
    return [
        Send("database_query", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def database_query(state: DatabaseQueryState, config: RunnableConfig) -> OverallState:
    """
    LangGraph node that performs database queries using Vanna for intelligent SQL generation.
    使用Vanna进行智能SQL生成的数据库查询节点
    """
    configurable = Configuration.from_runnable_config(config)
    
    search_query = state["search_query"]
    search_id = state["id"]
    
    print(f"🗄️ [Vanna数据库查询] 开始处理查询: {search_query} (ID: {search_id})")
    
    try:
        # 步骤1: 获取Vanna实例
        vn = get_vanna_instance()
        
        # 步骤2: 使用Vanna生成SQL
        print(f"🧠 [Vanna-SQL生成] 正在为查询生成SQL: {search_query}")
        generated_sql = vn.generate_sql(search_query)
        
        print(f"✅ [Vanna-SQL生成] SQL生成成功:")
        print(f"   {generated_sql}")
        
        # 步骤3: 执行SQL查询
        print(f"⚡ [执行SQL] 正在执行Vanna生成的SQL...")
        db_result = execute_database_query(generated_sql)
        
        # 步骤4: 格式化查询结果
        formatted_result = format_query_result(generated_sql, db_result)
        
        # 步骤5: 创建数据源引用
        sources_gathered = [{
            "label": f"Vanna智能查询{search_id}",
            "short_url": f"vanna-query-{search_id}",
            "value": f"Vanna生成的SQL查询结果"
        }]
        
        # 步骤6: 构建综合结果报告
        comprehensive_result = f"""
**Vanna智能数据库查询报告 - 查询ID: {search_id}**

**原始需求:** {search_query}

**Vanna生成的SQL:**
```sql
{generated_sql}
```

**查询结果:**
{formatted_result}

**分析说明:** 
本查询使用Vanna AI自动生成SQL语句，基于对数据库结构和业务逻辑的深度理解，为您的查询需求"{search_query}"提供了精确的数据分析结果。
"""
        
        print(f"🎉 [Vanna查询完成] 智能数据库查询成功完成")
        
        return {
            "sources_gathered": sources_gathered,
            "search_query": [state["search_query"]],
            "web_research_result": [comprehensive_result],
        }
        
    except Exception as e:
        print(f"❌ [Vanna查询错误] 智能查询失败: {e}")
        
        # 如果Vanna失败，回退到原始方法
        print(f"🔄 [回退策略] 尝试使用豆包方法生成SQL...")
        
        try:
            # 获取数据库schema描述
            database_schema = get_full_schema_for_ai()
            
            # 格式化数据库查询提示
            current_date = get_current_date()
            formatted_prompt = database_query_instructions.format(
                database_schema=database_schema,
                current_date=current_date,
                query_requirement=search_query
            )
            
            # 使用快速模型生成SQL查询
            sql_result = call_doubao_model(
                model_name=configurable.web_research_model,
                messages=formatted_prompt,
                temperature=0.0,
                structured_output_schema=DatabaseQueryResult,
                timeout=configurable.regular_model_timeout
            )
            
            print(f"🔍 [豆包SQL生成] 成功生成 {len(sql_result.queries)} 个SQL查询")
            
            # 执行每个SQL查询并收集结果
            query_results = []
            sources_gathered = []
            
            for i, sql_query in enumerate(sql_result.queries):
                print(f"⚡ [执行SQL] 正在执行第 {i+1} 个查询...")
                
                # 执行真实数据库查询
                db_result = execute_database_query(sql_query.sql)
                
                # 格式化查询结果
                formatted_result = format_query_result(sql_query.sql, db_result)
                query_results.append(formatted_result)
                
                # 添加到sources中
                sources_gathered.append({
                    "label": f"豆包SQL查询{i+1}",
                    "short_url": f"fallback-sql-query-{search_id}-{i+1}",
                    "value": f"豆包SQL查询结果 - {sql_query.explanation}"
                })
            
            # 综合所有查询结果
            comprehensive_result = f"""
                **数据库查询分析报告 - 查询ID: {search_id}** (豆包方法)

                **原始需求:** {search_query}

                **查询概述:** {sql_result.summary}

                {''.join(query_results)}

                **说明:** 
                由于Vanna智能查询遇到问题，本次使用豆包方法生成SQL查询。错误信息：{str(e)}
                """
            
            print(f"📊 [回退成功] 豆包方法查询完成，共执行了 {len(sql_result.queries)} 个查询")

            return {
                "sources_gathered": sources_gathered,
                "search_query": [state["search_query"]],
                "web_research_result": [comprehensive_result],
            }
            
        except Exception as fallback_error:
            print(f"❌ [回退失败] 豆包方法也失败了: {fallback_error}")
            
            # 返回错误信息
            error_result = f"""
                **数据库查询错误 - 查询ID: {search_id}**

                **原始需求:** {search_query}

                **Vanna错误:** {str(e)}

                **豆包方法错误:** {str(fallback_error)}

                **建议:** 请检查查询语句的语法、数据库连接状态和Vanna配置。
                """
            
            return {
                "sources_gathered": [{
                    "label": f"查询错误{search_id}",
                    "short_url": f"error-{search_id}",
                    "value": "数据库查询执行失败"
                }],
                "search_query": [state["search_query"]],
                "web_research_result": [error_result],
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
                "database_query",
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
builder.add_node("database_query", database_query)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_database_query, ["database_query"]
)
# Reflect on the database query
builder.add_edge("database_query", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["database_query", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="database-search-agent")
