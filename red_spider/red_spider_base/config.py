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

# 判断是否为加密URI方案（neo4j+s://、neo4j+ssc://、bolt+s://、bolt+ssc://）
# 这些URI方案已经包含加密信息，不能设置encrypted参数
is_encrypted_uri = (
    NEO4J_URI.startswith("neo4j+s://") or 
    NEO4J_URI.startswith("neo4j+ssc://") or
    NEO4J_URI.startswith("bolt+s://") or
    NEO4J_URI.startswith("bolt+ssc://")
)

# 构建Neo4j配置
# 注意：加密URI方案不能设置encrypted参数，驱动会自动处理
NEO4J_CONFIG = {
    "uri": NEO4J_URI,
    "auth": (NEO4J_USER, NEO4J_PASSWORD),
}

# 只有非加密URI方案才设置encrypted参数
if not is_encrypted_uri:
    NEO4J_CONFIG["encrypted"] = False
