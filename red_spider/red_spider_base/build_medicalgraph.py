import os
import json
from typing import List, Tuple, Set

from neo4j import GraphDatabase

from config import NEO4J_CONFIG


class MedicalGraph:
    """
    基于 `data/medical.json` 构建疾病相关的知识图谱：
    - 节点：Disease, Symptom, Drug, Food
    - 关系：
        Disease-[:has_symptom]->Symptom
        Disease-[:recommand_drug]->Drug
        Disease-[:recommand_eat]->Food
    """

    def __init__(self) -> None:
        # 当前文件所在目录
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        # 数据文件路径
        self.data_path = os.path.join(cur_dir, "data", "medical.json")
        # Neo4j 驱动
        self.driver = GraphDatabase.driver(**NEO4J_CONFIG)

    # 读取文件，抽取节点 & 关系列表
    def read_nodes(
        self,
    ) -> Tuple[Set[str], Set[str], Set[str], Set[str], List[list], List[list], List[list]]:
        # 共 4 类节点
        drugs: List[str] = []     # 药品
        foods: List[str] = []     # 食物
        diseases: List[str] = []  # 疾病
        symptoms: List[str] = []  # 症状

        # 构建节点实体关系
        rels_recommandeat: List[list] = []   # 疾病-推荐吃食物关系
        rels_recommanddrug: List[list] = []  # 疾病-推荐药品关系
        rels_symptom: List[list] = []        # 疾病-症状关系

        count = 0
        with open(self.data_path, encoding="utf-8") as f:
            for line in f:
                count += 1
                if count % 10 == 0:
                    print("count =", count)

                if not line.strip():
                    continue

                data_json = json.loads(line)
                disease = data_json.get("name")
                if not disease:
                    continue

                diseases.append(disease)

                # 疾病 - 症状
                if "symptom" in data_json and data_json["symptom"]:
                    symptoms += data_json["symptom"]
                    for symptom in data_json["symptom"]:
                        rels_symptom.append([disease, symptom])

                # 疾病 - 推荐药品
                if "recommand_drug" in data_json and data_json["recommand_drug"]:
                    recommand_drug = data_json["recommand_drug"]
                    drugs += recommand_drug
                    for drug in recommand_drug:
                        rels_recommanddrug.append([disease, drug])

                # 疾病 - 推荐食物
                if "recommand_eat" in data_json and data_json["recommand_eat"]:
                    recommand_eat = data_json["recommand_eat"]
                    foods += recommand_eat
                    for food in recommand_eat:
                        rels_recommandeat.append([disease, food])

        return (
            set(drugs),
            set(foods),
            set(symptoms),
            set(diseases),
            rels_recommandeat,
            rels_recommanddrug,
            rels_symptom,
        )

    # 创建知识图谱疾病相关的节点, 疾病, 症状, 药品, 食品
    def create_graphnodes_and_graphrels(self) -> None:
        (
            Drugs,
            Foods,
            Symptoms,
            Diseases,
            rels_recommandeat,
            rels_recommanddrug,
            rels_symptom,
        ) = self.read_nodes()

        print("Drugs:", len(Drugs))
        print("Foods:", len(Foods))
        print("Symptoms:", len(Symptoms))
        print("Diseases:", len(Diseases))
        print("rels_recommandeat:", len(rels_recommandeat))
        print("rels_recommanddrug:", len(rels_recommanddrug))
        print("rels_symptom:", len(rels_symptom))

        with self.driver.session() as session:
            # 创建中心疾病的知识图谱节点
            print("开始创建中心疾病节点......")
            for d in Diseases:
                cypher = "MERGE (a:Disease{name:%r}) RETURN a" % d
                session.run(cypher)

            # 创建“药品”、“食品”、“症状”的知识图谱节点
            print("开始创建药品节点 Drug ......")
            for n in Drugs:
                cypher = "MERGE (a:Drug{name:%r}) RETURN a" % n
                session.run(cypher)

            print("开始创建食品节点 Food ......")
            for n in Foods:
                cypher = "MERGE (a:Food{name:%r}) RETURN a" % n
                session.run(cypher)

            print("开始创建症状节点 Symptom ......")
            for n in Symptoms:
                cypher = "MERGE (a:Symptom{name:%r}) RETURN a" % n
                session.run(cypher)

        # 创建实体关系边
        self.create_relationship("Disease", "Food", rels_recommandeat, "recommand_eat", "推荐食谱")
        self.create_relationship("Disease", "Drug", rels_recommanddrug, "recommand_drug", "推荐药品")
        self.create_relationship("Disease", "Symptom", rels_symptom, "has_symptom", "症状")

    # 创建实体关联边
    def create_relationship(
        self,
        start_node: str,
        end_node: str,
        edges: List[list],
        rel_type: str,
        rel_name: str,
    ) -> None:
        # 去重处理
        set_edges = ["###".join(edge) for edge in edges if len(edge) == 2]
        num_edges = len(set(set_edges))
        print(f"num_edges({rel_type}) =", num_edges)

        with self.driver.session() as session:
            for edge_str in set(set_edges):
                p, q = edge_str.split("###")
                # 注意：这里直接拼接字符串，假设 medical.json 中 name 字段不会包含单引号
                cypher = (
                    "MATCH (p:%s),(q:%s) "
                    "WHERE p.name='%s' AND q.name='%s' "
                    "CREATE (p)-[rel:%s{name:'%s'}]->(q)"
                    % (start_node, end_node, p, q, rel_type, rel_name)
                )
                try:
                    session.run(cypher)
                except Exception as e:
                    # 打印出错的关系，便于排查
                    print("Failed to create relationship:", p, rel_type, q, "error:", e)


if __name__ == "__main__":
    mg = MedicalGraph()
    print("创建知识图谱中的节点和关系......")
    mg.create_graphnodes_and_graphrels()

