# Neo4j 数据迁移工具

快速将本地 Neo4j 数据库迁移到 Neo4j Aura 云实例。

## 快速开始

### 1. 安装依赖

```bash
cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/backend
pip install neo4j tqdm  # tqdm 是可选的，用于显示进度
```

### 2. 设置环境变量

```bash
# 本地 Neo4j（如果与默认值不同）
export LOCAL_NEO4J_URI="bolt://localhost:7687"
export LOCAL_NEO4J_USER="neo4j"
export LOCAL_NEO4J_PASSWORD="your_local_password"

# Aura 实例（根据您的实际信息修改）
export AURA_NEO4J_URI="neo4j+s://1f191891.databases.neo4j.io"
export AURA_NEO4J_USER="neo4j"
export AURA_NEO4J_PASSWORD="7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k"
```

### 3. 运行迁移

**方法 1：使用 shell 脚本（推荐）**

```bash
cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/scripts
./run_migration.sh
```

**方法 2：直接运行 Python 脚本**

```bash
cd /Users/hanwu/Documents/AIcodes/red_spider/AI医疗助手/scripts
python3 migrate_to_aura.py
```

## 迁移流程

脚本会自动执行以下步骤：

1. ✅ 测试本地和 Aura 数据库连接
2. 🔧 在 Aura 中创建约束和索引
3. 📦 从本地导出所有节点（Disease, Symptom, Drug, Food）
4. 🔗 从本地导出所有关系
5. 📥 批量导入节点到 Aura
6. 📥 批量导入关系到 Aura
7. 🔍 验证迁移结果（比较数据数量）

## 重要提示

⚠️ **等待 Aura 实例就绪**：创建 Aura 实例后，请等待 60 秒再运行迁移脚本。

⚠️ **密码安全**：不要在代码中硬编码密码，使用环境变量。

⚠️ **网络稳定性**：确保网络连接稳定，避免迁移中断。

## 更新后端配置

迁移完成后，更新后端应用的环境变量：

```bash
export NEO4J_URI="neo4j+s://1f191891.databases.neo4j.io"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k"
```

或在 Render 等部署平台中设置这些环境变量。

## 详细文档

查看 [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md) 获取完整的迁移指南和故障排除说明。
