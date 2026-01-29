"""
封装对现有 Red_Spider 机器人的调用逻辑。

目标：
- 复用 `red_spider/red_spider_V2/Deepseek/robot.py` 中已经实现好的业务流程
- 对外提供一个简单的函数：chat_once(question) -> ChatResponseData
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Optional

from app.models import ChatResponseData

# ---------------------------------------------------------------------------
# 将 Deepseek 版本的红蜘蛛机器人所在目录加入 sys.path，便于导入
# 目录结构大致为：
#   .../AIcodes/red_spider/red_spider_V2/Deepseek/robot.py
# 当前文件路径为：
#   .../AIcodes/red_spider/AI医疗助手/backend/app/services/red_spider_service.py
# ---------------------------------------------------------------------------

CURRENT_FILE = Path(__file__).resolve()
# 目录层级说明（从当前文件开始向上）：
#   parents[0] -> services
#   parents[1] -> app
#   parents[2] -> backend
#   parents[3] -> AI医疗助手
#   parents[4] -> red_spider           ✅ 我们需要的根目录
#   parents[5] -> AIcodes
RED_SPIDER_ROOT = CURRENT_FILE.parents[4]  # .../AIcodes/red_spider
DEEPSEEK_DIR = RED_SPIDER_ROOT / "red_spider_V2" / "Deepseek"

if str(DEEPSEEK_DIR) not in sys.path:
    sys.path.append(str(DEEPSEEK_DIR))

try:
    # type: ignore[import]
    from robot import Red_Spider  # noqa: E402
except ImportError as exc:  # pragma: no cover - 导入失败只在环境异常时出现
    raise ImportError(
        f"无法从 {DEEPSEEK_DIR} 导入 Red_Spider，请检查目录结构和 Python 路径配置。",
    ) from exc


_red_spider_instance: Optional["Red_Spider"] = None


def get_red_spider() -> "Red_Spider":
    """
    懒加载全局 Red_Spider 单例，避免在应用启动时就耗时初始化。

    注意：真正调用 chat_once 时才会实例化机器人，
    这一步可能会连接 Neo4j、加载词典/模型等，所以耗时相对较长。
    """

    global _red_spider_instance
    if _red_spider_instance is None:
        # flag='deepseek' 与原始脚本保持一致；model_path 仅为接口兼容占位
        _red_spider_instance = Red_Spider(flag="deepseek", model_path="./pretrain_model")
    return _red_spider_instance


def chat_once(question: str) -> ChatResponseData:
    """
    调用 Red_Spider 进行单轮问答，并包装为 ChatResponseData。
    """

    if not question or not question.strip():
        return ChatResponseData(
            answer="请先描述您的症状，例如：『发烧两天，体温38.5度』",
            source="unknown",
        )

    bot = get_red_spider()
    start = time.perf_counter()
    answer_text = bot.chat_main(question)
    elapsed_ms = int((time.perf_counter() - start) * 1000)

    return ChatResponseData(
        answer=answer_text,
        source="unknown",  # 暂时无法精确区分 KG / DeepSeek，后续可在 Red_Spider 中增加标记
        elapsed_ms=elapsed_ms,
    )


__all__ = ["chat_once", "get_red_spider"]

