from fastapi import FastAPI

from app.api import chat, emergency
from app.services.neo4j_client import close_neo4j_driver


def create_app() -> FastAPI:
    """
    创建并返回 FastAPI 应用实例。

    已注册的路由：
    - GET /health  ->  "ok"
    - POST /api/chat  ->  聊天接口
    - POST /api/emergency/check  ->  紧急症状检测接口
    - POST /api/emergency/batch-check  ->  批量紧急症状检测接口
    """
    app = FastAPI(
        title="HongZhizhu Medical Assistant API",
        description="红蜘蛛AI医疗助手后端服务",
        version="1.0.0",
    )

    @app.get("/health")
    async def health_check() -> str:
        return "ok"

    # 注册聊天接口路由
    app.include_router(chat.router)
    # 注册紧急症状检测路由
    app.include_router(emergency.router)

    # 应用关闭时清理资源
    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """应用关闭时清理 Neo4j 连接等资源。"""
        close_neo4j_driver()

    return app

