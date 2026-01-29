"""
DeepSeek API 客户端封装。

提供统一的 DeepSeek 调用接口，包含：
- 超时控制
- 重试机制
- 错误处理
- 日志记录
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from openai import OpenAI
from openai._exceptions import APIError, APITimeoutError, RateLimitError

from app.config import get_settings

logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_TIMEOUT = 15.0  # 秒
DEFAULT_MAX_RETRIES = 2  # 最大重试次数
DEFAULT_RETRY_DELAY = 1.0  # 重试延迟（秒）


class DeepSeekClient:
    """
    DeepSeek API 客户端，封装超时、重试、错误处理。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-chat",
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
    ) -> None:
        """
        初始化 DeepSeek 客户端。

        参数
        ----
        api_key : Optional[str]
            DeepSeek API Key。如果不提供，从配置中读取。
        base_url : Optional[str]
            API Base URL。如果不提供，从配置中读取。
        model : str
            使用的模型名称，默认 "deepseek-chat"。
        timeout : float
            请求超时时间（秒），默认 15.0。
        max_retries : int
            最大重试次数，默认 2。
        """
        settings = get_settings()

        self.api_key = api_key or settings.deepseek_api_key
        self.base_url = base_url or settings.deepseek_base_url
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

        if not self.api_key:
            raise ValueError(
                "未提供 DeepSeek API Key。\n"
                "请在初始化时传入 api_key，或在环境变量中设置 DEEPSEEK_API_KEY。"
            )

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0,  # 我们自己实现重试逻辑
        )

        logger.info(f"已初始化 DeepSeek 客户端，模型：{self.model}, 超时：{self.timeout}s")

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        调用 DeepSeek 生成回复，带重试和错误处理。

        参数
        ----
        prompt : str
            用户输入的问题/提示。
        system_prompt : Optional[str]
            系统提示词，如果不提供则使用默认医疗助手提示。
        temperature : float
            生成温度，默认 0.7。

        返回
        ----
        str
            AI 生成的回复文本。如果所有重试都失败，返回错误提示信息。

        异常
        ----
        不会抛出异常，所有错误都会被捕获并返回友好的错误信息。
        """
        if not prompt or not prompt.strip():
            return ""

        default_system = (
            "你是一个非常专业且贴心的中文医疗问答助手，"
            "需要结合医学常识和生活建议，给出温和、易懂的回答。"
        )
        system_content = system_prompt or default_system

        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": prompt},
        ]

        last_error: Optional[Exception] = None

        # 重试逻辑
        for attempt in range(self.max_retries + 1):
            try:
                start_time = time.perf_counter()

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    stream=False,
                )

                elapsed = time.perf_counter() - start_time
                logger.info(
                    f"DeepSeek API 调用成功 (尝试 {attempt + 1}/{self.max_retries + 1}), "
                    f"耗时: {elapsed:.2f}s"
                )

                # 提取回复内容
                try:
                    return response.choices[0].message.content or ""
                except (AttributeError, IndexError, KeyError) as e:
                    logger.warning(f"解析 DeepSeek 响应失败：{e}, 原始响应：{response}")
                    return f"解析 DeepSeek 响应时出错：{str(e)}"

            except APITimeoutError as e:
                last_error = e
                logger.warning(
                    f"DeepSeek API 超时 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                if attempt < self.max_retries:
                    time.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))  # 指数退避
                    continue
                return "抱歉，DeepSeek 服务响应超时，请稍后重试。"

            except RateLimitError as e:
                last_error = e
                logger.warning(
                    f"DeepSeek API 限流 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                if attempt < self.max_retries:
                    # 限流时等待更长时间
                    wait_time = DEFAULT_RETRY_DELAY * (2 ** (attempt + 1))
                    logger.info(f"等待 {wait_time:.1f}s 后重试...")
                    time.sleep(wait_time)
                    continue
                return "抱歉，DeepSeek 服务当前请求过于频繁，请稍后再试。"

            except APIError as e:
                last_error = e
                logger.error(
                    f"DeepSeek API 错误 (尝试 {attempt + 1}/{self.max_retries + 1}): {e}"
                )
                # API 错误通常不需要重试（除非是临时性错误）
                if "500" in str(e) or "503" in str(e):  # 服务器错误，可以重试
                    if attempt < self.max_retries:
                        time.sleep(DEFAULT_RETRY_DELAY * (attempt + 1))
                        continue
                return f"调用 DeepSeek 服务时出错：{str(e)}"

            except Exception as e:
                last_error = e
                logger.exception(
                    f"DeepSeek API 调用发生未知异常 (尝试 {attempt + 1}/{self.max_retries + 1})"
                )
                if attempt < self.max_retries:
                    time.sleep(DEFAULT_RETRY_DELAY)
                    continue
                return f"调用 DeepSeek 服务时发生未知错误：{str(e)}"

        # 所有重试都失败
        logger.error(f"DeepSeek API 调用失败，已重试 {self.max_retries + 1} 次，最后错误：{last_error}")
        return "抱歉，DeepSeek 服务暂时不可用，请稍后重试。"


__all__ = ["DeepSeekClient", "DEFAULT_TIMEOUT", "DEFAULT_MAX_RETRIES"]
