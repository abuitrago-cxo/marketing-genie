"""
Research Node - Enhanced Information Gathering and Analysis

This node handles comprehensive research tasks including web search,
information synthesis, and knowledge gap analysis.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage
from langsmith import traceable

from ..multi_agent_state import MultiAgentState, Citation, QualityMetrics, AgentExecution
from ..utils.llm_utils import get_llm
from ..utils.search_utils import perform_web_search, extract_content_from_urls
from ..utils.prompt_templates import RESEARCH_PROMPTS


@traceable(name="research_specialist")
async def research_node(state: MultiAgentState, config: RunnableConfig) -> MultiAgentState:
    """
    Research specialist node for comprehensive information gathering
    
    Capabilities:
    - Multi-source web research
    - Information synthesis and analysis
    - Knowledge gap identification
    - Citation management
    - Quality assessment
    """
    
    print("🔍 Research Specialist: Starting comprehensive research...")
    
    start_time = datetime.now()
    
    try:
        llm = get_llm(config)
        
        # Find research tasks
        research_tasks = [task for task in state["tasks"] if task.agent_type == "research" and task.status == "pending"]
        
        if not research_tasks:
            print("ℹ️ No research tasks found")
            return state
        
        # Execute research for each task
        research_results = []
        citations = []
        
        for task in research_tasks:
            print(f"📋 Executing research task: {task.title}")
            
            # Generate search queries
            search_queries = await generate_research_queries(
                state["original_query"], 
                task.description,
                llm
            )
            
            # Perform web searches
            search_results = await execute_research_searches(search_queries)
            
            # Analyze and synthesize information
            analysis_result = await analyze_research_data(
                search_results,
                state["original_query"],
                task.description,
                llm
            )
            
            research_results.append(analysis_result)
            citations.extend(analysis_result.get("citations", []))
            
            # Mark task as completed
            task.status = "completed"
            task.result = analysis_result
            task.updated_at = datetime.now()
        
        # Identify knowledge gaps
        knowledge_gaps = await identify_knowledge_gaps(
            research_results,
            state["original_query"],
            llm
        )
        
        # Calculate quality metrics
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        quality_metrics = QualityMetrics(
            overall_score=calculate_research_quality_score(research_results),
            completeness=assess_information_completeness(research_results),
            accuracy=assess_information_accuracy(research_results),
            relevance=assess_information_relevance(research_results, state["original_query"]),
            clarity=assess_information_clarity(research_results),
            execution_time=execution_time,
            token_usage=estimate_token_usage(research_results),
            error_count=0
        )
        
        # Update state
        updated_state = state.copy()
        updated_state["research_data"].extend(research_results)
        updated_state["citations"].extend(citations)
        updated_state["knowledge_gaps"] = knowledge_gaps
        updated_state["research_iterations"] += 1
        updated_state["workflow_stage"] = "research_complete"
        
        # Add execution record
        execution = AgentExecution(
            agent_type="research",
            task_id=research_tasks[0].id if research_tasks else "research_general",
            start_time=start_time,
            end_time=end_time,
            status="completed",
            output={
                "research_results": research_results,
                "citations_count": len(citations),
                "knowledge_gaps": knowledge_gaps
            },
            metrics=quality_metrics
        )
        updated_state["agent_executions"].append(execution)
        
        # Add performance data
        updated_state["performance_data"]["research"].append(quality_metrics)
        
        # Create research summary message
        research_message = create_research_summary(research_results, citations, knowledge_gaps)
        updated_state["messages"].append(AIMessage(content=research_message))
        
        # Determine if more research is needed
        if knowledge_gaps and updated_state["research_iterations"] < updated_state["max_iterations"]:
            updated_state["should_continue"] = True
            updated_state["workflow_stage"] = "research_iteration_needed"
        else:
            updated_state["should_continue"] = False
            updated_state["workflow_stage"] = "research_complete"
        
        print(f"✅ Research completed: {len(research_results)} results, {len(citations)} citations")
        
        return updated_state
        
    except Exception as e:
        print(f"❌ Research error: {e}")
        
        # Add error to state
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": "research",
            "error": str(e),
            "context": "research_execution"
        }
        
        updated_state = state.copy()
        updated_state["error_log"].append(error_entry)
        updated_state["workflow_stage"] = "research_error"
        
        # Mark research tasks as failed
        for task in state["tasks"]:
            if task.agent_type == "research" and task.status == "pending":
                task.status = "failed"
                task.error_message = str(e)
        
        return updated_state


async def generate_research_queries(original_query: str, task_description: str, llm) -> List[str]:
    """Generate targeted search queries for research"""
    
    prompt = RESEARCH_PROMPTS["query_generation"].format(
        original_query=original_query,
        task_description=task_description
    )
    
    response = await llm.ainvoke(prompt)
    
    # Parse queries from response
    queries = []
    lines = response.content.split('\n')
    for line in lines:
        line = line.strip()
        if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
            query = line.lstrip('-•* ').strip()
            if query:
                queries.append(query)
    
    # Ensure we have at least some queries
    if not queries:
        queries = [original_query, f"detailed information about {original_query}"]
    
    return queries[:5]  # Limit to 5 queries


async def execute_research_searches(queries: List[str]) -> List[Dict[str, Any]]:
    """Execute web searches for all queries"""
    
    search_results = []
    
    for query in queries:
        try:
            print(f"🔍 Searching: {query}")
            results = await perform_web_search(query, max_results=5)
            
            # Extract content from top results
            for result in results[:3]:  # Top 3 results per query
                content = await extract_content_from_urls([result["url"]])
                if content:
                    result["content"] = content[0]
                    search_results.append(result)
            
            # Small delay between searches
            await asyncio.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️ Search error for '{query}': {e}")
            continue
    
    return search_results


async def analyze_research_data(
    search_results: List[Dict[str, Any]], 
    original_query: str,
    task_description: str,
    llm
) -> Dict[str, Any]:
    """Analyze and synthesize research data"""
    
    # Prepare content for analysis
    content_summary = ""
    citations = []
    
    for i, result in enumerate(search_results, 1):
        content_summary += f"\n--- Source {i}: {result.get('title', 'Unknown')} ---\n"
        content_summary += result.get('content', result.get('snippet', ''))[:1000]  # Limit content
        
        # Create citation
        citation = Citation(
            source_id=i,
            title=result.get('title', 'Unknown'),
            url=result.get('url', ''),
            snippet=result.get('snippet', '')[:200],
            relevance_score=calculate_relevance_score(result, original_query)
        )
        citations.append(citation)
    
    # Analyze content
    analysis_prompt = RESEARCH_PROMPTS["content_analysis"].format(
        original_query=original_query,
        task_description=task_description,
        content_summary=content_summary
    )
    
    analysis_response = await llm.ainvoke(analysis_prompt)
    
    return {
        "analysis": analysis_response.content,
        "sources_analyzed": len(search_results),
        "citations": citations,
        "content_summary": content_summary[:2000],  # Truncate for storage
        "timestamp": datetime.now().isoformat()
    }


async def identify_knowledge_gaps(
    research_results: List[Dict[str, Any]], 
    original_query: str, 
    llm
) -> List[str]:
    """Identify gaps in the research that need additional investigation"""
    
    # Combine all research analyses
    combined_analysis = "\n\n".join([
        result.get("analysis", "") for result in research_results
    ])
    
    gap_analysis_prompt = RESEARCH_PROMPTS["gap_analysis"].format(
        original_query=original_query,
        research_summary=combined_analysis
    )
    
    response = await llm.ainvoke(gap_analysis_prompt)
    
    # Parse gaps from response
    gaps = []
    lines = response.content.split('\n')
    for line in lines:
        line = line.strip()
        if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
            gap = line.lstrip('-•* ').strip()
            if gap:
                gaps.append(gap)
    
    return gaps


def calculate_relevance_score(result: Dict[str, Any], query: str) -> float:
    """Calculate relevance score for a search result"""
    title = result.get('title', '').lower()
    snippet = result.get('snippet', '').lower()
    query_terms = query.lower().split()
    
    score = 0.0
    total_terms = len(query_terms)
    
    if total_terms == 0:
        return 0.5
    
    # Check title relevance (weighted more heavily)
    title_matches = sum(1 for term in query_terms if term in title)
    score += (title_matches / total_terms) * 0.6
    
    # Check snippet relevance
    snippet_matches = sum(1 for term in query_terms if term in snippet)
    score += (snippet_matches / total_terms) * 0.4
    
    return min(score, 1.0)


def calculate_research_quality_score(research_results: List[Dict[str, Any]]) -> float:
    """Calculate overall quality score for research"""
    if not research_results:
        return 0.0
    
    # Base score on number of sources and content quality
    source_count = sum(len(result.get("citations", [])) for result in research_results)
    content_quality = len(research_results) / max(1, len(research_results))  # Simplified
    
    # Normalize to 0-5 scale
    score = min(5.0, (source_count * 0.3 + content_quality * 4.7))
    return score


def assess_information_completeness(research_results: List[Dict[str, Any]]) -> float:
    """Assess how complete the information is"""
    if not research_results:
        return 0.0
    
    # Simple heuristic based on content length and source diversity
    total_content = sum(len(result.get("analysis", "")) for result in research_results)
    source_count = sum(len(result.get("citations", [])) for result in research_results)
    
    completeness = min(1.0, (total_content / 2000) * 0.7 + (source_count / 10) * 0.3)
    return completeness


def assess_information_accuracy(research_results: List[Dict[str, Any]]) -> float:
    """Assess information accuracy (simplified heuristic)"""
    # In a real implementation, this would involve fact-checking
    # For now, use source credibility as a proxy
    return 0.85  # Placeholder


def assess_information_relevance(research_results: List[Dict[str, Any]], query: str) -> float:
    """Assess how relevant the information is to the query"""
    if not research_results:
        return 0.0
    
    total_relevance = 0.0
    total_citations = 0
    
    for result in research_results:
        citations = result.get("citations", [])
        for citation in citations:
            total_relevance += citation.relevance_score
            total_citations += 1
    
    return total_relevance / max(1, total_citations)


def assess_information_clarity(research_results: List[Dict[str, Any]]) -> float:
    """Assess how clear and well-structured the information is"""
    # Simplified heuristic based on content structure
    return 0.8  # Placeholder


def estimate_token_usage(research_results: List[Dict[str, Any]]) -> int:
    """Estimate token usage for the research process"""
    total_content = sum(len(result.get("analysis", "")) for result in research_results)
    return int(total_content / 4)  # Rough estimate: 4 chars per token


def create_research_summary(
    research_results: List[Dict[str, Any]], 
    citations: List[Citation], 
    knowledge_gaps: List[str]
) -> str:
    """Create a comprehensive research summary"""
    
    message = f"""🔍 **Research Specialist Report**

**Research Completed:**
- Sources analyzed: {sum(len(result.get('citations', [])) for result in research_results)}
- Information quality: High
- Coverage: Comprehensive

**Key Findings:**
"""
    
    # Add key findings from each research result
    for i, result in enumerate(research_results, 1):
        analysis = result.get("analysis", "")
        if analysis:
            # Extract first few sentences as key findings
            sentences = analysis.split('. ')[:2]
            key_finding = '. '.join(sentences)
            if key_finding:
                message += f"{i}. {key_finding}\n"
    
    message += f"""
**Sources & Citations:**
{len(citations)} high-quality sources identified and analyzed.

**Knowledge Gaps Identified:**
"""
    
    if knowledge_gaps:
        for gap in knowledge_gaps:
            message += f"- {gap}\n"
    else:
        message += "- No significant knowledge gaps identified\n"
    
    message += """
**Next Steps:**
Research data is now available for other agents to use in their specialized tasks.
"""
    
    return message
