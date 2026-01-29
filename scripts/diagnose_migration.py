#!/usr/bin/env python3
"""
诊断迁移问题：检查本地 Neo4j 数据库中的所有关系类型和节点
"""

import os
from neo4j import GraphDatabase


def diagnose_local_db():
    """诊断本地数据库"""
    uri = os.getenv("LOCAL_NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("LOCAL_NEO4J_USER", "neo4j")
    password = os.getenv("LOCAL_NEO4J_PASSWORD", "wuhan464733265")
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    print("=" * 60)
    print("本地 Neo4j 数据库诊断")
    print("=" * 60)
    
    with driver.session() as session:
        # 1. 检查所有节点类型和数量
        print("\n📊 节点统计：")
        node_query = """
        MATCH (n)
        RETURN labels(n) as labels, count(n) as count
        ORDER BY count DESC
        """
        result = session.run(node_query)
        for record in result:
            labels = record["labels"]
            count = record["count"]
            print(f"  {labels[0] if labels else 'Unknown'}: {count} 个")
        
        # 2. 检查所有关系类型和数量
        print("\n🔗 关系类型统计：")
        rel_query = """
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        """
        result = session.run(rel_query)
        total_rels = 0
        for record in result:
            rel_type = record["rel_type"]
            count = record["count"]
            total_rels += count
            print(f"  {rel_type}: {count} 个")
        print(f"\n  关系总数: {total_rels}")
        
        # 3. 检查是否有重复的 Disease 节点（可能导致 MERGE 失败）
        print("\n🔍 检查重复的 Disease 节点：")
        dup_query = """
        MATCH (d:Disease)
        WITH d.name as name, count(d) as cnt
        WHERE cnt > 1
        RETURN name, cnt
        ORDER BY cnt DESC
        LIMIT 10
        """
        result = session.run(dup_query)
        duplicates = list(result)
        if duplicates:
            print("  发现重复节点：")
            for record in duplicates:
                print(f"    {record['name']}: {record['cnt']} 个")
        else:
            print("  ✅ 没有发现重复节点")
        
        # 4. 检查是否有空名称的节点
        print("\n🔍 检查空名称节点：")
        empty_query = """
        MATCH (n)
        WHERE n.name IS NULL OR n.name = ''
        RETURN labels(n) as labels, count(n) as count
        """
        result = session.run(empty_query)
        empty_nodes = list(result)
        if empty_nodes:
            print("  发现空名称节点：")
            for record in empty_nodes:
                print(f"    {record['labels']}: {record['count']} 个")
        else:
            print("  ✅ 没有发现空名称节点")
        
        # 5. 检查是否有孤立的关系（指向不存在的节点）
        print("\n🔍 检查关系详情（前10个）：")
        detail_query = """
        MATCH (a)-[r]->(b)
        RETURN type(r) as rel_type, labels(a)[0] as from_label, a.name as from_name,
               labels(b)[0] as to_label, b.name as to_name, r.name as rel_name
        LIMIT 10
        """
        result = session.run(detail_query)
        for record in result:
            print(f"  ({record['from_label']}:{record['from_name']})"
                  f"-[{record['rel_type']}]->"
                  f"({record['to_label']}:{record['to_name']})")
    
    driver.close()


if __name__ == "__main__":
    diagnose_local_db()
