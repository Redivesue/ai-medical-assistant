import os
import sys
from typing import Optional

from deepsk import DS_RedSpider

# 为了能在 Deepseek 模块中统一调用其它模型，这里适当调整 sys.path
CURRENT_DIR = os.path.dirname(__file__)              # .../red_spider_V2/Deepseek
V2_ROOT = os.path.dirname(CURRENT_DIR)               # .../red_spider_V2

if V2_ROOT not in sys.path:
    sys.path.append(V2_ROOT)

try:
    from gpt_module.gpt2 import GPT2_RedSpider
except Exception:
    GPT2_RedSpider = None

try:
    from config import *  # 如果有需要的全局配置，可在此导入
except Exception:
    pass


class ChatGPT:
    """
    统一的生成式回复封装类，支持多种模型：
    - flag='gpt2'      → 使用 GPT2_RedSpider
    - flag='yuyuan'    → 使用 Yuyuan_RedSpider（余元大模型）
    - flag='intern'    → 使用 InternLM_RedSpider（InternLM3-8B）
    - flag='qwen'      → 使用 Qwen_RedSpider（Qwen2.5-0.5B-Instruct，轻量版）
    - flag='qwen1.5B'  → 使用 Qwen_RedSpider（Qwen2.5-1.5B-Instruct，qwen1.5B）
    - flag='deepseek'  → 使用 DS_RedSpider（DeepSeek 大模型 API）
    """

    def __init__(self, flag: str = "deepseek", model_path: str = "./pretrain_model", api_key: Optional[str] = None):
        """
        参数
        ----
        flag : str
            模型类型标识：
            - 'gpt2'      : 使用 GPT2 模型
            - 'yuyuan'    : 使用 YuyuanQA-GPT2-3.5B 模型
            - 'intern'    : 使用 InternLM3-8B-Instruct-AWQ 模型
            - 'qwen'      : 使用 Qwen2.5-0.5B-Instruct 模型
            - 'qwen1.5B'  : 使用 Qwen2.5-1.5B-Instruct 模型
            - 'deepseek'  : 使用 DeepSeek API 服务
        model_path : str
            本地模型父目录路径，例如 "./pretrain_model"。
        api_key : str or None
            DeepSeek 的 API Key；如果不传，则从环境变量 DEEPSEEK_API_KEY 读取。
        """
        self.flag = flag

        # GPT2
        if flag == "gpt2":
            if GPT2_RedSpider is None:
                raise ImportError("GPT2_RedSpider 未找到，请检查 gpt_module/gpt2.py 是否存在")
            self.generator = GPT2_RedSpider(model_path)

        # 余元
        elif flag == "yuyuan":
            if Yuyuan_RedSpider is None:
                raise ImportError("Yuyuan_RedSpider 未找到，请检查 yuyuan_model/yuyuan.py 是否存在")
            self.generator = Yuyuan_RedSpider(model_path=model_path)

        # InternLM
        elif flag == "intern":
            if InternLM_RedSpider is None:
                raise ImportError("InternLM_RedSpider 未找到，请检查 InternLM/intern.py 是否存在")
            self.generator = InternLM_RedSpider(model_path=model_path)

        # Qwen 0.5B 轻量版
        elif flag == "qwen":
            if Qwen05B_RedSpider is None:
                raise ImportError("Qwen_RedSpider(0.5B) 未找到，请检查 qwen25/qwen.py 是否存在")
            self.generator = Qwen05B_RedSpider(model_path=model_path)

        # Qwen 1.5B 加强版
        elif flag == "qwen1.5B":
            if Qwen15B_RedSpider is None:
                raise ImportError("Qwen_RedSpider(1.5B) 未找到，请检查 qwen25/qwen1.5B/qwen1.5B.py 是否存在")
            self.generator = Qwen15B_RedSpider(model_path=model_path)

        # DeepSeek 服务
        elif flag == "deepseek":
            # 如果外部没有显式传入 api_key，则让 DS_RedSpider 使用其默认逻辑
            if api_key is None:
                self.generator = DS_RedSpider()
            else:
                self.generator = DS_RedSpider(api_key=api_key)

        else:
            raise ValueError(
                f"不支持的 flag='{flag}'。\n"
                f"支持的选项：'gpt2', 'yuyuan', 'intern', 'qwen', 'qwen1.5B', 'deepseek'"
            )

    def chat(self, prompt: str) -> str:
        res = self.generator.chat(prompt)
        return res


