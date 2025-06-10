import os
from pydantic import BaseModel, Field
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    """The configuration for the agent."""

    # 查询生成模型 - 使用常规模型，注重速度
    query_generator_model: str = Field(
        default="doubao-pro-256k-241115",
        metadata={
            "description": "The name of the language model to use for the agent's query generation."
        },
    )

    # 反思模型 - 使用深度思考模型，注重推理质量
    reflection_model: str = Field(
        default="doubao-1.5-thinking-pro-250415",
        metadata={
            "description": "The name of the language model to use for the agent's reflection."
        },
    )

    # 答案生成模型 - 使用深度思考模型，注重最终质量
    answer_model: str = Field(
        default="doubao-1.5-thinking-pro-250415",
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    # 网络搜索模型 - 使用常规模型，注重信息提取速度
    web_research_model: str = Field(
        default="doubao-pro-256k-241115",
        metadata={
            "description": "The name of the language model to use for web research."
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

    # 深度思考模型的超时时间设置
    thinking_model_timeout: int = Field(
        default=1800,  # 30分钟
        metadata={"description": "Timeout in seconds for thinking models."},
    )

    # 常规模型的超时时间设置
    regular_model_timeout: int = Field(
        default=300,   # 5分钟
        metadata={"description": "Timeout in seconds for regular models."},
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
