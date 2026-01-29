# 红蜘蛛AI医疗助手 - API 说明

## 概览

后端基于 FastAPI 提供 HTTP 接口，主要分为两类：

- 聊天接口：`POST /api/chat`
- 紧急症状检测接口：
  - `POST /api/emergency/check`
  - `POST /api/emergency/batch-check`
- 健康检查：`GET /health`

基础 URL 取决于部署环境：

- 本地开发：`http://127.0.0.1:8000`
- Render 生产：例如 `https://your-render-app.onrender.com`

---

## 1. 健康检查 - GET /health

### 请求

- 方法：`GET`
- 路径：`/health`
- 请求体：无

### 响应示例

```json
"ok"
```

---

## 2. 聊天接口 - POST /api/chat

### 描述

接收用户问题，调用红蜘蛛规则+知识图谱+DeepSeek 兜底逻辑，返回 AI 回答。

对应代码：`backend/app/api/chat.py` 中的 `chat_endpoint`。

### 请求

- 方法：`POST`
- 路径：`/api/chat`
- Content-Type：`application/json`

#### 请求体字段

```json
{
  "question": "感冒的症状是什么？",
  "session_id": "optional-session-id-123"  // 可选
}
```

- `question` (string, 必填)：用户输入的问题或症状描述
- `session_id` (string, 可选)：会话 ID，预留用于多轮对话

### 响应

统一响应结构对应 `ChatResponse` 模型：

```json
{
  "status": "ok",
  "data": {
    "answer": "感冒的典型症状包括发热、流鼻涕、咳嗽等……",
    "sections": null,
    "source": "unknown",
    "elapsed_ms": 1234
  },
  "error": null
}
```

#### 字段说明

- `status` (string)：
  - `"ok"`：正常应答
  - `"error"`：服务器内部错误或参数错误
  - `"emergency"`：检测到高危症状，返回紧急提示

- `data` (object, 可选)：
  - `answer` (string)：最终给用户展示的完整回答
  - `sections` (array, 可选)：分段答案列表（后续可扩展前端卡片展示）
  - `source` (string)：
    - `"kg"`：规则+知识图谱
    - `"deepseek"`：DeepSeek 兜底
    - `"mixed"`：混合
    - `"system"`：系统提示（如紧急提示）
    - `"unknown"`：当前未精确区分
  - `elapsed_ms` (int, 可选)：后端处理耗时（毫秒）

- `error` (object, 可选)：
  - `code` (string)：错误码，如 `"empty_question"`, `"internal_error"`
  - `message` (string)：错误描述

### 特殊逻辑

- 如果 `question` 为空或仅为空白：

```json
{
  "status": "error",
  "data": null,
  "error": {
    "code": "empty_question",
    "message": "问题不能为空，请描述您的症状或疑问。"
  }
}
```

- 如果检测到高危症状关键词（如 `"胸痛"`, `"呼吸困难"`, `"大量出血"`, `"昏迷"`, `"休克"`, `"猝死"`）：

```json
{
  "status": "emergency",
  "data": {
    "answer": "⚠️ 紧急提示：检测到严重症状，请立即拨打120或前往急诊！",
    "sections": null,
    "source": "system",
    "elapsed_ms": null
  },
  "error": null
}
```

---

## 3. 紧急检测接口 - POST /api/emergency/check

### 描述

单独检测一条文本中是否包含高危症状关键词，常用于前端实时检测或预检。

对应代码：`backend/app/api/emergency.py` 中的 `check_emergency`。

### 请求

- 方法：`POST`
- 路径：`/api/emergency/check`
- Content-Type：`application/json`

#### 请求体示例

```json
{
  "question": "我最近胸痛，还感觉呼吸困难"
}
```

### 响应示例（检测到紧急症状）

```json
{
  "status": "emergency",
  "data": {
    "answer": "⚠️ 紧急提示：检测到严重症状（胸痛、呼吸困难），请立即拨打120急救电话或前往最近的急诊科就诊！",
    "sections": null,
    "source": "system",
    "elapsed_ms": null
  },
  "error": null
}
```

### 响应示例（未检测到紧急症状）

```json
{
  "status": "ok",
  "data": {
    "answer": "未检测到紧急症状，您可以继续描述您的症状。",
    "sections": null,
    "source": "system",
    "elapsed_ms": null
  },
  "error": null
}
```

---

## 4. 批量紧急检测接口 - POST /api/emergency/batch-check

### 描述

批量检测多个问题中是否包含高危症状，便于前端一次性预检或日志分析。

对应代码：`backend/app/api/emergency.py` 中的 `batch_check_emergency`。

### 请求

- 方法：`POST`
- 路径：`/api/emergency/batch-check`
- Content-Type：`application/json`

#### 请求体示例

```json
[
  "我有点头痛",
  "胸痛，呼吸困难",
  "感冒了"
]
```

### 响应示例

```json
{
  "results": [
    {
      "question": "我有点头痛",
      "is_emergency": false,
      "matched_keywords": []
    },
    {
      "question": "胸痛，呼吸困难",
      "is_emergency": true,
      "matched_keywords": ["胸痛", "呼吸困难"]
    },
    {
      "question": "感冒了",
      "is_emergency": false,
      "matched_keywords": []
    }
  ]
}
```

---

## 5. 错误码约定

- `empty_question`：问题为空
- `internal_error`：服务器内部错误
- `configuration_error_*`：配置相关错误（预留）
- `database_connection_error`：数据库连接错误（预留）
- `api_error_*`：外部 API 调用错误（预留）

---

## 6. 认证与安全（预留）

当前版本接口未强制认证，适用于内网开发和测试环境。

上线生产环境时建议：

- 在网关或服务端增加 API Key / Token 校验
- 限制单 IP 请求频率（防止滥用）
- 对日志进行脱敏处理（避免存储敏感隐私信息）

