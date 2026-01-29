"""
聊天接口：POST /api/chat

接收用户问题，调用 Red_Spider 服务，返回结构化响应。
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter

from app.models import ChatRequest, ChatResponse, ChatResponseData, ErrorInfo
from app.services.red_spider_service import chat_once

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    处理用户提问，返回 AI 回答。

    请求体：
    {
        "question": "感冒的症状是什么？",
        "session_id": "optional_session_id"  // 可选，用于多轮对话
    }

    响应：
    {
        "status": "ok",
        "data": {
            "answer": "感冒的典型症状包括...",
            "sections": [...],
            "source": "kg" | "deepseek" | "unknown",
            "elapsed_ms": 1234
        }
    }
    """
    question = request.question.strip() if request.question else ""

    # 空问题检查
    if not question:
        return ChatResponse(
            status="error",
            error=ErrorInfo(
                code="empty_question",
                message="问题不能为空，请描述您的症状或疑问。",
            ),
        )

    # 高危症状关键词检测（前端已做一层，后端再加固）
    emergency_keywords = ["胸痛", "呼吸困难", "大量出血", "昏迷", "休克", "猝死"]
    if any(keyword in question for keyword in emergency_keywords):
        logger.warning(f"检测到高危症状关键词：{question}")
        return ChatResponse(
            status="emergency",
            data=ChatResponseData(
                answer="⚠️ 紧急提示：检测到严重症状，请立即拨打120或前往急诊！",
                source="system",
            ),
        )

    try:
        # 调用 Red_Spider 服务
        result: ChatResponseData = chat_once(question)

        return ChatResponse(
            status="ok",
            data=result,
        )

    except Exception as exc:
        logger.exception(f"处理问题时发生异常：{question[:50]}...")
        return ChatResponse(
            status="error",
            error=ErrorInfo(
                code="internal_error",
                message=f"服务器内部错误：{str(exc)}",
            ),
        )


__all__ = ["router"]
