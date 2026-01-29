package com.yourname.medbot

import com.yourname.medbot.model.ChatRequest
import com.yourname.medbot.model.ChatResponse
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

/**
 * API 客户端，用于调用后端 HTTP 接口
 * 
 * 配置说明：
 * - BASE_URL: 后端服务地址
 *   - 本地开发: "http://10.0.2.2:8000" (Android 模拟器访问本地)
 *   - 真机测试: "http://你的电脑IP:8000" (确保手机和电脑在同一网络)
 *   - 生产环境: "https://your-render-app.onrender.com"
 */
class ApiClient {
    companion object {
        // TODO: 根据实际部署情况修改此地址
        // 本地开发（模拟器）: "http://10.0.2.2:8000"
        // 本地开发（真机）: "http://192.168.x.x:8000" (替换为你的电脑IP)
        // 生产环境: "https://your-render-app.onrender.com"
        private const val BASE_URL = "https://your-render-app.onrender.com"
    }

    private val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .addConverterFactory(GsonConverterFactory.create())
        .build()

    private val apiService: ApiService = retrofit.create(ApiService::class.java)

    /**
     * 发送聊天请求
     */
    suspend fun chat(request: ChatRequest): ChatResponse {
        return apiService.chat(request)
    }

    /**
     * Retrofit 接口定义
     */
    private interface ApiService {
        @POST("/api/chat")
        suspend fun chat(@Body request: ChatRequest): ChatResponse
    }
}
