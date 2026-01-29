"""
Neo4j 数据库配置信息

优先从环境变量读取配置（适用于生产环境，如 Render + Neo4j Aura），
如果环境变量未设置，则使用本地开发默认值。

环境变量：
- NEO4J_URI: Neo4j 连接 URI（如：neo4j+s://xxx.databases.neo4j.io 或 bolt://localhost:7687）
- NEO4J_USER: 用户名（默认：neo4j）
- NEO4J_PASSWORD: 密码
"""

import os

# 从环境变量读取配置，如果没有则使用本地默认值
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "neo4j")

# 判断是否为 Aura 连接（neo4j+s:// 或 neo4j+ssc://）
is_aura = NEO4J_URI.startswith("neo4j+s://") or NEO4J_URI.startswith("neo4j+ssc://")

NEO4J_CONFIG = {
    "uri": NEO4J_URI,
    "auth": (NEO4J_USER, NEO4J_PASSWORD),
    # Aura 连接需要加密，本地连接不需要
    "encrypted": is_aura,
}
