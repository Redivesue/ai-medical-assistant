package com.yourname.medbot

import com.yourname.medbot.model.ChatRequest
import com.yourname.medbot.model.ChatResponse
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST
import java.util.concurrent.TimeUnit

/**
 * API 客户端，用于调用后端 HTTP 接口
 * 
 * 使用 ApiConfig 中的配置来设置 BASE_URL
 * 配置了合理的超时时间以应对 Render 免费版的休眠唤醒
 */
class ApiClient {
    private val okHttpClient: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)  // 连接超时：30秒（应对Render休眠唤醒）
        .readTimeout(60, TimeUnit.SECONDS)    // 读取超时：60秒（AI响应可能需要时间）
        .writeTimeout(30, TimeUnit.SECONDS)    // 写入超时：30秒
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY  // 开发时查看请求日志
        })
        .build()

    private val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(ApiConfig.BASE_URL)
        .client(okHttpClient)
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
