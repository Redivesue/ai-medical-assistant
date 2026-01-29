package com.yourname.medbot

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.yourname.medbot.databinding.ActivityMainBinding
import com.yourname.medbot.model.ChatMessage
import com.yourname.medbot.model.ChatRequest
import kotlinx.coroutines.launch

/**
 * 主聊天界面
 * 
 * 功能：
 * - 显示聊天消息列表
 * - 输入问题并发送
 * - 接收并显示 AI 回答
 */
class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var chatAdapter: ChatAdapter
    private val apiClient = ApiClient()

    private val messages = mutableListOf<ChatMessage>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        setupRecyclerView()
        setupSendButton()
    }

    /**
     * 设置消息列表 RecyclerView
     */
    private fun setupRecyclerView() {
        chatAdapter = ChatAdapter(messages)
        binding.recyclerViewMessages.apply {
            layoutManager = LinearLayoutManager(this@MainActivity)
            adapter = chatAdapter
        }
    }

    /**
     * 设置发送按钮点击事件
     */
    private fun setupSendButton() {
        binding.buttonSend.setOnClickListener {
            val question = binding.editTextQuestion.text.toString().trim()
            if (question.isNotEmpty()) {
                sendMessage(question)
                binding.editTextQuestion.text.clear()
            } else {
                Toast.makeText(this, "请输入您的问题", Toast.LENGTH_SHORT).show()
            }
        }
    }

    /**
     * 发送消息到后端并显示回复
     */
    private fun sendMessage(question: String) {
        // 添加用户消息到列表
        val userMessage = ChatMessage(
            text = question,
            isUser = true,
            timestamp = System.currentTimeMillis()
        )
        messages.add(userMessage)
        chatAdapter.notifyItemInserted(messages.size - 1)
        binding.recyclerViewMessages.scrollToPosition(messages.size - 1)

        // 显示加载状态
        val loadingMessage = ChatMessage(
            text = "红蜘蛛正在思考中...",
            isUser = false,
            isLoading = true,
            timestamp = System.currentTimeMillis()
        )
        messages.add(loadingMessage)
        val loadingIndex = messages.size - 1
        chatAdapter.notifyItemInserted(loadingIndex)
        binding.recyclerViewMessages.scrollToPosition(loadingIndex)

        // 禁用发送按钮，防止重复提交
        binding.buttonSend.isEnabled = false

        // 调用 API
        lifecycleScope.launch {
            try {
                val response = apiClient.chat(ChatRequest(question = question))

                // 移除加载消息
                messages.removeAt(loadingIndex)
                chatAdapter.notifyItemRemoved(loadingIndex)

                // 添加 AI 回复
                if (response.status == "ok" && response.data != null) {
                    val aiMessage = ChatMessage(
                        text = response.data.answer,
                        isUser = false,
                        timestamp = System.currentTimeMillis()
                    )
                    messages.add(aiMessage)
                    chatAdapter.notifyItemInserted(messages.size - 1)
                } else if (response.status == "emergency" && response.data != null) {
                    // 紧急症状提示
                    val emergencyMessage = ChatMessage(
                        text = response.data.answer,
                        isUser = false,
                        isEmergency = true,
                        timestamp = System.currentTimeMillis()
                    )
                    messages.add(emergencyMessage)
                    chatAdapter.notifyItemInserted(messages.size - 1)
                    Toast.makeText(
                        this@MainActivity,
                        "检测到紧急症状，请立即就医！",
                        Toast.LENGTH_LONG
                    ).show()
                } else {
                    // 错误处理：显示后端返回的具体错误信息
                    val errorText = if (response.error != null) {
                        // 显示后端返回的错误信息
                        response.error.message
                    } else {
                        // 如果没有错误信息，显示默认提示
                        "抱歉，服务暂时不可用，请稍后重试。"
                    }
                    val errorMessage = ChatMessage(
                        text = errorText,
                        isUser = false,
                        isError = true,
                        timestamp = System.currentTimeMillis()
                    )
                    messages.add(errorMessage)
                    chatAdapter.notifyItemInserted(messages.size - 1)
                }

                binding.recyclerViewMessages.scrollToPosition(messages.size - 1)

            } catch (e: Exception) {
                // 移除加载消息
                if (loadingIndex < messages.size) {
                    messages.removeAt(loadingIndex)
                    chatAdapter.notifyItemRemoved(loadingIndex)
                }

                // 根据异常类型显示更友好的错误信息
                val errorText = when {
                    e.message?.contains("timeout", ignoreCase = true) == true -> {
                        "请求超时，服务器可能正在启动中（免费版服务需要30-60秒唤醒），请稍后重试。"
                    }
                    e.message?.contains("Unable to resolve host", ignoreCase = true) == true -> {
                        "网络连接失败，请检查网络设置。"
                    }
                    e.message?.contains("Connection refused", ignoreCase = true) == true -> {
                        "无法连接到服务器，请检查服务器地址是否正确。"
                    }
                    else -> {
                        "网络错误：${e.message ?: "未知错误"}"
                    }
                }

                val errorMessage = ChatMessage(
                    text = errorText,
                    isUser = false,
                    isError = true,
                    timestamp = System.currentTimeMillis()
                )
                messages.add(errorMessage)
                chatAdapter.notifyItemInserted(messages.size - 1)
                binding.recyclerViewMessages.scrollToPosition(messages.size - 1)

                Toast.makeText(
                    this@MainActivity,
                    errorText,
                    Toast.LENGTH_LONG
                ).show()

            } finally {
                // 恢复发送按钮
                binding.buttonSend.isEnabled = true
            }
        }
    }
}
