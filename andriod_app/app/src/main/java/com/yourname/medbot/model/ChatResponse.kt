package com.yourname.medbot.model

/**
 * 聊天响应数据类
 * 对应后端 API 的响应结构
 */
data class ChatResponse(
    val status: String,  // "ok" | "error" | "emergency"
    val data: ChatResponseData? = null,
    val error: ErrorInfo? = null
)

data class ChatResponseData(
    val answer: String,
    val sections: List<AnswerSection>? = null,
    val source: String? = null,  // "kg" | "deepseek" | "unknown" | "system"
    val elapsed_ms: Int? = null
)

data class AnswerSection(
    val title: String,
    val content: String,
    val icon: String? = null
)

data class ErrorInfo(
    val code: String,
    val message: String
)
