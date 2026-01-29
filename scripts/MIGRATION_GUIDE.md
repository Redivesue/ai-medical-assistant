# Neo4j 数据迁移指南：本地 -> Aura

本指南将帮助您将本地 Neo4j 数据库的数据迁移到 Neo4j Aura 云实例。

## 前置要求

1. **本地 Neo4j 数据库**：确保本地 Neo4j 正在运行且可以访问
2. **Aura 实例**：已创建并获取连接信息
3. **Python 环境**：Python 3.7+
4. **依赖包**：
   - `neo4j` (>=5.21.0)
   - `tqdm` (用于进度显示，可选)

## 安装依赖

```bash
cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/backend
pip install neo4j tqdm
```

或者如果已有 requirements.txt：

```bash
pip install -r requirements.txt
pip install tqdm  # 如果 requirements.txt 中没有 tqdm
```

## 配置连接信息

### 方法 1：使用环境变量（推荐）

在运行脚本前设置环境变量：

```bash
# 本地 Neo4j 连接信息（如果与默认值不同）
export LOCAL_NEO4J_URI="bolt://localhost:7687"
export LOCAL_NEO4J_USER="neo4j"
export LOCAL_NEO4J_PASSWORD="your_local_password"

# Aura 实例连接信息
export AURA_NEO4J_URI="neo4j+s://1f191891.databases.neo4j.io"
export AURA_NEO4J_USER="neo4j"
export AURA_NEO4J_PASSWORD="7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k"
```

### 方法 2：直接修改脚本

编辑 `migrate_to_aura.py` 文件，在 `main()` 函数中修改默认值。

### 方法 3：命令行参数

```bash
python migrate_to_aura.py \
  <local_uri> <local_user> <local_password> \
  <aura_uri> <aura_user> <aura_password>
```

## 执行迁移

### 步骤 1：测试连接

脚本会自动测试本地和 Aura 的连接。如果连接失败，请检查：

- 本地 Neo4j 是否正在运行
- Aura 实例是否已创建并可用（等待 60 秒后连接）
- 连接信息是否正确
- 网络连接是否正常

### 步骤 2：运行迁移脚本

```bash
cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/scripts
python migrate_to_aura.py
```

### 步骤 3：等待迁移完成

脚本会执行以下步骤：

1. ✅ **测试连接**：验证本地和 Aura 数据库连接
2. 🔧 **创建约束**：在 Aura 中创建必要的唯一性约束
3. 📦 **导出节点**：从本地数据库导出所有节点（Disease, Symptom, Drug, Food）
4. 🔗 **导出关系**：从本地数据库导出所有关系
5. 📥 **导入节点**：批量导入节点到 Aura
6. 📥 **导入关系**：批量导入关系到 Aura
7. 🔍 **验证迁移**：比较本地和 Aura 的数据数量

### 步骤 4：验证结果

脚本会自动验证迁移结果，显示：

```
🔍 验证迁移结果...
  ✅ Disease: 本地=XXX, Aura=XXX
  ✅ Symptom: 本地=XXX, Aura=XXX
  ✅ Drug: 本地=XXX, Aura=XXX
  ✅ Food: 本地=XXX, Aura=XXX
  ✅ 关系总数: 本地=XXX, Aura=XXX
```

如果所有数据数量一致，迁移成功！

## 更新后端配置

迁移完成后，需要更新后端应用的配置以连接到 Aura 实例。

### 方法 1：环境变量（推荐）

在部署环境中设置：

```bash
export NEO4J_URI="neo4j+s://1f191891.databases.neo4j.io"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k"
```

### 方法 2：修改 .env 文件

在 `backend/` 目录下创建或修改 `.env` 文件：

```env
NEO4J_URI=neo4j+s://1f191891.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k
```

### 方法 3：Render 环境变量

如果使用 Render 部署，在 Render Dashboard 中设置环境变量：

1. 进入项目设置
2. 找到 "Environment" 部分
3. 添加以下环境变量：
   - `NEO4J_URI=neo4j+s://1f191891.databases.neo4j.io`
   - `NEO4J_USER=neo4j`
   - `NEO4J_PASSWORD=7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k`

## 故障排除

### 问题 1：连接超时

**症状**：无法连接到 Aura 实例

**解决方案**：
- 等待 60 秒后再连接（Aura 实例创建后需要时间初始化）
- 检查 URI 是否正确（应该是 `neo4j+s://` 开头）
- 检查网络连接和防火墙设置

### 问题 2：认证失败

**症状**：用户名或密码错误

**解决方案**：
- 确认密码是否正确（注意特殊字符）
- 检查用户名是否为 `neo4j`
- 在 Aura Console 中重置密码

### 问题 3：数据不一致

**症状**：验证时发现节点或关系数量不一致

**解决方案**：
- 检查迁移过程中是否有错误信息
- 确认本地数据库数据完整
- 可以重新运行迁移脚本（使用 MERGE 不会重复创建）

### 问题 4：内存不足

**症状**：大数据量迁移时内存不足

**解决方案**：
- 脚本已使用批量导入，但如果数据量非常大，可以考虑分批迁移
- 增加 Python 进程的内存限制

## 注意事项

1. **数据备份**：迁移前建议备份本地数据库
2. **网络稳定性**：确保网络连接稳定，避免迁移中断
3. **Aura 限制**：注意 Aura 实例的存储和性能限制
4. **密码安全**：不要在代码中硬编码密码，使用环境变量
5. **幂等性**：脚本使用 MERGE 操作，可以安全地重复运行

## 迁移后的验证

迁移完成后，建议：

1. 在 Aura Console 中查看数据
2. 运行后端应用测试查询功能
3. 验证所有功能正常工作

## 联系支持

如果遇到问题，可以：

1. 查看 Neo4j Aura 文档：https://neo4j.com/docs/aura/
2. 检查 Aura Console 的日志
3. 联系 Neo4j 支持团队
