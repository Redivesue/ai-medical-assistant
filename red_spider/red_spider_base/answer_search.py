from typing import List, Dict, Any

from neo4j import GraphDatabase

from config import NEO4J_CONFIG


# 答案搜索的主类
class AnswerSearcher:
    def __init__(self) -> None:
        # 单个回答中最多展示的条目数
        self.num_limit = 10
        # 复用和其他模块相同的 Neo4j 配置
        self.driver = GraphDatabase.driver(**NEO4J_CONFIG)

    # 执行 cypher 查询，并返回相应结果
    def search_main(self, sqls: List[Dict[str, Any]]) -> List[str]:
        """
        sqls 示例：
        [
            {
                "question_type": "disease_symptom",
                "sql": ["MATCH ... RETURN m.name, r.name, n.name", ...]
            },
            ...
        ]
        """
        final_answers: List[str] = []

        if not sqls:
            return final_answers

        with self.driver.session() as session:
            for sql_ in sqls:
                question_type = sql_.get("question_type")
                queries = sql_.get("sql", [])
                if not queries:
                    continue

                answers: List[Dict[str, Any]] = []

                # 遍历所有的查询 cypher，依次执行，并将结果逐个添加进列表中
                for query in queries:
                    ress = session.run(query).data()
                    answers += ress

                # 调用精准回复模板
                final_answer = self.answer_prettify(question_type, answers)
                if final_answer:
                    final_answers.append(final_answer)

        return final_answers

    # 根据对应的 question_type，调用相应的回复模板
    def answer_prettify(self, question_type: str, answers: List[Dict[str, Any]]) -> str:
        if not answers:
            return ""

        # 注意：这里依赖于 Cypher 中的 RETURN m.name, r.name, n.name
        # Neo4j Python 驱动默认的键名为 'm.name' / 'r.name' / 'n.name'

        # 查询疾病有哪些症状
        if question_type == "disease_symptom":
            desc = [i["n.name"] for i in answers if "n.name" in i]
            if not desc:
                return ""
            subject = answers[0].get("m.name", "")
            if not subject:
                return ""
            uniq_desc = list(set(desc))[: self.num_limit]
            return "{}的症状包括: {}".format(subject, "；".join(uniq_desc))

        # 查询疾病建议吃的东西
        if question_type == "disease_food":
            desc = [i["n.name"] for i in answers if "n.name" in i]
            if not desc:
                return ""
            subject = answers[0].get("m.name", "")
            if not subject:
                return ""
            uniq_desc = list(set(desc))[: self.num_limit]
            return "{}推荐饮食/食谱包括: {}".format(subject, "；".join(uniq_desc))

        # 查询疾病常用药品
        if question_type == "disease_drug":
            desc = [i["n.name"] for i in answers if "n.name" in i]
            if not desc:
                return ""
            subject = answers[0].get("m.name", "")
            if not subject:
                return ""
            uniq_desc = list(set(desc))[: self.num_limit]
            return "{}常用/推荐药品包括: {}".format(subject, "；".join(uniq_desc))

        # 其他类型暂未定义模板
        return ""


if __name__ == "__main__":
    ans = AnswerSearcher()
    print(ans)

