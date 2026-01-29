"""
Neo4j 数据库访问封装。

提供统一的 Neo4j 查询接口，方便后续迁移到云端数据库时只需修改连接配置。
"""

from __future__ import annotations

import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, TransientError

from app.config import get_settings

logger = logging.getLogger(__name__)

# 全局驱动实例（懒加载）
_neo4j_driver: Optional[Driver] = None


def get_neo4j_driver() -> Driver:
    """
    获取全局 Neo4j 驱动实例（懒加载单例模式）。

    首次调用时会根据配置创建驱动，后续调用直接返回已有实例。

    返回
    ----
    Driver
        Neo4j 驱动实例。

    异常
    ----
    ValueError
        如果配置不完整（缺少 URI、用户名或密码）。
    ServiceUnavailable
        如果无法连接到 Neo4j 数据库。
    """
    global _neo4j_driver

    if _neo4j_driver is None:
        settings = get_settings()

        if not settings.neo4j_uri:
            raise ValueError("Neo4j URI 未配置，请设置 NEO4J_URI 环境变量")

        if not settings.neo4j_user or not settings.neo4j_password:
            raise ValueError("Neo4j 认证信息未配置，请设置 NEO4J_USER 和 NEO4J_PASSWORD 环境变量")

        try:
            _neo4j_driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                # 本地开发通常不需要加密，云端可能需要
                encrypted=False,
            )

            # 验证连接
            with _neo4j_driver.session() as session:
                session.run("RETURN 1").data()

            logger.info(f"Neo4j 连接成功：{settings.neo4j_uri}")

        except ServiceUnavailable as e:
            logger.error(f"无法连接到 Neo4j 数据库：{e}")
            raise
        except Exception as e:
            logger.exception(f"初始化 Neo4j 驱动时发生异常：{e}")
            raise

    return _neo4j_driver


def close_neo4j_driver() -> None:
    """
    关闭 Neo4j 驱动连接。

    通常在应用关闭时调用，例如在 FastAPI 的 shutdown 事件中。
    """
    global _neo4j_driver

    if _neo4j_driver is not None:
        try:
            _neo4j_driver.close()
            logger.info("Neo4j 驱动已关闭")
        except Exception as e:
            logger.warning(f"关闭 Neo4j 驱动时发生异常：{e}")
        finally:
            _neo4j_driver = None


@contextmanager
def get_neo4j_session():
    """
    获取 Neo4j 会话的上下文管理器。

    使用方式：
        with get_neo4j_session() as session:
            result = session.run("MATCH (n) RETURN n LIMIT 1").data()

    返回
    ----
    Session
        Neo4j 会话对象。
    """
    driver = get_neo4j_driver()
    session = driver.session()
    try:
        yield session
    finally:
        session.close()


def run_query(
    cypher: str,
    parameters: Optional[Dict[str, Any]] = None,
    max_retries: int = 2,
) -> List[Dict[str, Any]]:
    """
    执行单个 Cypher 查询并返回结果。

    参数
    ----
    cypher : str
        Cypher 查询语句。
    parameters : Optional[Dict[str, Any]]
        查询参数（用于参数化查询，防止注入）。
    max_retries : int
        最大重试次数（遇到临时错误时），默认 2。

    返回
    ----
    List[Dict[str, Any]]
        查询结果列表，每个元素是一个字典，键为 RETURN 子句中的字段名。

    异常
    ----
    ServiceUnavailable
        如果 Neo4j 服务不可用。
    TransientError
        如果遇到临时错误且重试后仍失败。
    """
    if parameters is None:
        parameters = {}

    last_error: Optional[Exception] = None

    for attempt in range(max_retries + 1):
        try:
            with get_neo4j_session() as session:
                result = session.run(cypher, parameters)
                data = result.data()

                logger.debug(
                    f"Neo4j 查询成功 (尝试 {attempt + 1}/{max_retries + 1}): "
                    f"返回 {len(data)} 条记录"
                )

                return data

        except TransientError as e:
            last_error = e
            logger.warning(
                f"Neo4j 查询遇到临时错误 (尝试 {attempt + 1}/{max_retries + 1}): {e}"
            )
            if attempt < max_retries:
                import time

                time.sleep(0.5 * (attempt + 1))  # 简单退避
                continue
            raise

        except Exception as e:
            logger.error(f"Neo4j 查询发生异常：{e}, Cypher: {cypher[:100]}...")
            raise

    # 理论上不会到这里，但为了类型检查
    if last_error:
        raise last_error
    return []


def run_queries(
    queries: List[str],
    parameters: Optional[List[Dict[str, Any]]] = None,
) -> List[List[Dict[str, Any]]]:
    """
    批量执行多个 Cypher 查询。

    参数
    ----
    queries : List[str]
        Cypher 查询语句列表。
    parameters : Optional[List[Dict[str, Any]]]
        每个查询对应的参数列表（长度应与 queries 相同）。

    返回
    ----
    List[List[Dict[str, Any]]]
        每个查询的结果列表。

    注意
    ----
    所有查询在同一个会话中执行，如果某个查询失败，整个批次都会回滚。
    """
    if parameters is None:
        parameters = [{}] * len(queries)

    if len(parameters) != len(queries):
        raise ValueError("参数列表长度必须与查询列表长度相同")

    results: List[List[Dict[str, Any]]] = []

    try:
        with get_neo4j_session() as session:
            for cypher, params in zip(queries, parameters):
                result = session.run(cypher, params)
                results.append(result.data())

        logger.debug(f"批量执行 {len(queries)} 个查询，全部成功")

    except Exception as e:
        logger.error(f"批量执行 Neo4j 查询时发生异常：{e}")
        raise

    return results


def test_connection() -> bool:
    """
    测试 Neo4j 连接是否正常。

    返回
    ----
    bool
        True 表示连接正常，False 表示连接失败。
    """
    try:
        with get_neo4j_session() as session:
            session.run("RETURN 1 AS test").data()
        return True
    except Exception as e:
        logger.error(f"Neo4j 连接测试失败：{e}")
        return False


__all__ = [
    "get_neo4j_driver",
    "close_neo4j_driver",
    "get_neo4j_session",
    "run_query",
    "run_queries",
    "test_connection",
]
