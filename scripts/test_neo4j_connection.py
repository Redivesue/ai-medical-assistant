#!/usr/bin/env python3
"""
测试 Neo4j 连接脚本
帮助找到正确的本地 Neo4j 密码
"""

import os
import sys
from neo4j import GraphDatabase


def test_connection(uri, user, password):
    """测试 Neo4j 连接"""
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
            driver.close()
            return True, "连接成功！"
    except Exception as e:
        return False, str(e)


def main():
    print("=" * 60)
    print("Neo4j 连接测试工具")
    print("=" * 60)
    print()

    # 从环境变量读取，或使用默认值
    uri = os.getenv("LOCAL_NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("LOCAL_NEO4J_USER", "neo4j")
    
    # 尝试从环境变量读取密码
    password = os.getenv("LOCAL_NEO4J_PASSWORD")
    
    if not password:
        print(f"当前配置：")
        print(f"  URI: {uri}")
        print(f"  用户名: {user}")
        print(f"  密码: (未设置)")
        print()
        print("请提供密码进行测试：")
        print("  方法1: 设置环境变量")
        print("    export LOCAL_NEO4J_PASSWORD='your_password'")
        print("    python3 test_neo4j_connection.py")
        print()
        print("  方法2: 直接输入密码（交互式）")
        password = input("请输入 Neo4j 密码: ").strip()
    else:
        print(f"当前配置：")
        print(f"  URI: {uri}")
        print(f"  用户名: {user}")
        print(f"  密码: {'*' * len(password)}")
        print()

    print("正在测试连接...")
    success, message = test_connection(uri, user, password)
    
    if success:
        print("✅", message)
        print()
        print("连接信息正确！可以使用以下命令运行迁移：")
        print(f"  export LOCAL_NEO4J_PASSWORD='{password}'")
        print("  ./run_migration.sh")
    else:
        print("❌ 连接失败:", message)
        print()
        print("可能的解决方案：")
        print("1. 检查 Neo4j 是否正在运行：")
        print("   brew services list  # macOS")
        print("   systemctl status neo4j  # Linux")
        print()
        print("2. 通过 Web 界面重置密码：")
        print("   访问 http://localhost:7474")
        print("   使用当前密码登录，然后修改密码")
        print()
        print("3. 如果忘记了密码，可以重置：")
        print("   - 停止 Neo4j 服务")
        print("   - 删除认证文件（需要找到数据目录）")
        print("   - 重启服务，使用默认密码 neo4j 登录")
        print()
        print("4. 检查密码是否正确（注意大小写和特殊字符）")


if __name__ == "__main__":
    main()
