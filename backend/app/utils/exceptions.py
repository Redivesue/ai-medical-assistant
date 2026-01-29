"""
自定义异常类。

定义应用特定的异常类型，便于统一处理和错误追踪。
"""

from __future__ import annotations


class MedicalAssistantException(Exception):
    """医疗助手应用的基础异常类。"""

    def __init__(self, message: str, code: str = "unknown_error") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


class ConfigurationError(MedicalAssistantException):
    """配置错误异常。"""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="configuration_error")


class DatabaseConnectionError(MedicalAssistantException):
    """数据库连接错误异常。"""

    def __init__(self, message: str) -> None:
        super().__init__(message, code="database_connection_error")


class APIError(MedicalAssistantException):
    """外部 API 调用错误异常。"""

    def __init__(self, message: str, api_name: str = "unknown") -> None:
        super().__init__(message, code=f"api_error_{api_name}")
        self.api_name = api_name


class ValidationError(MedicalAssistantException):
    """输入验证错误异常。"""

    def __init__(self, message: str, field: str = "unknown") -> None:
        super().__init__(message, code=f"validation_error_{field}")
        self.field = field


__all__ = [
    "MedicalAssistantException",
    "ConfigurationError",
    "DatabaseConnectionError",
    "APIError",
    "ValidationError",
]
