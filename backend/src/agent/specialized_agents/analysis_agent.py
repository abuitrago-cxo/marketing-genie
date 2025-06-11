"""
Analysis Agent

Specialized agent for research analysis and knowledge gap identification.
"""

from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseSpecializedAgent


class AnalysisAgent(BaseSpecializedAgent):
    """
    Analysis Agent for research evaluation and gap identification.
    
    Capabilities:
    - Research quality assessment
    - Knowledge gap identification
    - Follow-up query generation
    - Research continuation decisions
    """
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute analysis phase with research evaluation.
        
        Args:
            state: Current workflow state with research data
            
        Returns:
            Updated state with analysis results
        """
        try:
            print(f"AnalysisAgent executing with state: {type(state).__name__}")
            
            # Validate state is a dictionary
            if not isinstance(state, dict):
                print(f"Warning: Analysis agent received non-dict state of type {type(state).__name__}")
                # Create a minimal valid state
                state = {"original_query": "Unknown query", "messages": []}
                
            # Get research data with validation
            research_data = state.get("research_data", {})
            if not isinstance(research_data, dict):
                print(f"Warning: research_data is not a dictionary: {type(research_data).__name__}")
                research_data = {"search_results": [], "sources": []}
                
            research_summary = state.get("research_summary", "")
            original_query = state.get("original_query", "")
            
            print(f"Original query: {original_query}")
            print(f"Research data keys: {research_data.keys() if isinstance(research_data, dict) else 'None'}")
            
            # Use the original graph's reflection capabilities
            from ..graph import reflection
            
            # Prepare state for reflection with validation
            messages = state.get("messages", [])
            search_results = []
            if isinstance(research_data, dict) and "search_results" in research_data:
                search_results = research_data["search_results"]
                if not isinstance(search_results, list):
                    print(f"Warning: search_results is not a list: {type(search_results).__name__}")
                    search_results = []
                    
            reflection_state = {
                "messages": messages,
                "search_results": search_results
            }
            
            # Perform reflection/analysis with error handling
            try:
                reflection_result = reflection(reflection_state, self.config)
                print(f"Reflection result type: {type(reflection_result).__name__}")
                
                # Handle case where reflection_result is not a dictionary
                if not isinstance(reflection_result, dict):
                    print(f"Warning: reflection_result is not a dictionary: {type(reflection_result).__name__}")
                    reflection_result = {
                        "reflection": "Analysis could not be completed due to data format issues.",
                        "is_sufficient": False,
                        "knowledge_gap": "Unknown",
                        "follow_up_queries": []
                    }
            except Exception as reflection_error:
                print(f"Error in reflection step: {str(reflection_error)}")
                reflection_result = {
                    "reflection": f"Error during analysis: {str(reflection_error)}",
                    "is_sufficient": False,
                    "knowledge_gap": "Error occurred during analysis",
                    "follow_up_queries": []
                }
        
            # Analyze research quality with error handling
            try:
                quality_assessment = self._assess_research_quality(research_data, reflection_result)
            except Exception as e:
                print(f"Error assessing research quality: {str(e)}")
                quality_assessment = {
                    "overall_quality": "unknown",
                    "source_quality": "unknown",
                    "coverage": "unknown"
                }
            
            # Identify knowledge gaps with error handling
            try:
                knowledge_gaps = self._identify_knowledge_gaps(
                    original_query, research_data, reflection_result
                )
            except Exception as e:
                print(f"Error identifying knowledge gaps: {str(e)}")
                knowledge_gaps = ["Unable to identify knowledge gaps due to processing error"]
            
            # Generate follow-up queries if needed with error handling
            try:
                follow_up_queries = self._generate_follow_up_queries(knowledge_gaps, original_query)
            except Exception as e:
                print(f"Error generating follow-up queries: {str(e)}")
                follow_up_queries = []
            
            # Decide if research should continue with error handling
            try:
                should_continue = self._should_continue_research(
                    state, quality_assessment, knowledge_gaps
                )
            except Exception as e:
                print(f"Error determining if research should continue: {str(e)}")
                should_continue = False
            
            # Calculate analysis confidence with error handling
            try:
                confidence = self._calculate_analysis_confidence(
                    quality_assessment, knowledge_gaps, research_data
                )
            except Exception as e:
                print(f"Error calculating analysis confidence: {str(e)}")
                confidence = 0.5  # Default medium confidence
        
            # Prepare analysis data with validation
            analysis_data = {
                "quality_assessment": quality_assessment,
                "knowledge_gaps_identified": len(knowledge_gaps),
                "follow_up_queries_generated": len(follow_up_queries),
                "research_continuation_recommended": should_continue,
                "reflection_summary": reflection_result.get("reflection", "") if isinstance(reflection_result, dict) else str(reflection_result),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            print(f"Analysis completed successfully, returning results")
            return {
                **state,
                "analysis_data": analysis_data,
                "knowledge_gaps": knowledge_gaps,
                "follow_up_queries": follow_up_queries,
                "should_continue_research": should_continue,
                "analysis_confidence": confidence,
                "analysis_timestamp": datetime.now().isoformat(),
                "current_agent": "analysis",
                "workflow_stage": "analysis"
            }
            
        except Exception as e:
            print(f"Critical error in AnalysisAgent.execute: {str(e)}")
            # Return a minimal valid state with error information
            return {
                **state,
                "analysis_data": {
                    "error": str(e),
                    "analysis_timestamp": datetime.now().isoformat()
                },
                "knowledge_gaps": ["Error occurred during analysis"],
                "follow_up_queries": [],
                "should_continue_research": False,
                "analysis_confidence": 0.1,
                "analysis_timestamp": datetime.now().isoformat(),
                "current_agent": "analysis",
                "workflow_stage": "analysis",
                "error": f"Analysis failed: {str(e)}"
            }
    
    def _assess_research_quality(
        self, 
        research_data: Dict[str, Any], 
        reflection_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess the quality of research results"""
        
        sources = research_data.get("sources", [])
        search_results = research_data.get("search_results", [])
        
        # Source quality metrics
        total_sources = len(sources)
        high_quality_sources = len([s for s in sources if s.get("quality_score", 0) > 0.7])
        avg_source_quality = sum(s.get("quality_score", 0) for s in sources) / total_sources if total_sources > 0 else 0
        
        # Coverage metrics
        total_results = len(search_results)
        
        # Determine overall quality level
        if avg_source_quality > 0.8 and high_quality_sources >= 3:
            quality_level = "excellent"
        elif avg_source_quality > 0.6 and total_sources >= 3:
            quality_level = "good"
        elif avg_source_quality > 0.4 and total_sources >= 2:
            quality_level = "fair"
        else:
            quality_level = "poor"
        
        # Extract search quality from reflection if available
        search_quality = reflection_result.get("search_quality", quality_level)
        
        return {
            "overall_quality": quality_level,
            "search_quality": search_quality,
            "source_metrics": {
                "total_sources": total_sources,
                "high_quality_sources": high_quality_sources,
                "average_quality": avg_source_quality
            },
            "coverage_metrics": {
                "total_results": total_results,
                "results_per_query": total_results / max(1, len(research_data.get("queries_generated", [])))
            }
        }
    
    def _identify_knowledge_gaps(
        self, 
        original_query: str, 
        research_data: Dict[str, Any], 
        reflection_result: Dict[str, Any]
    ) -> List[str]:
        """Identify gaps in current research"""
        
        gaps = []
        
        # Extract gaps from reflection if available
        reflection_gaps = reflection_result.get("information_gaps", [])
        gaps.extend(reflection_gaps)
        
        # Analyze query coverage
        query_terms = original_query.lower().split()
        sources = research_data.get("sources", [])
        
        # Check if key terms are covered
        covered_terms = set()
        for source in sources:
            title = source.get("title", "").lower()
            snippet = source.get("snippet", "").lower()
            content = title + " " + snippet
            
            for term in query_terms:
                if term in content and len(term) > 3:  # Skip short words
                    covered_terms.add(term)
        
        # Identify uncovered terms
        uncovered_terms = [term for term in query_terms if term not in covered_terms and len(term) > 3]
        
        if uncovered_terms:
            gaps.append(f"Limited coverage of: {', '.join(uncovered_terms)}")
        
        # Check source diversity
        domains = set()
        for source in sources:
            url = source.get("url", "")
            if url:
                domain = url.split("//")[-1].split("/")[0]
                domains.add(domain)
        
        if len(domains) < 3 and len(sources) > 3:
            gaps.append("Limited source diversity - most results from similar domains")
        
        # Check recency (if timestamps available)
        recent_sources = 0
        for source in sources:
            # This would need actual date parsing in production
            # For now, assume all sources are reasonably recent
            recent_sources += 1
        
        if recent_sources < len(sources) * 0.5:
            gaps.append("Limited recent information - most sources may be outdated")
        
        return gaps[:5]  # Limit to top 5 gaps
    
    def _generate_follow_up_queries(
        self, 
        knowledge_gaps: List[str], 
        original_query: str
    ) -> List[str]:
        """Generate follow-up queries to address knowledge gaps"""
        
        follow_up_queries = []
        
        for gap in knowledge_gaps[:3]:  # Limit to 3 follow-ups
            if "coverage of:" in gap:
                # Extract uncovered terms
                terms = gap.split("coverage of:")[-1].strip()
                follow_up_queries.append(f"{original_query} {terms}")
            elif "diversity" in gap:
                # Add more specific search terms
                follow_up_queries.append(f"{original_query} latest research")
                follow_up_queries.append(f"{original_query} expert opinion")
            elif "recent" in gap:
                # Focus on recent information
                follow_up_queries.append(f"{original_query} 2024 latest")
            else:
                # Generic follow-up
                follow_up_queries.append(f"{original_query} additional information")
        
        return follow_up_queries
    
    def _should_continue_research(
        self, 
        state: Dict[str, Any], 
        quality_assessment: Dict[str, Any], 
        knowledge_gaps: List[str]
    ) -> bool:
        """Determine if research should continue"""
        
        current_iteration = state.get("research_iteration", 0)
        max_iterations = state.get("max_research_iterations", 3)
        
        # Don't continue if we've reached max iterations
        if current_iteration >= max_iterations:
            return False
        
        # Continue if quality is poor and we have gaps
        quality_level = quality_assessment.get("overall_quality", "good")
        has_significant_gaps = len(knowledge_gaps) > 2
        
        should_continue = (
            quality_level in ["poor", "fair"] and 
            has_significant_gaps and 
            current_iteration < max_iterations
        )
        
        return should_continue
    
    def _calculate_analysis_confidence(
        self, 
        quality_assessment: Dict[str, Any], 
        knowledge_gaps: List[str], 
        research_data: Dict[str, Any]
    ) -> float:
        """Calculate confidence in analysis results"""
        
        # Base confidence from research quality
        quality_level = quality_assessment.get("overall_quality", "fair")
        quality_scores = {
            "excellent": 0.9,
            "good": 0.7,
            "fair": 0.5,
            "poor": 0.3
        }
        quality_confidence = quality_scores.get(quality_level, 0.5)
        
        # Adjust for knowledge gaps
        gap_penalty = min(0.3, len(knowledge_gaps) * 0.1)
        
        # Adjust for source count
        source_count = len(research_data.get("sources", []))
        source_bonus = min(0.2, source_count * 0.05)
        
        total_confidence = quality_confidence - gap_penalty + source_bonus
        
        return max(0.1, min(1.0, total_confidence))
