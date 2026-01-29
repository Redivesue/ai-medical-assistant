"""
日志配置工具。

统一配置应用日志格式和级别。
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

from app.config import get_settings


def setup_logging(
    level: Optional[str] = None,
    format_string: Optional[str] = None,
) -> None:
    """
    配置应用日志。

    参数
    ----
    level : Optional[str]
        日志级别（如 "DEBUG", "INFO", "WARNING", "ERROR"）。
        如果不提供，从环境变量 LOG_LEVEL 读取，默认为 "INFO"。
    format_string : Optional[str]
        日志格式字符串。如果不提供，使用默认格式。
    """
    import os

    log_level = level or os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = (
        format_string
        or "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 根据环境设置日志级别
    settings = get_settings()
    if settings.environment == "development":
        # 开发环境默认使用 DEBUG 级别（如果未指定）
        if level is None:
            log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()
    else:
        # 生产环境默认使用 INFO 级别
        if level is None:
            log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )

    # 设置第三方库的日志级别（避免过多噪音）
    logging.getLogger("neo4j").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


__all__ = ["setup_logging"]
