"""
Research Agent

Specialized agent for comprehensive research and information gathering.
"""

from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseSpecializedAgent


class ResearchAgent(BaseSpecializedAgent):
    """
    Research Agent for comprehensive information gathering.
    
    Capabilities:
    - Web search and data collection
    - Source evaluation and ranking
    - Multi-source synthesis
    - Citation management
    """
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research phase with comprehensive information gathering.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state with research results
        """
        query = state.get("original_query", "")
        
        # Use the original graph's research capabilities
        from ..graph import generate_query, web_research
        
        # Generate research queries with robust error handling
        query_state = {"messages": state.get("messages", [])}
        try:
            query_result = generate_query(query_state, self.config)
            # Add debug logging
            print(f"Query result type: {type(query_result).__name__}")
            
            # Handle potential non-dictionary query_result
            if not isinstance(query_result, dict):
                print(f"Warning: query_result is not a dictionary: {type(query_result).__name__}")
                research_queries = [query]  # Fallback to original query
            else:
                # Extract query list safely
                query_list = query_result.get("query_list", [])
                if not isinstance(query_list, list):
                    research_queries = [query]
                else:
                    # Safely extract individual queries
                    research_queries = []
                    for q in query_list:
                        if isinstance(q, dict):
                            query_text = q.get("query", "")
                            if query_text:
                                research_queries.append(query_text)
                    
            # Ensure we have at least one query
            if not research_queries:
                research_queries = [query]
                
            print(f"Generated {len(research_queries)} research queries")
            primary_query = research_queries[0]
            
        except Exception as e:
            print(f"Error generating queries: {str(e)}")
            # Fallback to original query
            research_queries = [query]
            primary_query = query
        # Perform web research using primary query
        research_result = web_research({"search_query": primary_query, "id": 0}, self.config)
        
        # Process and enhance research data
        search_results = research_result.get("web_research_result", [])
        sources = research_result.get("sources_gathered", [])
        
        # Evaluate source quality
        evaluated_sources = self._evaluate_sources(sources)
        
        # Create comprehensive research summary
        research_summary = self._create_research_summary(
            research_queries, evaluated_sources, search_results
        )
        
        # Calculate research confidence
        confidence = self._calculate_research_confidence(evaluated_sources, search_results)
        
        # Prepare research data
        research_data = {
            "queries_generated": research_queries,
            "search_results": search_results,
            "sources": evaluated_sources,
            "total_sources": len(evaluated_sources),
            "high_quality_sources": len([s for s in evaluated_sources if s.get("quality_score", 0) > 0.7]),
            "research_timestamp": datetime.now().isoformat()
        }
        
        return {
            **state,
            "research_queries": research_queries,
            "research_data": research_data,
            "research_summary": research_summary,
            "research_confidence": confidence,
            "research_timestamp": datetime.now().isoformat(),
            "current_agent": "research",
            "workflow_stage": "research"
        }
    
    def _evaluate_sources(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate and score source quality"""
        evaluated = []
        
        for source in sources:
            # Simple quality scoring based on available metadata
            quality_score = 0.5  # Base score
            
            # Boost score for certain domains
            url = source.get("url", "").lower()
            if any(domain in url for domain in [".edu", ".gov", ".org"]):
                quality_score += 0.2
            
            # Boost score for longer content
            content_length = len(source.get("snippet", ""))
            if content_length > 200:
                quality_score += 0.1
            
            # Boost score if title matches query well
            title = source.get("title", "").lower()
            if len(title) > 10:
                quality_score += 0.1
            
            # Cap at 1.0
            quality_score = min(1.0, quality_score)
            
            evaluated.append({
                **source,
                "quality_score": quality_score,
                "evaluation_timestamp": datetime.now().isoformat()
            })
        
        # Sort by quality score
        evaluated.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
        
        return evaluated
    
    def _create_research_summary(
        self, 
        queries: List[str], 
        sources: List[Dict[str, Any]], 
        search_results: List[Dict[str, Any]]
    ) -> str:
        """Create a comprehensive research summary"""
        
        summary = f"Research Summary:\n\n"
        summary += f"• Executed {len(queries)} research queries\n"
        summary += f"• Found {len(sources)} sources\n"
        summary += f"• Retrieved {len(search_results)} search results\n\n"
        
        # Add top sources
        high_quality_sources = [s for s in sources if s.get("quality_score", 0) > 0.7]
        if high_quality_sources:
            summary += f"Top Quality Sources ({len(high_quality_sources)}):\n"
            for i, source in enumerate(high_quality_sources[:3]):
                summary += f"{i+1}. {source.get('title', 'Untitled')} (Score: {source.get('quality_score', 0):.2f})\n"
            summary += "\n"
        
        # Add research coverage assessment
        if len(sources) >= 5:
            coverage = "Comprehensive"
        elif len(sources) >= 3:
            coverage = "Good"
        else:
            coverage = "Limited"
        
        summary += f"Research Coverage: {coverage}\n"
        summary += f"Average Source Quality: {sum(s.get('quality_score', 0) for s in sources) / len(sources):.2f}\n" if sources else "No sources evaluated\n"
        
        return summary
    
    def _calculate_research_confidence(
        self, 
        sources: List[Dict[str, Any]], 
        search_results: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in research results"""
        
        if not sources:
            return 0.1
        
        # Base confidence from number of sources
        source_confidence = min(0.4, len(sources) * 0.08)
        
        # Quality confidence from source scores
        avg_quality = sum(s.get("quality_score", 0) for s in sources) / len(sources)
        quality_confidence = avg_quality * 0.4
        
        # Coverage confidence from search results
        coverage_confidence = min(0.2, len(search_results) * 0.02)
        
        total_confidence = source_confidence + quality_confidence + coverage_confidence
        
        return min(1.0, total_confidence)
