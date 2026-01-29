from question_classifier import QuestionClassifier
from question_parser import QuestionPaser
from answer_search import AnswerSearcher


# 红蜘蛛机器人综合问答类
class Red_Spider:
    def __init__(self) -> None:
        # 1: 问题分类器
        self.classifier = QuestionClassifier()
        # 2: 问题解析器
        self.parser = QuestionPaser()
        # 3: 答案搜索器
        self.searcher = AnswerSearcher()

    def chat_main(self, sentence: str) -> str:
        # 默认客套回答
        answer = "您好，我是红蜘蛛 AI 助理，希望可以帮到您，祝您身体安康，快乐常伴~"

        if not sentence or not sentence.strip():
            return answer

        # 1: 首先进⾏问题分类，如果无法分类到症状、食物、药品相关问题上，则直接返回客套话
        res_classify = self.classifier.classify(sentence)
        if not res_classify:
            return answer

        # 2: 对分类后的问题进行解析，组装出 neo4j 查询语句
        res_sql = self.parser.parser_main(res_classify)
        if not res_sql:
            return answer

        # 3: 利用查询语句，调用答案搜索器查询 neo4j，得到最终答案
        final_answers = self.searcher.search_main(res_sql)

        # 无法查询到相关答案，则返回客套话；否则将若干答案分行返回
        if not final_answers:
            return answer
        else:
            return "\n".join(final_answers)


if __name__ == "__main__":
    # 实例化红蜘蛛机器人
    red_spider = Red_Spider()

    # 无限循环多轮对话
    while True:
        try:
            question = input("用户: ")
        except (EOFError, KeyboardInterrupt):
            print("\n红蜘蛛: 再见，祝您身体健康！")
            break

        # 退出指令
        if question in ("Q", "q", "退出", "再见", "bye", "Bye", "quit", "exit"):
            print("红蜘蛛: 再见，祝您身体健康！")
            break

        answer = red_spider.chat_main(question)
        print("红蜘蛛:", answer)

