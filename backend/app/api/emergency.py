"""
紧急症状检测接口。

提供独立的紧急症状检测 API，可用于前端实时检测或批量检测。
"""

from __future__ import annotations

import logging
from typing import List

from fastapi import APIRouter

from app.models import ChatRequest, ChatResponse, ChatResponseData, ErrorInfo
from app.utils.emergency import detect_emergency_keywords, get_emergency_message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["emergency"])


@router.post("/emergency/check", response_model=ChatResponse)
async def check_emergency(request: ChatRequest) -> ChatResponse:
    """
    检测用户输入中是否包含高危症状关键词。

    请求体：
    {
        "question": "我最近胸痛，还感觉呼吸困难"
    }

    响应：
    {
        "status": "emergency" | "ok",
        "data": {
            "answer": "⚠️ 紧急提示：检测到严重症状（胸痛、呼吸困难），请立即拨打120...",
            "source": "system"
        }
    }
    """
    question = request.question.strip() if request.question else ""

    if not question:
        return ChatResponse(
            status="error",
            error=ErrorInfo(
                code="empty_question",
                message="问题不能为空。",
            ),
        )

    # 检测高危症状
    is_emergency, matched_keywords = detect_emergency_keywords(question)

    if is_emergency:
        logger.warning(
            f"检测到高危症状关键词：{matched_keywords}, 问题：{question[:50]}..."
        )

        return ChatResponse(
            status="emergency",
            data=ChatResponseData(
                answer=get_emergency_message(matched_keywords),
                source="system",
            ),
        )

    # 未检测到高危症状
    return ChatResponse(
        status="ok",
        data=ChatResponseData(
            answer="未检测到紧急症状，您可以继续描述您的症状。",
            source="system",
        ),
    )


@router.post("/emergency/batch-check")
async def batch_check_emergency(questions: List[str]) -> dict:
    """
    批量检测多个问题中是否包含高危症状。

    请求体：
    [
        "我有点头痛",
        "胸痛，呼吸困难",
        "感冒了"
    ]

    响应：
    {
        "results": [
            {
                "question": "我有点头痛",
                "is_emergency": false,
                "matched_keywords": []
            },
            {
                "question": "胸痛，呼吸困难",
                "is_emergency": true,
                "matched_keywords": ["胸痛", "呼吸困难"]
            },
            ...
        ]
    }
    """
    results = []

    for question in questions:
        if not question or not question.strip():
            results.append(
                {
                    "question": question,
                    "is_emergency": False,
                    "matched_keywords": [],
                }
            )
            continue

        is_emergency, matched_keywords = detect_emergency_keywords(question)
        results.append(
            {
                "question": question,
                "is_emergency": is_emergency,
                "matched_keywords": matched_keywords,
            }
        )

    return {"results": results}


__all__ = ["router"]
