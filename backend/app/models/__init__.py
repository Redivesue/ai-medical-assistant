"""
Pydantic 数据模型聚合入口。

对外只需要从 app.models 导入常用模型：

    from app.models import ChatRequest, ChatResponse, ChatResponseData
"""

from .chat import ChatRequest, ChatResponse, ChatResponseData, AnswerSection, ErrorInfo

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "ChatResponseData",
    "AnswerSection",
    "ErrorInfo",
]

