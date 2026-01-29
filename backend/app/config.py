"""
应用配置模块。

统一管理 DeepSeek、Neo4j 等相关配置，优先从环境变量读取，
本地开发可通过 .env 文件覆盖，避免在代码中硬编码敏感信息。
"""

from __future__ import annotations

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel

# 尝试从当前工作目录及其父目录加载 .env，方便本地开发
load_dotenv()


class Settings(BaseModel):
    # 运行环境：development / production 等
    environment: str = os.getenv("ENVIRONMENT", "development")

    # DeepSeek 相关配置
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    deepseek_base_url: str = os.getenv(
        "DEEPSEEK_BASE_URL",
        "https://api.deepseek.com",
    )

    # Neo4j 相关配置（当前本地默认值来自 Neo4j 安装说明）
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "neo4j")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    返回全局唯一的配置实例，避免重复解析环境变量。
    使用方式：

        from app.config import get_settings
        settings = get_settings()
        print(settings.deepseek_api_key)
    """

    return Settings()


__all__ = ["Settings", "get_settings"]

