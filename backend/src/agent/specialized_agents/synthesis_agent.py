"""
Synthesis Agent

Specialized agent for final answer generation and synthesis.
"""

from typing import Dict, Any, List
from datetime import datetime

from .base_agent import BaseSpecializedAgent


class SynthesisAgent(BaseSpecializedAgent):
    """
    Synthesis Agent for final answer generation and integration.
    
    Capabilities:
    - Multi-source information synthesis
    - Citation generation and management
    - Answer quality optimization
    - Comprehensive response formatting
    """
    
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute synthesis phase with final answer generation.
        
        Args:
            state: Current workflow state with research and analysis data
            
        Returns:
            Updated state with final synthesized answer
        """
        try:
            print(f"SynthesisAgent executing with state: {type(state).__name__}")
            
            # Validate state is a dictionary
            if not isinstance(state, dict):
                print(f"Warning: Synthesis agent received non-dict state of type {type(state).__name__}")
                # Create a minimal valid state
                state = {"original_query": "Unknown query", "messages": []}
            
            # Get all available data with validation
            research_data = state.get("research_data", {})
            if not isinstance(research_data, dict):
                print(f"Warning: research_data is not a dictionary: {type(research_data).__name__}")
                research_data = {"sources": [], "search_results": []}
                
            analysis_data = state.get("analysis_data", {})
            if not isinstance(analysis_data, dict):
                print(f"Warning: analysis_data is not a dictionary: {type(analysis_data).__name__}")
                analysis_data = {}
                
            original_query = state.get("original_query", "")
            if not original_query:
                original_query = "Unknown query"
                
            print(f"Original query for synthesis: {original_query}")
            
            # Use the original graph's finalization capabilities
            from ..graph import finalize_answer
            
            # Prepare comprehensive state for finalization with validation
            messages = state.get("messages", [])
            search_results = []
            if isinstance(research_data, dict) and "search_results" in research_data:
                search_results = research_data["search_results"]
                if not isinstance(search_results, list):
                    print(f"Warning: search_results is not a list: {type(search_results).__name__}")
                    search_results = []
                    
            reflection_summary = ""
            if isinstance(analysis_data, dict) and "reflection_summary" in analysis_data:
                reflection_summary = analysis_data["reflection_summary"]
            elif isinstance(analysis_data, dict) and "reflection" in analysis_data:
                reflection_summary = analysis_data["reflection"]
            else:
                reflection_summary = "Analysis completed with limited data"
                
            finalize_state = {
                "messages": messages,
                "search_results": search_results,
                "reflection": reflection_summary
            }
            
            # Generate base answer with error handling
            try:
                print("Calling finalize_answer function")
                final_result = finalize_answer(finalize_state, self.config)
                
                # Check if final_result is a dictionary
                if not isinstance(final_result, dict):
                    print(f"Warning: final_result is not a dictionary: {type(final_result).__name__}")
                    base_answer = f"Based on the information gathered, I can provide the following answer: {original_query}"
                else:
                    base_answer = final_result.get("final_answer", "")
                    if "messages" in final_result and final_result["messages"] and hasattr(final_result["messages"][-1], 'content'):
                        # Extract from message object if present
                        base_answer = final_result["messages"][-1].content
                        
                if not base_answer:
                    base_answer = f"Based on the available information, I can provide an answer to your question about {original_query}."
                    
            except Exception as finalize_error:
                print(f"Error in finalize_answer step: {str(finalize_error)}")
                base_answer = f"I've analyzed the information related to your question about {original_query}."
        
            # Enhance answer with specialized insights (with error handling)
            try:
                enhanced_answer = self._enhance_answer_with_insights(
                    base_answer, research_data, analysis_data, original_query
                )
            except Exception as enhance_error:
                print(f"Error enhancing answer: {str(enhance_error)}")
                enhanced_answer = base_answer
            
            # Generate comprehensive citations (with error handling)
            try:
                citations = self._generate_citations(research_data)
            except Exception as citation_error:
                print(f"Error generating citations: {str(citation_error)}")
                citations = []
            
            # Calculate synthesis confidence (with error handling)
            try:
                confidence = self._calculate_synthesis_confidence(
                    research_data, analysis_data, enhanced_answer, citations
                )
            except Exception as confidence_error:
                print(f"Error calculating confidence: {str(confidence_error)}")
                confidence = 0.5  # Default medium confidence
            
            # Ensure we have a valid answer
            if not enhanced_answer:
                enhanced_answer = f"Based on my analysis, here's what I can tell you about {original_query}: Additional research may be needed to provide a more comprehensive answer."
            
            # Prepare synthesis data
            synthesis_data = {
                "base_answer_length": len(base_answer),
                "enhanced_answer_length": len(enhanced_answer),
                "citations_generated": len(citations),
                "research_sources_used": len(research_data.get("sources", [])) if isinstance(research_data, dict) else 0,
                "analysis_insights_integrated": bool(analysis_data),
                "synthesis_timestamp": datetime.now().isoformat()
            }
            
            print("Synthesis completed successfully")
            return {
                **state,
                "synthesis_data": synthesis_data,
                "final_answer": enhanced_answer,
                "citations": citations,
                "synthesis_confidence": confidence,
                "synthesis_timestamp": datetime.now().isoformat(),
                "current_agent": "synthesis",
                "workflow_stage": "complete"
            }
            
        except Exception as e:
            print(f"Critical error in SynthesisAgent.execute: {str(e)}")
            # Provide a fallback answer
            fallback_answer = f"After analyzing the available information about '{original_query}', I've compiled a response. Note that additional research might provide more comprehensive details."
            
            # Return a minimal valid state with error information but still providing an answer
            return {
                **state,
                "synthesis_data": {
                    "error": str(e),
                    "synthesis_timestamp": datetime.now().isoformat()
                },
                "final_answer": fallback_answer,
                "citations": [],
                "synthesis_confidence": 0.3,
                "synthesis_timestamp": datetime.now().isoformat(),
                "current_agent": "synthesis",
                "workflow_stage": "complete",
                "error": f"Synthesis failed: {str(e)}"
            }
    
    def _enhance_answer_with_insights(
        self, 
        base_answer: str, 
        research_data: Dict[str, Any], 
        analysis_data: Dict[str, Any], 
        original_query: str
    ) -> str:
        """Enhance the base answer with research and analysis insights"""
        
        enhanced_answer = base_answer
        
        # Add research summary if significant
        research_summary = research_data.get("research_summary", "")
        if research_summary and len(research_summary) > 50:
            enhanced_answer += f"\n\n## Research Summary\n\n{research_summary}"
        
        # Add source quality information
        sources = research_data.get("sources", [])
        if sources:
            high_quality_sources = [s for s in sources if s.get("quality_score", 0) > 0.7]
            if high_quality_sources:
                enhanced_answer += f"\n\n*This response is based on {len(sources)} sources, including {len(high_quality_sources)} high-quality references.*"
        
        # Add analysis insights
        quality_assessment = analysis_data.get("quality_assessment", {})
        if quality_assessment:
            quality_level = quality_assessment.get("overall_quality", "")
            if quality_level in ["excellent", "good"]:
                enhanced_answer += f"\n\n*Research quality: {quality_level.title()} - comprehensive information available.*"
            elif quality_level in ["fair", "poor"]:
                enhanced_answer += f"\n\n*Note: Research coverage is {quality_level}. Additional information may be available from specialized sources.*"
        
        # Add knowledge gaps warning if significant
        knowledge_gaps = analysis_data.get("knowledge_gaps_identified", 0)
        if knowledge_gaps > 2:
            enhanced_answer += f"\n\n*Please note: Some aspects of your query may require additional specialized research.*"
        
        return enhanced_answer
    
    def _generate_citations(self, research_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate comprehensive citations from research sources"""
        
        sources = research_data.get("sources", [])
        citations = []
        
        # Sort sources by quality score
        sorted_sources = sorted(sources, key=lambda x: x.get("quality_score", 0), reverse=True)
        
        # Generate citations for top sources
        for i, source in enumerate(sorted_sources[:10]):  # Limit to top 10
            citation = {
                "source_id": i + 1,
                "title": source.get("title", f"Source {i + 1}"),
                "url": source.get("url", ""),
                "snippet": source.get("snippet", "")[:300],  # Limit snippet length
                "relevance_score": source.get("quality_score", 0.5),
                "domain": self._extract_domain(source.get("url", "")),
                "citation_timestamp": datetime.now().isoformat()
            }
            
            # Add quality indicators
            quality_score = source.get("quality_score", 0)
            if quality_score > 0.8:
                citation["quality_indicator"] = "High Quality"
            elif quality_score > 0.6:
                citation["quality_indicator"] = "Good Quality"
            else:
                citation["quality_indicator"] = "Standard"
            
            citations.append(citation)
        
        return citations
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for citation"""
        if not url:
            return "Unknown"
        
        try:
            # Simple domain extraction
            if "//" in url:
                domain = url.split("//")[1].split("/")[0]
            else:
                domain = url.split("/")[0]
            
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            
            return domain
        except:
            return "Unknown"
    
    def _calculate_synthesis_confidence(
        self, 
        research_data: Dict[str, Any], 
        analysis_data: Dict[str, Any], 
        final_answer: str, 
        citations: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in synthesis results"""
        
        # Base confidence from research quality
        research_confidence = research_data.get("research_confidence", 0.5)
        analysis_confidence = analysis_data.get("analysis_confidence", 0.5)
        
        # Average of research and analysis confidence
        base_confidence = (research_confidence + analysis_confidence) / 2
        
        # Boost for good citation coverage
        citation_boost = min(0.2, len(citations) * 0.02)
        
        # Boost for comprehensive answer
        answer_length_boost = min(0.1, len(final_answer) / 1000 * 0.1)
        
        # Penalty for knowledge gaps
        knowledge_gaps = analysis_data.get("knowledge_gaps_identified", 0)
        gap_penalty = min(0.2, knowledge_gaps * 0.05)
        
        total_confidence = base_confidence + citation_boost + answer_length_boost - gap_penalty
        
        return max(0.1, min(1.0, total_confidence))
