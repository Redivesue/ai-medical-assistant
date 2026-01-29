#!/usr/bin/env python3
"""
Neo4j 数据迁移脚本：从本地 Neo4j 迁移到 Neo4j Aura 实例

使用方法：
1. 设置本地 Neo4j 连接信息（如果与默认值不同）
2. 设置 Aura 实例连接信息
3. 运行脚本：python migrate_to_aura.py

环境变量示例：
export LOCAL_NEO4J_URI="bolt://localhost:7687"
export LOCAL_NEO4J_USER="neo4j"
export LOCAL_NEO4J_PASSWORD="your_local_password"

export AURA_NEO4J_URI="neo4j+s://1f191891.databases.neo4j.io"
export AURA_NEO4J_USER="neo4j"
export AURA_NEO4J_PASSWORD="7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k"
"""

import os
import sys
from typing import Dict, List, Tuple, Any
from neo4j import GraphDatabase

# tqdm 是可选的，用于显示进度条
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


class Neo4jMigrator:
    """Neo4j 数据迁移工具类"""

    def __init__(
        self,
        source_uri: str,
        source_user: str,
        source_password: str,
        target_uri: str,
        target_user: str,
        target_password: str,
    ):
        """
        初始化迁移器

        Args:
            source_uri: 源数据库 URI（本地）
            source_user: 源数据库用户名
            source_password: 源数据库密码
            target_uri: 目标数据库 URI（Aura）
            target_user: 目标数据库用户名
            target_password: 目标数据库密码
        """
        self.source_driver = GraphDatabase.driver(
            source_uri, auth=(source_user, source_password)
        )
        self.target_driver = GraphDatabase.driver(
            target_uri, auth=(target_user, target_password)
        )

    def test_connections(self) -> Tuple[bool, bool]:
        """测试源和目标数据库连接"""
        source_ok = False
        target_ok = False

        try:
            with self.source_driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
                source_ok = True
                print("✅ 本地 Neo4j 连接成功")
        except Exception as e:
            print(f"❌ 本地 Neo4j 连接失败: {e}")

        try:
            with self.target_driver.session() as session:
                result = session.run("RETURN 1 as test")
                result.single()
                target_ok = True
                print("✅ Aura Neo4j 连接成功")
        except Exception as e:
            print(f"❌ Aura Neo4j 连接失败: {e}")

        return source_ok, target_ok

    def export_nodes(self) -> Dict[str, List[Dict[str, Any]]]:
        """从源数据库导出所有节点"""
        nodes = {}

        print("\n📦 开始导出节点...")
        with self.source_driver.session() as session:
            # 先获取所有节点类型
            query = """
            MATCH (n)
            RETURN DISTINCT labels(n) as labels
            """
            result = session.run(query)
            all_labels = []
            for record in result:
                labels = record["labels"]
                if labels:
                    all_labels.append(labels[0])
            
            # 导出每种类型的节点
            for label in sorted(all_labels):
                nodes[label] = []
                query = f"MATCH (n:{label}) WHERE n.name IS NOT NULL AND n.name <> '' RETURN DISTINCT n.name as name"
                result = session.run(query)
                node_names = [record["name"] for record in result]
                # 去重（处理重复节点）
                nodes[label] = list(set(node_names))
                print(f"  - {label}: {len(nodes[label])} 个节点（去重后）")

        return nodes

    def export_relationships(self) -> List[Dict[str, Any]]:
        """从源数据库导出所有关系"""
        relationships = []

        print("\n🔗 开始导出关系...")
        with self.source_driver.session() as session:
            # 导出所有关系类型（通用查询）
            query = """
            MATCH (a)-[r]->(b)
            WHERE a.name IS NOT NULL AND a.name <> ''
              AND b.name IS NOT NULL AND b.name <> ''
            RETURN labels(a)[0] as from_label, a.name as from_node,
                   type(r) as rel_type, r.name as rel_name,
                   labels(b)[0] as to_label, b.name as to_node
            """
            result = session.run(query)
            for record in result:
                relationships.append({
                    "from_node": record["from_node"],
                    "from_label": record["from_label"],
                    "to_node": record["to_node"],
                    "to_label": record["to_label"],
                    "rel_type": record["rel_type"],
                    "rel_name": record.get("rel_name") or "",
                })

        # 统计各类型关系数量
        rel_counts = {}
        for rel in relationships:
            rel_type = rel["rel_type"]
            rel_counts[rel_type] = rel_counts.get(rel_type, 0) + 1
        
        print(f"  - 共导出 {len(relationships)} 个关系")
        print("  - 关系类型统计：")
        for rel_type, count in sorted(rel_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"    {rel_type}: {count} 个")
        
        return relationships

    def create_constraints(self):
        """在目标数据库创建约束和索引"""
        print("\n🔧 创建约束和索引...")
        # 为所有有 name 属性的节点类型创建唯一约束
        constraints = [
            "CREATE CONSTRAINT disease_name_unique IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT drug_name_unique IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE",
            "CREATE CONSTRAINT food_name_unique IF NOT EXISTS FOR (f:Food) REQUIRE f.name IS UNIQUE",
            "CREATE CONSTRAINT symptom_name_unique IF NOT EXISTS FOR (s:Symptom) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT producer_name_unique IF NOT EXISTS FOR (p:Producer) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT check_name_unique IF NOT EXISTS FOR (c:Check) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT department_name_unique IF NOT EXISTS FOR (d:Department) REQUIRE d.name IS UNIQUE",
        ]

        with self.target_driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    print(f"  ✅ {constraint.split('FOR')[0].strip()}")
                except Exception as e:
                    print(f"  ⚠️  约束可能已存在: {e}")

    def import_nodes(self, nodes: Dict[str, List[str]]):
        """导入节点到目标数据库"""
        print("\n📥 开始导入节点...")
        with self.target_driver.session() as session:
            for label, node_names in nodes.items():
                if not node_names:
                    continue

                print(f"  导入 {label} 节点 ({len(node_names)} 个)...")
                # 使用 UNWIND 批量创建，提高效率
                query = f"""
                UNWIND $names as name
                MERGE (n:{label} {{name: name}})
                RETURN count(n) as count
                """
                result = session.run(query, names=node_names)
                count = result.single()["count"]
                print(f"    ✅ 成功导入 {count} 个 {label} 节点")

    def import_relationships(self, relationships: List[Dict[str, Any]]):
        """导入关系到目标数据库"""
        print("\n📥 开始导入关系...")
        if not relationships:
            print("  ⚠️  没有关系需要导入")
            return

        # 按关系类型分组批量导入
        rel_groups = {}
        for rel in relationships:
            key = (rel["rel_type"], rel["from_label"], rel["to_label"])
            if key not in rel_groups:
                rel_groups[key] = []
            rel_groups[key].append(rel)

        with self.target_driver.session() as session:
            for (rel_type, from_label, to_label), rels in rel_groups.items():
                print(f"  导入 {rel_type} 关系 ({len(rels)} 个)...")
                # 批量创建关系
                query = f"""
                UNWIND $rels as rel
                MATCH (from:{from_label} {{name: rel.from_node}})
                MATCH (to:{to_label} {{name: rel.to_node}})
                MERGE (from)-[r:{rel_type} {{name: rel.rel_name}}]->(to)
                RETURN count(r) as count
                """
                rel_data = [
                    {
                        "from_node": r["from_node"],
                        "to_node": r["to_node"],
                        "rel_name": r["rel_name"],
                    }
                    for r in rels
                ]
                result = session.run(query, rels=rel_data)
                count = result.single()["count"]
                print(f"    ✅ 成功导入 {count} 个 {rel_type} 关系")

    def verify_migration(self) -> bool:
        """验证迁移结果"""
        print("\n🔍 验证迁移结果...")
        all_match = True
        
        with self.source_driver.session() as source_session, self.target_driver.session() as target_session:
            # 获取所有节点类型
            source_label_query = """
            MATCH (n)
            RETURN DISTINCT labels(n)[0] as label
            ORDER BY label
            """
            source_labels = [record["label"] for record in source_session.run(source_label_query)]
            
            # 比较节点数量
            print("  节点统计：")
            for label in source_labels:
                source_query = f"MATCH (n:{label}) RETURN count(n) as count"
                target_query = f"MATCH (n:{label}) RETURN count(n) as count"

                source_count = source_session.run(source_query).single()["count"]
                target_count = target_session.run(target_query).single()["count"]

                status = "✅" if source_count == target_count else "❌"
                print(f"  {status} {label}: 本地={source_count}, Aura={target_count}")
                if source_count != target_count:
                    all_match = False

            # 比较关系数量和类型
            print("\n  关系统计：")
            source_rel_query = """
            MATCH ()-[r]->()
            RETURN type(r) as rel_type, count(r) as count
            ORDER BY rel_type
            """
            source_rels = {}
            for record in source_session.run(source_rel_query):
                source_rels[record["rel_type"]] = record["count"]
            
            target_rel_query = """
            MATCH ()-[r]->()
            RETURN type(r) as rel_type, count(r) as count
            ORDER BY rel_type
            """
            target_rels = {}
            for record in target_session.run(target_rel_query):
                target_rels[record["rel_type"]] = record["count"]
            
            # 比较每种关系类型
            all_rel_types = sorted(set(list(source_rels.keys()) + list(target_rels.keys())))
            for rel_type in all_rel_types:
                source_count = source_rels.get(rel_type, 0)
                target_count = target_rels.get(rel_type, 0)
                status = "✅" if source_count == target_count else "❌"
                print(f"  {status} {rel_type}: 本地={source_count}, Aura={target_count}")
                if source_count != target_count:
                    all_match = False
            
            # 比较关系总数
            source_rel_total = sum(source_rels.values())
            target_rel_total = sum(target_rels.values())
            status = "✅" if source_rel_total == target_rel_total else "❌"
            print(f"\n  {status} 关系总数: 本地={source_rel_total}, Aura={target_rel_total}")
            if source_rel_total != target_rel_total:
                all_match = False

        return all_match

    def clear_target_database(self):
        """清空目标数据库（可选，用于重新迁移）"""
        print("\n🗑️  清空 Aura 数据库...")
        with self.target_driver.session() as session:
            # 删除所有关系和节点
            session.run("MATCH (n) DETACH DELETE n")
            print("  ✅ 已清空所有数据")
    
    def migrate(self, clear_first=False):
        """执行完整迁移流程"""
        print("=" * 60)
        print("🚀 开始 Neo4j 数据迁移：本地 -> Aura")
        print("=" * 60)

        # 1. 测试连接
        source_ok, target_ok = self.test_connections()
        if not source_ok or not target_ok:
            print("\n❌ 连接测试失败，请检查配置后重试")
            return False

        # 1.5. 可选：清空目标数据库
        if clear_first:
            self.clear_target_database()

        # 2. 创建约束
        self.create_constraints()

        # 3. 导出数据
        nodes = self.export_nodes()
        relationships = self.export_relationships()

        # 4. 导入数据
        self.import_nodes(nodes)
        self.import_relationships(relationships)

        # 5. 验证迁移
        success = self.verify_migration()

        print("\n" + "=" * 60)
        if success:
            print("✅ 迁移完成！数据已成功迁移到 Aura 实例")
        else:
            print("⚠️  迁移完成，但验证时发现数据不一致，请检查")
        print("=" * 60)

        return success

    def close(self):
        """关闭数据库连接"""
        if self.source_driver:
            self.source_driver.close()
        if self.target_driver:
            self.target_driver.close()


def main():
    """主函数"""
    # 从环境变量读取配置
    local_uri = os.getenv("LOCAL_NEO4J_URI", "bolt://localhost:7687")
    local_user = os.getenv("LOCAL_NEO4J_USER", "neo4j")
    local_password = os.getenv("LOCAL_NEO4J_PASSWORD", "neo4j")

    aura_uri = os.getenv(
        "AURA_NEO4J_URI", "neo4j+s://1f191891.databases.neo4j.io"
    )
    aura_user = os.getenv("AURA_NEO4J_USER", "neo4j")
    aura_password = os.getenv(
        "AURA_NEO4J_PASSWORD", "7T4CjCWq2AvUG9s17eKZGvCTF-mRw0LBZa24ddWso-k"
    )

    # 检查是否要清空目标数据库
    clear_first = os.getenv("CLEAR_AURA_FIRST", "false").lower() == "true"
    if "--clear" in sys.argv or "-c" in sys.argv:
        clear_first = True

    # 如果通过命令行参数提供，优先使用
    if len(sys.argv) >= 7:
        local_uri = sys.argv[1]
        local_user = sys.argv[2]
        local_password = sys.argv[3]
        aura_uri = sys.argv[4]
        aura_user = sys.argv[5]
        aura_password = sys.argv[6]

    print("配置信息：")
    print(f"  本地 Neo4j: {local_uri}")
    print(f"  Aura Neo4j: {aura_uri}")
    if clear_first:
        print("  ⚠️  将清空 Aura 数据库后重新迁移")
    print()

    migrator = Neo4jMigrator(
        source_uri=local_uri,
        source_user=local_user,
        source_password=local_password,
        target_uri=aura_uri,
        target_user=aura_user,
        target_password=aura_password,
    )

    try:
        migrator.migrate(clear_first=clear_first)
    except KeyboardInterrupt:
        print("\n\n⚠️  迁移被用户中断")
    except Exception as e:
        print(f"\n\n❌ 迁移过程中发生错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        migrator.close()


if __name__ == "__main__":
    main()
