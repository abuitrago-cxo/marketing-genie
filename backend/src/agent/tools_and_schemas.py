from typing import List
from pydantic import BaseModel, Field


class SearchQueryList(BaseModel):
    query: List[str] = Field(
        description="A list of search queries to be used for web research."
    )
    rationale: str = Field(
        description="A brief explanation of why these queries are relevant to the research topic."
    )


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


# 数据库查询相关的Schema
class SQLQuery(BaseModel):
    """单个SQL查询及其结果"""
    sql: str = Field(description="生成的SQL查询语句")
    explanation: str = Field(description="对该SQL查询的解释说明")
    result_description: str = Field(description="预期结果的描述")


class DatabaseQueryResult(BaseModel):
    """数据库查询结果"""
    queries: List[SQLQuery] = Field(description="生成的SQL查询列表")
    summary: str = Field(description="查询结果的总结说明")
