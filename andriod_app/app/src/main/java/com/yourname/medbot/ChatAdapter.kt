package com.yourname.medbot

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.yourname.medbot.model.ChatMessage

/**
 * 聊天消息列表适配器
 */
class ChatAdapter(private val messages: List<ChatMessage>) :
    RecyclerView.Adapter<ChatAdapter.MessageViewHolder>() {

    class MessageViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val textMessage: TextView = itemView.findViewById(R.id.textMessage)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): MessageViewHolder {
        // 根据消息类型选择不同的布局
        val layoutId = when (viewType) {
            TYPE_USER -> R.layout.item_message_user
            TYPE_AI -> R.layout.item_message_ai
            TYPE_LOADING -> R.layout.item_message_loading
            TYPE_ERROR -> R.layout.item_message_error
            TYPE_EMERGENCY -> R.layout.item_message_emergency
            else -> R.layout.item_message_ai
        }

        val view = LayoutInflater.from(parent.context).inflate(layoutId, parent, false)
        return MessageViewHolder(view)
    }

    override fun onBindViewHolder(holder: MessageViewHolder, position: Int) {
        val message = messages[position]
        holder.textMessage.text = message.text
    }

    override fun getItemCount(): Int = messages.size

    override fun getItemViewType(position: Int): Int {
        val message = messages[position]
        return when {
            message.isUser -> TYPE_USER
            message.isLoading -> TYPE_LOADING
            message.isError -> TYPE_ERROR
            message.isEmergency -> TYPE_EMERGENCY
            else -> TYPE_AI
        }
    }

    companion object {
        private const val TYPE_USER = 1
        private const val TYPE_AI = 2
        private const val TYPE_LOADING = 3
        private const val TYPE_ERROR = 4
        private const val TYPE_EMERGENCY = 5
    }
}
