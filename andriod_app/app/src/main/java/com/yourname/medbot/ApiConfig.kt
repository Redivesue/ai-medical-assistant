package com.yourname.medbot

/**
 * API 配置
 * 
 * 配置说明：
 * - BASE_URL: 后端服务地址
 *   - 本地开发（模拟器）: "http://10.0.2.2:8000"
 *   - 本地开发（真机）: "http://你的电脑IP:8000" (确保手机和电脑在同一网络)
 *   - 生产环境: "https://hongzhizhu-medical-backend.onrender.com"
 */
object ApiConfig {
    // 生产环境 - Render 部署地址
    const val BASE_URL = "https://hongzhizhu-medical-backend.onrender.com"
    
    // API 端点
    const val CHAT_ENDPOINT = "/api/chat"
    const val EMERGENCY_CHECK_ENDPOINT = "/api/emergency/check"
    const val EMERGENCY_BATCH_CHECK_ENDPOINT = "/api/emergency/batch-check"
    
    // 完整 URL（可选，用于直接访问）
    const val CHAT_URL = "$BASE_URL$CHAT_ENDPOINT"
    const val EMERGENCY_CHECK_URL = "$BASE_URL$EMERGENCY_CHECK_ENDPOINT"
    const val EMERGENCY_BATCH_CHECK_URL = "$BASE_URL$EMERGENCY_BATCH_CHECK_ENDPOINT"
}
