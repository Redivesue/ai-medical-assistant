import os
from typing import Dict, List

import ahocorasick


class QuestionClassifier:
    """
    问题分类子任务：
    - 根据用户问句中出现的疾病、症状、药品、食物等特征词 + 疑问词，
      将问句归类到红蜘蛛可支持的若干子类中，方便后续解析与答案搜索。
    """

    def __init__(self) -> None:
        cur_dir = os.path.dirname(os.path.abspath(__file__))

        # 特征词路径（注意：需要在 red_spider/dict/ 下准备好对应 txt 文件）
        self.disease_path = os.path.join(cur_dir, "dict", "disease.txt")
        self.drug_path = os.path.join(cur_dir, "dict", "drug.txt")
        self.food_path = os.path.join(cur_dir, "dict", "food.txt")
        self.symptom_path = os.path.join(cur_dir, "dict", "symptom.txt")

        # 加载特征词
        self.disease_words = [i.strip() for i in open(self.disease_path, encoding="utf-8") if i.strip()]
        self.drug_words = [i.strip() for i in open(self.drug_path, encoding="utf-8") if i.strip()]
        self.food_words = [i.strip() for i in open(self.food_path, encoding="utf-8") if i.strip()]
        self.symptom_words = [i.strip() for i in open(self.symptom_path, encoding="utf-8") if i.strip()]

        self.region_words = set(
            self.disease_words + self.drug_words + self.food_words + self.symptom_words
        )

        # 构造领域 actree，加速关键词匹配查找
        self.region_tree = self.build_actree(list(self.region_words))

        # 构建“词 -> 类型列表”的字典
        self.wdtype_dict = self.build_wdtype_dict()

        # 问句疑问词，V1.0 仅支持症状、食物、药品的查询
        self.symptom_request = [
            "症状",
            "表征",
            "现象",
            "症候",
            "表现",
            # 新增：
            "不适",
            "难受",
            "疼痛",
            "痛",
            "酸痛",
            "胀痛",
            "反应",
            "感觉",
            "迹象",
            "征兆",
            "体征",
            "病症",
            "病状",
            "毛病",
            "问题",
            "发作",
            "复发",
            "恶化",
            "加重",
            "并发症",
            "后遗症",
            "副作用",
            "异常",
            "不正常",
            "不舒服",
        ]
        self.food_request = [
            "饮食",
            "饮用",
            "吃",
            "食",
            "伙食",
            "膳食",
            "喝",
            "菜",
            "忌口",
            "补品",
            "保健品",
            "食谱",
            "菜谱",
            "食用",
            "食物",
            "补品",
            # 新增：
            "营养",
            "进食",
            "摄入",
            "饮食习惯",
            "餐",
            "水果",
            "蔬菜",
            "肉类",
            "海鲜",
            "主食",
            "零食",
            "小吃",
            "点心",
            "甜点",
            "禁忌",
            "宜吃",
            "能吃",
            "不能吃",
            "可以吃",
            "忌食",
            "禁食",
            "戒口",
            "忌讳",
            "营养品",
            "滋补品",
            "调理",
            "食补",
            "药膳",
            "饮料",
            "茶",
            "汤",
            "粥",
            "清淡",
            "辛辣",
            "油腻",
            "生冷",
            "配餐",
            "搭配",
            "料理",
        ]
        self.drug_request = [
            "药",
            "药品",
            "用药",
            "胶囊",
            "口服液",
            "炎片",
            # 新增：
            "药物",
            "medication",
            "处方",
            "非处方",
            "片剂",
            "颗粒",
            "冲剂",
            "糖浆",
            "喷雾",
            "注射",
            "针剂",
            "输液",
            "滴剂",
            "软膏",
            "贴剂",
            "中药",
            "西药",
            "汤药",
            "中成药",
            "消炎药",
            "止痛药",
            "退烧药",
            "抗生素",
            "服药",
            "吃药",
            "用药量",
            "药量",
            "剂量",
            "疗程",
            "停药",
            "换药",
            "配药",
            "副作用",
            "禁忌",
            "相互作用",
            "OTC",
            "处方药",
            "特效药",
            "常用药",
            "维生素",
            "钙片",
            "营养剂",
        ]

        print("QuestionClassifier model init finished ......")

    # 分类主函数
    def classify(self, question: str) -> Dict:
        data: Dict = {}

        medical_dict = self.check_medical(question)
        if not medical_dict:
            return {}

        data["args"] = medical_dict

        # 收集问句当中所涉及到的实体类型
        types: List[str] = []
        for type_list in medical_dict.values():
            types += type_list

        question_types: List[str] = []

        # 症状
        if self.check_words(self.symptom_request, question) and ("disease" in types):
            question_types.append("disease_symptom")

        # 推荐食物
        if self.check_words(self.food_request, question) and ("disease" in types):
            question_types.append("disease_food")

        # 推荐药品
        if self.check_words(self.drug_request, question) and ("disease" in types):
            question_types.append("disease_drug")

        # 若没有查到相关的外部查询信息，那么则将该疾病的描述信息返回
        if question_types == [] and "symptom" in types:
            question_types = ["disease_symptom"]

        # 组装成一个字典
        data["question_types"] = question_types
        return data

    # 构造关键词对应的节点类型
    def build_wdtype_dict(self) -> Dict[str, List[str]]:
        word_dict: Dict[str, List[str]] = {}
        for word in self.region_words:
            word_dict[word] = []

            # 检查是否有疾病关键词
            if word in self.disease_words:
                word_dict[word].append("disease")

            # 检查是否有药品关键词
            if word in self.drug_words:
                word_dict[word].append("drug")

            # 检查是否有食物关键词
            if word in self.food_words:
                word_dict[word].append("food")

            # 检查是否有症状关键词
            if word in self.symptom_words:
                word_dict[word].append("symptom")

        return word_dict

    # 构造 actree 加速过滤
    def build_actree(self, wordlist: List[str]):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    # 问句检查：识别问句里出现了哪些医疗相关实体
    def check_medical(self, question: str) -> Dict[str, List[str]]:
        region_words: List[str] = []

        # 利用 ac-tree 加速查询关键词
        for _, (_, word) in self.region_tree.iter(question):
            region_words.append(word)

        # 子词进入停用词表
        stop_words: List[str] = []
        for word1 in region_words:
            for word2 in region_words:
                if word1 in word2 and word1 != word2:
                    stop_words.append(word1)

        final_words = [i for i in region_words if i not in stop_words]
        final_dict = {i: self.wdtype_dict.get(i, []) for i in final_words}
        return final_dict

    # 基于特征词进行问句检测，并进行问句类型的规则分类
    def check_words(self, words: List[str], sent: str) -> bool:
        for word in words:
            if word in sent:
                return True
        return False


if __name__ == "__main__":
    qc = QuestionClassifier()
    while True:
        question = input("input a question: ")
        data = qc.classify(question)
        print(data)

