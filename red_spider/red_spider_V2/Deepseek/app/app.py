import os
import sys
import time

from flask import Flask, request, jsonify
from flask_cors import CORS

# ---------------------------------------------------------------------------
# 路径处理：确保可以导入 Deepseek 下的 robot.Red_Spider
# ---------------------------------------------------------------------------
CURRENT_DIR = os.path.dirname(__file__)                 # .../Deepseek/app
DEEPSEEK_DIR = os.path.dirname(CURRENT_DIR)            # .../Deepseek
PROJECT_ROOT = os.path.dirname(os.path.dirname(DEEPSEEK_DIR))  # .../red_spider

for p in (DEEPSEEK_DIR, PROJECT_ROOT):
    if p not in sys.path:
        sys.path.append(p)

from red_spider.red_spider_V2.Deepseek.robot import Red_Spider  # type: ignore


app = Flask(__name__)
CORS(app)


# ---------------------------------------------------------------------------
# 初始化 DeepSeek 版红蜘蛛机器人
# ---------------------------------------------------------------------------
print("初始化 DeepSeek 版红蜘蛛......")
start_time = time.time()

# flag 固定为 'deepseek'，model_path 只是为了接口一致，这里可以为 None
red_spider = Red_Spider(flag="deepseek", model_path=None)

end_time = time.time()
print("DeepSeek 红蜘蛛初始化耗时: {:.2f}s".format(end_time - start_time))


@app.route("/v1/main_server/", methods=["GET", "POST"])
def main_server():
    # GET：返回简单的使用说明
    if request.method == "GET":
        return jsonify(
            {
                "code": 200,
                "message": "红蜘蛛AI服务（DeepSeek版）API",
                "usage": {
                    "method": "POST",
                    "url": "/v1/main_server/",
                    "content_type": "application/x-www-form-urlencoded 或 application/json",
                    "parameters": {
                        "uid": "用户ID（可选）",
                        "text": "问题文本（必填）",
                    },
                },
            }
        )

    # POST：处理对话请求
    try:
        if request.is_json:
            data = request.get_json() or {}
            uid = data.get("uid", "")
            text = data.get("text", "")
        else:
            uid = request.form.get("uid", "")
            text = request.form.get("text", "")

        if not text:
            return (
                jsonify(
                    {
                        "code": 400,
                        "message": "请求参数错误: text 字段不能为空",
                        "data": None,
                    }
                ),
                400,
            )

        answer = red_spider.chat_main(text)

        return (
            jsonify(
                {
                    "code": 200,
                    "message": "success",
                    "data": {"uid": uid, "answer": answer},
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify(
                {
                    "code": 500,
                    "message": f"服务器内部错误: {str(e)}",
                    "data": None,
                }
            ),
            500,
        )


@app.route("/health", methods=["GET"])
def health():
    return jsonify(
        {
            "code": 200,
            "message": "红蜘蛛AI DeepSeek 版服务运行正常",
            "status": "healthy",
        }
    )


@app.route("/", methods=["GET"])
def index():
    # 复用 V1 中的前端风格，但调用的是本服务的 /v1/main_server/
    html = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>红蜘蛛AI医疗问答机器人（DeepSeek版）</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #ff5e62;
            text-align: center;
            margin-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: bold;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        button {
            background: linear-gradient(135deg, #ff9966 0%, #ff5e62 100%);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
        }
        .answer-box {
            margin-top: 20px;
            padding: 20px;
            background: #f5f5f5;
            border-radius: 8px;
            border-left: 4px solid #ff5e62;
            min-height: 50px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .loading {
            text-align: center;
            color: #ff5e62;
            font-style: italic;
        }
        .error {
            color: #e74c3c;
            background: #ffe6e6;
            border-left-color: #e74c3c;
        }
        .examples {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #eee;
        }
        .example-btn {
            display: inline-block;
            margin: 5px;
            padding: 8px 15px;
            background: #f0f0f0;
            border: 1px solid #ddd;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .example-btn:hover {
            background: #e0e0e0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🕷️ 红蜘蛛AI医疗问答（DeepSeek版）</h1>
        <p class="subtitle">规则+知识图谱优先，DeepSeek 大模型兜底</p>
        
        <div class="input-group">
            <label for="question">请输入您的问题：</label>
            <textarea id="question" placeholder="例如：最近总是失眠怎么办？"></textarea>
        </div>
        
        <button onclick="askQuestion()">提问</button>
        
        <div id="answer" class="answer-box" style="display:none;"></div>
        
        <div class="examples">
            <h3>示例问题：</h3>
            <button class="example-btn" onclick="setQuestion('感冒的症状是什么？')">感冒的症状</button>
            <button class="example-btn" onclick="setQuestion('高血压应该吃什么药？')">高血压用药</button>
            <button class="example-btn" onclick="setQuestion('最近总是睡不着，有什么建议？')">失眠建议</button>
            <button class="example-btn" onclick="setQuestion('头痛可能是什么病？')">头痛相关</button>
        </div>
    </div>

    <script>
        function setQuestion(text) {
            document.getElementById('question').value = text;
        }

        async function askQuestion() {
            const question = document.getElementById('question').value.trim();
            const answerDiv = document.getElementById('answer');
            
            if (!question) {
                answerDiv.className = 'answer-box error';
                answerDiv.textContent = '请输入您的问题！';
                answerDiv.style.display = 'block';
                return;
            }
            
            answerDiv.className = 'answer-box loading';
            answerDiv.textContent = 'DeepSeek 正在思考中，请稍候...';
            answerDiv.style.display = 'block';
            
            try {
                const formData = new FormData();
                formData.append('uid', 'deepseek_web_user');
                formData.append('text', question);
                
                const response = await fetch('/v1/main_server/', {
                    method: 'POST',
                    body: formData
                });
                
                const data = await response.json();
                
                if (data.code === 200 && data.data) {
                    answerDiv.className = 'answer-box';
                    answerDiv.textContent = data.data.answer;
                } else {
                    answerDiv.className = 'answer-box error';
                    answerDiv.textContent = data.message || '获取答案失败';
                }
            } catch (error) {
                answerDiv.className = 'answer-box error';
                answerDiv.textContent = '请求失败: ' + error.message;
            }
        }

        // Ctrl+Enter 提交
        document.getElementById('question').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                askQuestion();
            }
        });
    </script>
</body>
</html>
"""
    return html


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5010))
    print(f"启动红蜘蛛 DeepSeek 版服务，端口: {port}")
    print(f"API 地址: http://localhost:{port}/v1/main_server/")
    app.run(host="0.0.0.0", port=port, debug=True)

