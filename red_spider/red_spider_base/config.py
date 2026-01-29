# Neo4j 数据库配置信息
# 基于本地 Homebrew 安装的 Neo4j (http://localhost:7474)

NEO4J_CONFIG = {
    # 使用 bolt 协议直连本地单机数据库，避免 neo4j:// 协议的路由错误
    "uri": "neo4j://localhost:7687",
    
    # 使用你之前在驱动脚本中验证成功的账号密码
    "auth": ("neo4j", "wuhan464733265"),
    
    # 本地连接不需要加密
    "encrypted": False
}
