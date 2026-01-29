#!/bin/bash
# Neo4j 数据迁移脚本 - 快速运行脚本

# 设置本地 Neo4j 连接信息（如果与默认值不同，请修改）
export LOCAL_NEO4J_URI="${LOCAL_NEO4J_URI:-bolt://localhost:7687}"
export LOCAL_NEO4J_USER="${LOCAL_NEO4J_USER:-neo4j}"
export LOCAL_NEO4J_PASSWORD="${LOCAL_NEO4J_PASSWORD:-neo4j}"

# 设置 Aura 实例连接信息（请根据您的实际信息修改）
export AURA_NEO4J_URI="${AURA_NEO4J_URI:-neo4j+s://1f191891.databases.neo4j.io}"
export AURA_NEO4J_USER="${AURA_NEO4J_USER:-neo4j}"
export AURA_NEO4J_PASSWORD="${AURA_NEO4J_PASSWORD:-7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k}"

# 是否清空 Aura 数据库后重新迁移（默认 false，设置为 true 会清空旧数据）
export CLEAR_AURA_FIRST="${CLEAR_AURA_FIRST:-true}"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 运行迁移脚本
echo "开始执行 Neo4j 数据迁移..."
echo "本地 Neo4j: $LOCAL_NEO4J_URI"
echo "Aura Neo4j: $AURA_NEO4J_URI"
if [ "$CLEAR_AURA_FIRST" = "true" ]; then
    echo "⚠️  将清空 Aura 数据库后重新迁移"
fi
echo ""

python3 "$SCRIPT_DIR/migrate_to_aura.py"
