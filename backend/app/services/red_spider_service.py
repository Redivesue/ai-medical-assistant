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
#   本地开发：
#     parents[0] -> services
#     parents[1] -> app
#     parents[2] -> backend
#     parents[3] -> AI医疗助手
#     parents[4] -> red_spider           ✅ 本地：red_spider 在 AI医疗助手 同级
#   
#   GitHub/Render 部署（rootDirectory: backend）：
#     parents[0] -> services
#     parents[1] -> app
#     parents[2] -> backend
#     parents[3] -> /opt/render/project (仓库根目录)
#     red_spider/ 在 parents[3] 下
#
# 兼容两种结构：先尝试本地结构，再尝试 GitHub 结构，最后尝试 Render 结构
REPO_ROOT = CURRENT_FILE.parents[3]  # 仓库根目录或 AI医疗助手 目录

# 尝试本地结构：red_spider 在 AI医疗助手 同级
RED_SPIDER_ROOT_LOCAL = CURRENT_FILE.parents[4] / "red_spider"
# 尝试 GitHub 结构：red_spider 在仓库根目录
RED_SPIDER_ROOT_GITHUB = REPO_ROOT / "red_spider"
# 尝试 Render 结构：如果 backend 是 rootDirectory，red_spider 在仓库根目录
RED_SPIDER_ROOT_RENDER = REPO_ROOT / "red_spider"

# 选择存在的路径，按优先级尝试
RED_SPIDER_ROOT = None
candidates = [
    ("本地结构", RED_SPIDER_ROOT_LOCAL),
    ("GitHub/Render结构", RED_SPIDER_ROOT_GITHUB),
    ("Render结构（备用）", RED_SPIDER_ROOT_RENDER),
]

for name, candidate in candidates:
    deepseek_dir = candidate / "red_spider_V2" / "Deepseek"
    if candidate.exists() and deepseek_dir.exists() and (deepseek_dir / "robot.py").exists():
        RED_SPIDER_ROOT = candidate
        break

# 如果都不存在，使用 GitHub/Render 结构（默认），并记录详细错误信息
if RED_SPIDER_ROOT is None:
    RED_SPIDER_ROOT = RED_SPIDER_ROOT_GITHUB
    import logging
    logger = logging.getLogger(__name__)
    error_msg = (
        f"未找到 red_spider 目录！\n"
        f"当前文件: {CURRENT_FILE}\n"
        f"仓库根目录: {REPO_ROOT}\n"
        f"已尝试的路径:\n"
    )
    for name, candidate in candidates:
        deepseek_dir = candidate / "red_spider_V2" / "Deepseek"
        error_msg += (
            f"  - {name}: {candidate}\n"
            f"    存在: {candidate.exists()}\n"
            f"    Deepseek目录存在: {deepseek_dir.exists() if candidate.exists() else False}\n"
            f"    robot.py存在: {(deepseek_dir / 'robot.py').exists() if deepseek_dir.exists() else False}\n"
        )
    logger.error(error_msg)

DEEPSEEK_DIR = RED_SPIDER_ROOT / "red_spider_V2" / "Deepseek"

if str(DEEPSEEK_DIR) not in sys.path:
    sys.path.append(str(DEEPSEEK_DIR))

try:
    # type: ignore[import]
    from robot import Red_Spider  # noqa: E402
except ImportError as exc:  # pragma: no cover - 导入失败只在环境异常时出现
    import logging
    logger = logging.getLogger(__name__)
    logger.error(
        f"无法从 {DEEPSEEK_DIR} 导入 Red_Spider。\n"
        f"当前工作目录: {Path.cwd()}\n"
        f"RED_SPIDER_ROOT: {RED_SPIDER_ROOT}\n"
        f"DEEPSEEK_DIR 是否存在: {DEEPSEEK_DIR.exists()}\n"
        f"sys.path 包含: {[p for p in sys.path if 'red_spider' in p or 'Deepseek' in p]}"
    )
    raise ImportError(
        f"无法从 {DEEPSEEK_DIR} 导入 Red_Spider，请检查目录结构和 Python 路径配置。\n"
        f"确保 red_spider 目录在仓库根目录下，且路径为: {RED_SPIDER_ROOT}",
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

