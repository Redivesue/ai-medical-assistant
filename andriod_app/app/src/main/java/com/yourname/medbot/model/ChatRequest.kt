package com.yourname.medbot.model

/**
 * 聊天请求数据类
 * 对应后端 API 的请求体
 */
data class ChatRequest(
    val question: String,
    val session_id: String? = null  // 可选，用于多轮对话
)
