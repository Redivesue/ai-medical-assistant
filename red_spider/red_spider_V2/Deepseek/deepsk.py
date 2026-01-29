import os
from typing import Optional

from openai import OpenAI


class DS_RedSpider:
    """
    DeepSeek 大模型红蜘蛛封装：
    - 默认使用 deepseek-chat 模型
    - 通过 OpenAI 兼容接口访问 DeepSeek (`https://api.deepseek.com`)
    - API Key 建议通过环境变量 `DEEPSEEK_API_KEY` 提供
    """

    def __init__(
        self,
        api_key: Optional[str] ="sk-b5483765b3a045a196e09f8d2b3d1ae3" ,
        base_url: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
    ) -> None:
        """
        参数
        ----
        api_key : Optional[str]
            DeepSeek 的 API Key。优先顺序：
            1. 显式传入的 api_key
            2. 环境变量 DEEPSEEK_API_KEY
        base_url : str
            DeepSeek 的 API Base URL，默认为 "https://api.deepseek.com"。
        model : str
            使用的 DeepSeek 模型名称，默认 "deepseek-chat"。
        """
        # 优先使用传入的 api_key，否则从环境变量读取
        api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError(
                "未提供 DeepSeek API Key。\n"
                "请在初始化 DS_RedSpider(api_key=...) 传入，"
                "或在环境变量中设置 DEEPSEEK_API_KEY。"
            )

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

        print(f"已初始化 DeepSeek 客户端，使用模型：{self.model}")

    def chat(self, prompt: str) -> str:
        """
        调用 DeepSeek 生成回复。
        """
        if not prompt:
            return ""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                # 如需使用推理增强模型，可切换为 "deepseek-reasoner"
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个非常专业且贴心的中文医疗问答助手，需要结合医学常识和生活建议，给出温和、易懂的回答。",
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                stream=False,
            )
        except Exception as e:
            return f"调用 DeepSeek 接口失败：{e}"

        # 兼容 OpenAI 风格返回
        try:
            return response.choices[0].message.content
        except Exception:
            return str(response)


