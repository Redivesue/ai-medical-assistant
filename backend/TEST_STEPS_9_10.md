# 步骤 9-10 测试说明

## 已完成的内容

### 9. `app/services/neo4j_client.py` - Neo4j 访问封装
- ✅ 提供统一的 Neo4j 查询接口
- ✅ 懒加载单例模式（首次调用时才连接）
- ✅ 支持单个查询 `run_query()` 和批量查询 `run_queries()`
- ✅ 自动重试机制（遇到临时错误时）
- ✅ 连接测试函数 `test_connection()`
- ✅ 应用关闭时自动清理连接

### 10. `app/utils/` + `app/api/emergency.py` - 工具模块和紧急检测 API
- ✅ `utils/emergency.py`: 高危症状关键词检测工具
- ✅ `utils/logger.py`: 日志配置工具
- ✅ `utils/exceptions.py`: 自定义异常类
- ✅ `api/emergency.py`: 紧急症状检测 API（单个和批量）

## 测试步骤

### 1. 测试 Neo4j 客户端

```python
# 在 Python 交互环境中测试
cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/backend
python

>>> from app.services.neo4j_client import test_connection, run_query
>>> 
>>> # 测试连接
>>> test_connection()
True  # 如果返回 True，说明连接成功
>>> 
>>> # 测试查询
>>> result = run_query("MATCH (n) RETURN count(n) AS total LIMIT 1")
>>> print(result)
[{'total': 1234}]  # 示例结果
```

### 2. 测试紧急症状检测工具

```python
>>> from app.utils.emergency import detect_emergency_keywords, get_emergency_message
>>> 
>>> # 测试高危症状检测
>>> is_emergency, keywords = detect_emergency_keywords("我最近胸痛，还感觉呼吸困难")
>>> print(f"是否紧急: {is_emergency}, 匹配关键词: {keywords}")
是否紧急: True, 匹配关键词: ['胸痛', '呼吸困难']
>>> 
>>> # 测试正常症状
>>> is_emergency, keywords = detect_emergency_keywords("我有点头痛")
>>> print(f"是否紧急: {is_emergency}, 匹配关键词: {keywords}")
是否紧急: False, 匹配关键词: []
```

### 3. 测试紧急症状检测 API

启动服务后，使用 curl 或 Postman 测试：

```bash
# 启动服务
cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/backend
./run_local.sh
# 或
uvicorn app.main:app --reload
```

#### 测试单个检测接口

```bash
curl -X POST http://127.0.0.1:8000/api/emergency/check \
  -H "Content-Type: application/json" \
  -d '{"question": "我最近胸痛，还感觉呼吸困难"}'
```

预期响应：
```json
{
  "status": "emergency",
  "data": {
    "answer": "⚠️ 紧急提示：检测到严重症状（胸痛、呼吸困难），请立即拨打120急救电话或前往最近的急诊科就诊！",
    "source": "system"
  }
}
```

#### 测试批量检测接口

```bash
curl -X POST http://127.0.0.1:8000/api/emergency/batch-check \
  -H "Content-Type: application/json" \
  -d '["我有点头痛", "胸痛，呼吸困难", "感冒了"]'
```

预期响应：
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

### 4. 测试聊天接口中的紧急检测

```bash
curl -X POST http://127.0.0.1:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "我胸痛，怎么办？"}'
```

应该返回紧急提示，而不是调用 Red_Spider。

### 5. 访问 API 文档

浏览器打开：`http://127.0.0.1:8000/docs`

可以看到新增的紧急检测接口文档。

## 注意事项

1. **Neo4j 连接**：
   - 确保 Neo4j 服务已启动
   - 检查环境变量 `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` 是否正确
   - 默认值：`bolt://localhost:7687`, `neo4j`, `neo4j`

2. **日志配置**：
   - 可以通过环境变量 `LOG_LEVEL` 设置日志级别（DEBUG/INFO/WARNING/ERROR）
   - 开发环境默认 DEBUG，生产环境默认 INFO

3. **应用关闭**：
   - 应用关闭时会自动调用 `close_neo4j_driver()` 清理 Neo4j 连接
   - 无需手动管理连接生命周期

## 后续优化建议

1. **Neo4j 连接池**：如果并发量较大，可以考虑使用连接池
2. **高危词扩展**：根据实际使用情况，扩展 `EMERGENCY_KEYWORDS` 列表
3. **日志持久化**：生产环境可以考虑将日志写入文件
4. **监控告警**：可以集成监控系统，对紧急症状检测进行统计和告警
