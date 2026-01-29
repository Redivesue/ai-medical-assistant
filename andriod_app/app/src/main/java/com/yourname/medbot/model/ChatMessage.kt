package com.yourname.medbot.model

/**
 * 聊天消息数据类（用于 UI 显示）
 */
data class ChatMessage(
    val text: String,
    val isUser: Boolean,  // true: 用户消息, false: AI 消息
    val timestamp: Long = System.currentTimeMillis(),
    val isLoading: Boolean = false,  // 是否正在加载
    val isError: Boolean = false,    // 是否是错误消息
    val isEmergency: Boolean = false // 是否是紧急提示
)
