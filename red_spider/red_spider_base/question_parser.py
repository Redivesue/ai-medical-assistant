from typing import Dict, List, Any


class QuestionPaser:  # 保持与你提供的类名一致（原版就是 Paser）
    """
    问题解析子任务：
    - 接收问题分类结果（来自 QuestionClassifier）
    - 根据 question_types + 实体，组装对应的 Neo4j Cypher 查询语句
    """

    # 构建实体节点字典：{"disease": [..], "drug": [..], "food": [..], "symptom": [..]}
    def build_entitydict(self, args: Dict[str, List[str]]) -> Dict[str, List[str]]:
        entity_dict: Dict[str, List[str]] = {}
        for arg, types in args.items():
            for t in types:
                if t not in entity_dict:
                    entity_dict[t] = [arg]
                else:
                    entity_dict[t].append(arg)
        return entity_dict

    # 解析主函数：把分类结果转成一组 cypher 语句
    def parser_main(self, res_classify: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        输入示例：
        {
            "args": {"感冒": ["disease"]},
            "question_types": ["disease_symptom"]
        }
        输出示例：
        [
            {
                "question_type": "disease_symptom",
                "sql": ["MATCH ... RETURN ...", ...]
            }
        ]
        """
        if not res_classify:
            return []

        args = res_classify.get("args", {})
        question_types = res_classify.get("question_types", [])
        if not args or not question_types:
            return []

        entity_dict = self.build_entitydict(args)

        sqls: List[Dict[str, Any]] = []
        for question_type in question_types:
            sql_item: Dict[str, Any] = {"question_type": question_type}

            # 按照不同的分类结果，组装不同的 cypher 查询语句
            if question_type in ("disease_symptom", "disease_food", "disease_drug"):
                # 目前这三类都只依赖疾病实体
                entities = entity_dict.get("disease")
                sql_list = self.sql_transfer(question_type, entities)
            else:
                # 其他类型暂不支持
                sql_list = []

            if sql_list:
                sql_item["sql"] = sql_list
                sqls.append(sql_item)

        return sqls

    # 针对不同的问题，分开进行处理
    def sql_transfer(self, question_type: str, entities: List[str]) -> List[str]:
        if not entities:
            return []

        # 查询语句列表
        sql: List[str] = []

        # 查询疾病有哪些症状
        if question_type == "disease_symptom":
            sql = [
                (
                    "MATCH (m:Disease)-[r:has_symptom]->(n:Symptom) "
                    "WHERE m.name = '{0}' "
                    "RETURN m.name, r.name, n.name"
                ).format(i)
                for i in entities
            ]

        # 查询疾病建议吃的东西
        elif question_type == "disease_food":
            sql = [
                (
                    "MATCH (m:Disease)-[r:recommand_eat]->(n:Food) "
                    "WHERE m.name = '{0}' "
                    "RETURN m.name, r.name, n.name"
                ).format(i)
                for i in entities
            ]

        # 查询疾病常用药品
        elif question_type == "disease_drug":
            sql = [
                (
                    "MATCH (m:Disease)-[r:recommand_drug]->(n:Drug) "
                    "WHERE m.name = '{0}' "
                    "RETURN m.name, r.name, n.name"
                ).format(i)
                for i in entities
            ]

        return sql


if __name__ == "__main__":
    qp = QuestionPaser()
    print(qp)

