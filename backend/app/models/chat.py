"""
聊天相关的请求 / 响应数据模型定义。

与后续 /api/chat 接口保持一致，便于前后端约定统一结构。
"""

from __future__ import annotations

from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """
    /api/chat 的请求体。
    """

    question: str = Field(..., description="用户输入的问题或症状描述")
    session_id: Optional[str] = Field(
        default=None,
        description="会话 ID（预留，用于后续多轮对话）",
    )


class AnswerSection(BaseModel):
    """
    答案的分段信息，例如：
    - 症状分析
    - 可能原因
    - 应对建议
    - 就医指导
    """

    title: str
    content: str
    icon: Optional[str] = None


class ChatResponseData(BaseModel):
    """
    /api/chat 正常返回时的 data 字段。
    """

    answer: str = Field(..., description="最终给用户展示的完整答案文本")
    sections: Optional[List[AnswerSection]] = Field(
        default=None,
        description="可选的分段答案列表，前端可按卡片形式展示",
    )
    source: Literal["kg", "deepseek", "mixed", "unknown"] = Field(
        default="unknown",
        description="答案主要来源：规则+知识图谱 / DeepSeek / 混合 / 未知",
    )
    elapsed_ms: Optional[int] = Field(
        default=None,
        description="从后端视角统计的处理耗时（毫秒）",
    )


class ErrorInfo(BaseModel):
    code: str
    message: str


class ChatResponse(BaseModel):
    """
    /api/chat 的统一响应结构。
    """

    status: Literal["ok", "error", "emergency"] = "ok"
    data: Optional[ChatResponseData] = None
    error: Optional[ErrorInfo] = None

