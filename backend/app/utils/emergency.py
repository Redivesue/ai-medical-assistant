"""
紧急症状检测工具。

提供高危症状关键词检测和紧急提示消息生成功能。
"""

from __future__ import annotations

from typing import List, Tuple

# 高危症状关键词列表（可根据实际需求扩展）
EMERGENCY_KEYWORDS: List[str] = [
    # 心血管相关
    "胸痛",
    "胸闷",
    "心绞痛",
    "心肌梗死",
    "心跳骤停",
    "猝死",
    # 呼吸系统
    "呼吸困难",
    "窒息",
    "气促",
    "呼吸骤停",
    # 出血相关
    "大量出血",
    "大出血",
    "呕血",
    "便血",
    "咯血",
    # 神经系统
    "昏迷",
    "休克",
    "意识丧失",
    "癫痫持续",
    "脑出血",
    "脑梗死",
    # 其他严重症状
    "严重过敏",
    "过敏性休克",
    "中毒",
    "严重外伤",
    "骨折",
    "烧伤",
]


def detect_emergency_keywords(text: str) -> Tuple[bool, List[str]]:
    """
    检测文本中是否包含高危症状关键词。

    参数
    ----
    text : str
        待检测的文本（通常是用户输入的问题）。

    返回
    ----
    Tuple[bool, List[str]]
        (是否检测到高危症状, 匹配到的关键词列表)
    """
    if not text or not text.strip():
        return False, []

    text_lower = text.lower()
    matched_keywords: List[str] = []

    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text or keyword.lower() in text_lower:
            matched_keywords.append(keyword)

    return len(matched_keywords) > 0, matched_keywords


def get_emergency_message(matched_keywords: List[str]) -> str:
    """
    根据匹配到的关键词生成紧急提示消息。

    参数
    ----
    matched_keywords : List[str]
        匹配到的高危症状关键词列表。

    返回
    ----
    str
        紧急提示消息。
    """
    if not matched_keywords:
        return "⚠️ 紧急提示：检测到严重症状，请立即拨打120或前往急诊！"

    keywords_str = "、".join(matched_keywords[:3])  # 最多显示3个关键词
    if len(matched_keywords) > 3:
        keywords_str += "等"

    return (
        f"⚠️ 紧急提示：检测到严重症状（{keywords_str}），"
        f"请立即拨打120急救电话或前往最近的急诊科就诊！"
    )


__all__ = [
    "EMERGENCY_KEYWORDS",
    "detect_emergency_keywords",
    "get_emergency_message",
]
