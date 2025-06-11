"""
Research & Knowledge Analysis Graph

This graph specializes in advanced research and knowledge synthesis.
It conducts comprehensive research across multiple sources, evaluates
source credibility, identifies knowledge gaps, and synthesizes findings.

Integrated with:
- WebOperationsTool for advanced web research
- Memory system for research patterns and trusted sources
- MCP tools for specialized information sources
"""

import logging
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from src.agent.state import ResearchAnalysisState
from memory.integration_pattern import IntegratedNodePattern
from agent.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class ResearchAnalysisGraph:
    """
    Specialized graph for research and knowledge analysis.

    This graph follows the established pattern with 5 integrated nodes:
    1. route_research - Analyze research topic and determine approach
    2. generate_research_queries - Create comprehensive research queries
    3. execute_research - Conduct multi-source research
    4. evaluate_sources - Assess source credibility and quality
    5. synthesize_knowledge - Generate final knowledge synthesis
    """

    def __init__(self):
        self.tool_registry = ToolRegistry()
        self.graph = None

    def create_graph(self) -> StateGraph:
        """Create the research analysis graph"""

        # Create the graph
        workflow = StateGraph(ResearchAnalysisState)

        # Add nodes
        workflow.add_node("route_research", self._create_route_research_node())
        workflow.add_node("generate_research_queries", self._create_generate_research_queries_node())
        workflow.add_node("execute_research", self._create_execute_research_node())
        workflow.add_node("evaluate_sources", self._create_evaluate_sources_node())
        workflow.add_node("synthesize_knowledge", self._create_synthesize_knowledge_node())

        # Define the flow
        workflow.set_entry_point("route_research")
        workflow.add_edge("route_research", "generate_research_queries")
        workflow.add_edge("generate_research_queries", "execute_research")
        workflow.add_edge("execute_research", "evaluate_sources")
        workflow.add_edge("evaluate_sources", "synthesize_knowledge")
        workflow.add_edge("synthesize_knowledge", END)

        self.graph = workflow.compile(name="research-analysis-specialist")
        return self.graph

    def _create_route_research_node(self):
        """Create the research routing node with integrated pattern"""

        async def route_research_logic(state: ResearchAnalysisState) -> ResearchAnalysisState:
            """Analyze research topic and determine approach"""

            research_topic = state.get("research_topic", "")
            research_scope = state.get("research_scope", "general")

            # Analyze research complexity and domain
            academic_indicators = [
                "study", "research", "analysis", "methodology", "framework",
                "theory", "model", "empirical", "systematic", "literature"
            ]

            technical_indicators = [
                "implementation", "architecture", "algorithm", "performance",
                "optimization", "scalability", "security", "integration"
            ]

            business_indicators = [
                "market", "strategy", "competitive", "roi", "cost",
                "revenue", "customer", "business", "industry", "trends"
            ]

            # Determine research domain
            academic_score = sum(1 for indicator in academic_indicators
                               if indicator.lower() in research_topic.lower())
            technical_score = sum(1 for indicator in technical_indicators
                                if indicator.lower() in research_topic.lower())
            business_score = sum(1 for indicator in business_indicators
                               if indicator.lower() in research_topic.lower())

            if academic_score >= max(technical_score, business_score):
                research_domain = "academic"
                research_approach = "systematic_literature_review"
            elif technical_score >= business_score:
                research_domain = "technical"
                research_approach = "technical_documentation_analysis"
            else:
                research_domain = "business"
                research_approach = "market_intelligence_gathering"

            # Determine information sources based on domain
            if research_domain == "academic":
                information_sources = [
                    "google_scholar", "arxiv", "pubmed", "ieee_xplore",
                    "acm_digital_library", "springer", "elsevier"
                ]
            elif research_domain == "technical":
                information_sources = [
                    "github", "stackoverflow", "documentation_sites",
                    "technical_blogs", "api_references", "forums"
                ]
            else:
                information_sources = [
                    "industry_reports", "market_research", "news_sources",
                    "company_websites", "analyst_reports", "surveys"
                ]

            # Set research context
            state["research_domain"] = research_domain
            state["research_approach"] = research_approach
            state["information_sources"] = information_sources
            state["complexity_score"] = academic_score + technical_score + business_score
            state["research_stage"] = "routing_complete"
            state["research_progress"] = 0.2

            logger.info(f"Research routing complete. Domain: {research_domain}, Approach: {research_approach}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="route_research",
            agent_id="research_analyst",
            required_tools=["web_operations"],
            memory_types=["research_pattern", "domain_knowledge"],
            cache_ttl=1800
        )

        async def integrated_route_research(state: ResearchAnalysisState) -> ResearchAnalysisState:
            await pattern.setup()

            cache_key = f"route_research_{hash(state.get('research_topic', ''))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=route_research_logic,
                cache_key=cache_key,
                memory_content=f"Analyzed research topic: {state.get('research_topic', 'unknown')}",
                memory_type="research_routing",
                importance_score=0.7
            )

            return result or state

        return integrated_route_research

    def _create_generate_research_queries_node(self):
        """Create the research query generation node with integrated pattern"""

        async def generate_research_queries_logic(state: ResearchAnalysisState) -> ResearchAnalysisState:
            """Create comprehensive research queries"""

            research_topic = state.get("research_topic", "")
            research_domain = state.get("research_domain", "general")
            research_approach = state.get("research_approach", "general_research")

            # Generate domain-specific queries
            queries = []

            if research_domain == "academic":
                # Academic research queries
                queries.extend([
                    f"systematic review {research_topic}",
                    f"meta-analysis {research_topic}",
                    f"empirical study {research_topic}",
                    f"theoretical framework {research_topic}",
                    f"methodology {research_topic}",
                    f"literature review {research_topic}"
                ])
            elif research_domain == "technical":
                # Technical research queries
                queries.extend([
                    f"{research_topic} implementation guide",
                    f"{research_topic} best practices",
                    f"{research_topic} architecture patterns",
                    f"{research_topic} performance optimization",
                    f"{research_topic} security considerations",
                    f"{research_topic} troubleshooting"
                ])
            else:
                # Business research queries
                queries.extend([
                    f"{research_topic} market analysis",
                    f"{research_topic} industry trends",
                    f"{research_topic} competitive landscape",
                    f"{research_topic} business case",
                    f"{research_topic} ROI analysis",
                    f"{research_topic} market size"
                ])

            # Add general exploratory queries
            queries.extend([
                f"what is {research_topic}",
                f"{research_topic} definition",
                f"{research_topic} examples",
                f"{research_topic} use cases",
                f"{research_topic} benefits",
                f"{research_topic} challenges"
            ])

            # Add comparative queries
            queries.extend([
                f"{research_topic} vs alternatives",
                f"{research_topic} comparison",
                f"{research_topic} pros and cons",
                f"{research_topic} evaluation criteria"
            ])

            # Structure queries with metadata
            structured_queries = []
            for i, query in enumerate(queries):
                structured_queries.append({
                    "id": i + 1,
                    "query": query,
                    "priority": "high" if i < 6 else "medium" if i < 12 else "low",
                    "domain": research_domain,
                    "type": "primary" if i < 6 else "secondary" if i < 12 else "exploratory"
                })

            state["research_queries"] = structured_queries
            state["research_stage"] = "queries_generated"
            state["research_progress"] = 0.4

            logger.info(f"Generated {len(structured_queries)} research queries")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="generate_research_queries",
            agent_id="research_analyst",
            required_tools=["web_operations"],
            memory_types=["query_pattern", "research_template"],
            cache_ttl=1200
        )

        async def integrated_generate_research_queries(state: ResearchAnalysisState) -> ResearchAnalysisState:
            await pattern.setup()

            cache_key = f"queries_{hash(str(state.get('research_topic', '')))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=generate_research_queries_logic,
                cache_key=cache_key,
                memory_content=f"Generated {len(state.get('research_queries', []))} research queries",
                memory_type="query_generation",
                importance_score=0.8
            )

            return result or state

        return integrated_generate_research_queries

    def _create_execute_research_node(self):
        """Create the research execution node with integrated pattern"""

        async def execute_research_logic(state: ResearchAnalysisState) -> ResearchAnalysisState:
            """Conduct multi-source research"""

            research_queries = state.get("research_queries", [])
            information_sources = state.get("information_sources", [])

            # Simulate research execution (in real implementation, would use WebOperationsTool)
            collected_data = {}

            # Process high-priority queries first
            high_priority_queries = [q for q in research_queries if q.get("priority") == "high"]

            for query in high_priority_queries[:5]:  # Limit to top 5 for performance
                query_text = query["query"]

                # Simulate research results for each source
                source_results = {}
                for source in information_sources[:3]:  # Limit sources for performance
                    source_results[source] = {
                        "title": f"Research result for '{query_text}' from {source}",
                        "summary": f"Comprehensive information about {query_text} found in {source}",
                        "relevance_score": 0.8,
                        "credibility_score": 0.9 if source in ["google_scholar", "ieee_xplore"] else 0.7,
                        "publication_date": "2024-01-01",
                        "source_type": "academic" if source in ["google_scholar", "arxiv"] else "technical"
                    }

                collected_data[query_text] = source_results

            # Calculate research metrics
            total_sources = sum(len(results) for results in collected_data.values())
            avg_relevance = sum(
                result["relevance_score"]
                for results in collected_data.values()
                for result in results.values()
            ) / max(total_sources, 1)

            avg_credibility = sum(
                result["credibility_score"]
                for results in collected_data.values()
                for result in results.values()
            ) / max(total_sources, 1)

            research_metrics = {
                "queries_executed": len(high_priority_queries),
                "total_sources": total_sources,
                "avg_relevance_score": round(avg_relevance, 2),
                "avg_credibility_score": round(avg_credibility, 2),
                "source_diversity": len(information_sources)
            }

            state["collected_data"] = collected_data
            state["research_metrics"] = research_metrics
            state["research_stage"] = "research_executed"
            state["research_progress"] = 0.6

            logger.info(f"Research execution complete. Processed {len(high_priority_queries)} queries")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="execute_research",
            agent_id="research_analyst",
            required_tools=["web_operations"],
            memory_types=["research_result", "source_pattern"],
            cache_ttl=900
        )

        async def integrated_execute_research(state: ResearchAnalysisState) -> ResearchAnalysisState:
            await pattern.setup()

            cache_key = f"research_{hash(str(state.get('research_queries', [])))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=execute_research_logic,
                cache_key=cache_key,
                memory_content=f"Executed research for {len(state.get('research_queries', []))} queries",
                memory_type="research_execution",
                importance_score=0.9
            )

            return result or state

        return integrated_execute_research

    def _create_evaluate_sources_node(self):
        """Create the source evaluation node with integrated pattern"""

        async def evaluate_sources_logic(state: ResearchAnalysisState) -> ResearchAnalysisState:
            """Assess source credibility and quality"""

            collected_data = state.get("collected_data", {})

            # Evaluate source credibility
            credibility_criteria = {
                "academic_sources": ["google_scholar", "arxiv", "pubmed", "ieee_xplore"],
                "authoritative_sources": ["documentation_sites", "official_websites"],
                "community_sources": ["stackoverflow", "github", "forums"],
                "commercial_sources": ["industry_reports", "company_websites"]
            }

            source_evaluations = {}
            knowledge_gaps = []

            for query, results in collected_data.items():
                query_evaluation = {
                    "total_sources": len(results),
                    "credibility_breakdown": {"high": 0, "medium": 0, "low": 0},
                    "source_types": {},
                    "avg_credibility": 0,
                    "coverage_score": 0
                }

                total_credibility = 0
                for source, result in results.items():
                    credibility = result.get("credibility_score", 0.5)
                    total_credibility += credibility

                    # Categorize credibility
                    if credibility >= 0.8:
                        query_evaluation["credibility_breakdown"]["high"] += 1
                    elif credibility >= 0.6:
                        query_evaluation["credibility_breakdown"]["medium"] += 1
                    else:
                        query_evaluation["credibility_breakdown"]["low"] += 1

                    # Track source types
                    source_type = result.get("source_type", "unknown")
                    query_evaluation["source_types"][source_type] = query_evaluation["source_types"].get(source_type, 0) + 1

                # Calculate averages
                if results:
                    query_evaluation["avg_credibility"] = round(total_credibility / len(results), 2)
                    query_evaluation["coverage_score"] = min(len(results) / 3, 1.0)  # Ideal: 3+ sources per query

                # Identify knowledge gaps
                if query_evaluation["avg_credibility"] < 0.6:
                    knowledge_gaps.append({
                        "query": query,
                        "issue": "Low source credibility",
                        "recommendation": "Seek more authoritative sources"
                    })

                if query_evaluation["coverage_score"] < 0.5:
                    knowledge_gaps.append({
                        "query": query,
                        "issue": "Insufficient source coverage",
                        "recommendation": "Expand search to additional sources"
                    })

                source_evaluations[query] = query_evaluation

            # Calculate overall source credibility
            all_credibilities = [
                result["credibility_score"]
                for results in collected_data.values()
                for result in results.values()
            ]

            overall_credibility = {
                "avg_credibility": round(sum(all_credibilities) / max(len(all_credibilities), 1), 2),
                "high_credibility_percentage": len([c for c in all_credibilities if c >= 0.8]) / max(len(all_credibilities), 1) * 100,
                "source_diversity_score": len(set(
                    result.get("source_type", "unknown")
                    for results in collected_data.values()
                    for result in results.values()
                )) / 5  # Normalize by expected number of source types
            }

            state["source_credibility"] = overall_credibility
            state["source_evaluations"] = source_evaluations
            state["knowledge_gaps"] = knowledge_gaps
            state["research_stage"] = "sources_evaluated"
            state["research_progress"] = 0.8

            logger.info(f"Source evaluation complete. Avg credibility: {overall_credibility['avg_credibility']}")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="evaluate_sources",
            agent_id="research_analyst",
            required_tools=[],
            memory_types=["credibility_pattern", "source_evaluation"],
            cache_ttl=600
        )

        async def integrated_evaluate_sources(state: ResearchAnalysisState) -> ResearchAnalysisState:
            await pattern.setup()

            cache_key = f"evaluate_{hash(str(state.get('collected_data', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=evaluate_sources_logic,
                cache_key=cache_key,
                memory_content=f"Evaluated sources with avg credibility {state.get('source_credibility', {}).get('avg_credibility', 0)}",
                memory_type="source_evaluation",
                importance_score=0.8
            )

            return result or state

        return integrated_evaluate_sources

    def _create_synthesize_knowledge_node(self):
        """Create the knowledge synthesis node with integrated pattern"""

        async def synthesize_knowledge_logic(state: ResearchAnalysisState) -> ResearchAnalysisState:
            """Generate final knowledge synthesis"""

            collected_data = state.get("collected_data", {})
            source_credibility = state.get("source_credibility", {})
            knowledge_gaps = state.get("knowledge_gaps", [])
            research_topic = state.get("research_topic", "")

            # Synthesize key findings
            key_findings = []
            for query, results in collected_data.items():
                # Extract high-credibility findings
                high_credibility_results = [
                    result for result in results.values()
                    if result.get("credibility_score", 0) >= 0.7
                ]

                if high_credibility_results:
                    finding = {
                        "topic": query,
                        "summary": f"Analysis of {query} reveals consistent patterns across {len(high_credibility_results)} credible sources",
                        "confidence": sum(r["credibility_score"] for r in high_credibility_results) / len(high_credibility_results),
                        "source_count": len(high_credibility_results)
                    }
                    key_findings.append(finding)

            # Generate synthesis summary
            synthesis_summary = {
                "research_topic": research_topic,
                "total_findings": len(key_findings),
                "avg_confidence": round(sum(f["confidence"] for f in key_findings) / max(len(key_findings), 1), 2),
                "knowledge_completeness": max(0, 1.0 - len(knowledge_gaps) / 10),  # Normalize gaps
                "source_diversity": source_credibility.get("source_diversity_score", 0.5)
            }

            # Generate recommendations
            recommendations = []

            if synthesis_summary["avg_confidence"] >= 0.8:
                recommendations.append({
                    "category": "confidence",
                    "priority": "info",
                    "recommendation": "High-confidence research results obtained",
                    "rationale": "Multiple credible sources provide consistent information"
                })
            elif synthesis_summary["avg_confidence"] >= 0.6:
                recommendations.append({
                    "category": "confidence",
                    "priority": "medium",
                    "recommendation": "Consider additional verification of findings",
                    "rationale": "Moderate confidence suggests need for more authoritative sources"
                })
            else:
                recommendations.append({
                    "category": "confidence",
                    "priority": "high",
                    "recommendation": "Conduct additional research with focus on authoritative sources",
                    "rationale": "Low confidence indicates insufficient credible information"
                })

            if len(knowledge_gaps) > 3:
                recommendations.append({
                    "category": "gaps",
                    "priority": "high",
                    "recommendation": "Address identified knowledge gaps before proceeding",
                    "rationale": f"Multiple knowledge gaps ({len(knowledge_gaps)}) may impact decision quality"
                })

            if source_credibility.get("source_diversity_score", 0) < 0.5:
                recommendations.append({
                    "category": "diversity",
                    "priority": "medium",
                    "recommendation": "Expand research to include more diverse source types",
                    "rationale": "Limited source diversity may introduce bias"
                })

            # Calculate overall research quality score
            quality_score = 10.0

            # Adjust based on confidence
            confidence_penalty = (1.0 - synthesis_summary["avg_confidence"]) * 3
            quality_score -= confidence_penalty

            # Adjust based on knowledge gaps
            gaps_penalty = min(len(knowledge_gaps) * 0.5, 3.0)
            quality_score -= gaps_penalty

            # Adjust based on source diversity
            diversity_bonus = source_credibility.get("source_diversity_score", 0.5) * 1.0
            quality_score += diversity_bonus

            # Ensure score bounds
            quality_score = max(min(quality_score, 10.0), 1.0)

            knowledge_synthesis = {
                "synthesis_summary": synthesis_summary,
                "key_findings": key_findings,
                "recommendations": recommendations,
                "research_quality_score": round(quality_score, 1),
                "confidence_level": "high" if quality_score >= 8.0 else "medium" if quality_score >= 6.0 else "low",
                "next_steps": [
                    "Review and validate key findings",
                    "Address any identified knowledge gaps",
                    "Consider additional expert consultation if needed",
                    "Document research methodology and sources"
                ]
            }

            state["knowledge_synthesis"] = knowledge_synthesis
            state["research_quality_score"] = quality_score
            state["source_diversity_score"] = source_credibility.get("source_diversity_score", 0.5)
            state["research_stage"] = "complete"
            state["research_progress"] = 1.0

            logger.info(f"Knowledge synthesis complete. Quality score: {quality_score}/10")
            return state

        # Create integrated node
        pattern = IntegratedNodePattern(
            node_name="synthesize_knowledge",
            agent_id="research_analyst",
            required_tools=[],
            memory_types=["synthesis_pattern", "knowledge_template"],
            cache_ttl=300
        )

        async def integrated_synthesize_knowledge(state: ResearchAnalysisState) -> ResearchAnalysisState:
            await pattern.setup()

            cache_key = f"synthesize_{hash(str(state.get('collected_data', {})))}"

            result = await pattern.execute_with_pattern(
                state=state,
                execution_func=synthesize_knowledge_logic,
                cache_key=cache_key,
                memory_content=f"Synthesized knowledge with quality score {state.get('research_quality_score', 0)}",
                memory_type="knowledge_synthesis",
                importance_score=1.0
            )

            return result or state

        return integrated_synthesize_knowledge
