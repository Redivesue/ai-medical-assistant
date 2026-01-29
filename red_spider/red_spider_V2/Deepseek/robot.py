import os
import sys
import time
from typing import Optional

from chat_gpt import ChatGPT

# ---------------------------------------------------------------------------
# 云端路径配置（仅有 Deepseek 和 red_spider_base 两个目录）
#
# 当前文件路径（云端）大致为：
#   /workspace/
#       ├── Deepseek/
#       │     └── robot.py （当前文件）
#       └── red_spider_base/
#             ├── question_classifier.py
#             ├── question_parser.py
#             └── answer_search.py
# ---------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(__file__)           # .../red_spider/red_spider_V2/Deepseek 或 /workspace/Deepseek
REPO_ROOT = os.path.dirname(CURRENT_DIR)         # 本地: .../red_spider/red_spider_V2；云端: .../workspace

# 同时兼容两种目录结构：
# 1) 云端：  /workspace/
#          ├── Deepseek/
#          └── red_spider_base/
# 2) 本地： /Users/.../red_spider/
#          ├── red_spider_base/
#          └── red_spider_V2/Deepseek/
BASE_DIR_CLOUD = os.path.join(REPO_ROOT, "red_spider_base")
PROJECT_ROOT = os.path.dirname(REPO_ROOT)
BASE_DIR_LOCAL = os.path.join(PROJECT_ROOT, "red_spider_base")

for base_dir in (BASE_DIR_CLOUD, BASE_DIR_LOCAL):
    if os.path.isdir(base_dir) and base_dir not in sys.path:
        sys.path.append(base_dir)

from question_classifier import QuestionClassifier
from question_parser import QuestionPaser
from answer_search import AnswerSearcher


class Red_Spider:
    """
    红蜘蛛 V2 综合问答机器人（使用 DeepSeek 大模型 API）：
    - 首选使用规则+知识图谱（分类 → 解析 → Neo4j 检索）
    - 如果任一阶段失败，则回退到生成式模型（DeepSeek）
    """

    def __init__(self, flag: str = "deepseek", model_path: Optional[str] = None):
        # 1: 问题分类器
        print("初始化 QuestionClassifier ......")
        self.classifier = QuestionClassifier()

        # 2: 问题解析器
        print("初始化 QuestionParser ......")
        self.parser = QuestionPaser()

        # 3: 答案搜索器
        print("初始化 AnswerSearcher ......")
        self.searcher = AnswerSearcher()

        # 4: 生成回复模块（LLM，使用 DeepSeek）
        print("初始化 ChatGPT (生成式模块, DeepSeek) ......")
        # Deepseek/chat_gpt.py 中的 ChatGPT 期望 flag='deepseek'
        # api_key 默认从环境变量 DEEPSEEK_API_KEY 读取
        self.generator = ChatGPT(flag=flag, model_path=model_path or "./pretrain_model")

        # 开幕词
        self.answer = "您好, 我是红蜘蛛AI助理（DeepSeek 版）, 希望可以帮到您, 祝您身体安康, 快乐常伴~"
        print(self.answer)

    def chat_main(self, sentence: str) -> str:
        """
        单轮对话主逻辑：
        1) 使用规则+知识图谱查询
        2) 任一阶段失败则回退到生成式模型（DeepSeek）
        """
        # 1: 首先进行问题分类
        res_classify = self.classifier.classify(sentence)

        # 如果无法分类到症状、食品、药品等相关问题上，则进入 LLM 生成
        if not res_classify:
            return self.generator.chat(sentence)

        # 2: 对分类后的问题进行解析, 组装成 neo4j 查询语句
        res_sql = self.parser.parser_main(res_classify)

        # 解析失败（没有有效 Cypher），同样进入生成模型回复逻辑
        if not res_sql:
            return self.generator.chat(sentence)

        # 3: 利用查询语句, 调用答案搜索器查询 neo4j, 得到最终答案
        final_answers = self.searcher.search_main(res_sql)

        # 无法查询到相关答案时, 则返回生成式模型的回复, 否则将若干答案分行返回
        if not final_answers:
            return self.generator.chat(sentence)
        return "\n".join(final_answers)


if __name__ == '__main__':
    # 实例化红蜘蛛机器人
    print('初始化AI红蜘蛛......')
    start_time = time.time()
    flag = 'deepseek'

    # 对 DeepSeek 来说，model_path 主要用于与其它本地模型保持接口一致，这里可以忽略
    model_path = './pretrain_model'

    red_spider = Red_Spider(flag, model_path)
    end_time = time.time()
    print('初始化耗时{}s'.format(end_time - start_time))

    # 无限循环多轮对话
    while True:
        question = input('用户:')
        if question in ('Q', 'q'):
            break
        answer = red_spider.chat_main(question)
        print('AI红蜘蛛:', answer)
        print('\n')

