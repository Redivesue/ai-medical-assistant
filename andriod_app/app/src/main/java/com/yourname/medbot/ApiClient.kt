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
 * 使用 ApiConfig 中的配置来设置 BASE_URL
 */
class ApiClient {
    private val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(ApiConfig.BASE_URL)
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
        @POST(ApiConfig.CHAT_ENDPOINT)
        suspend fun chat(@Body request: ChatRequest): ChatResponse
    }
}
