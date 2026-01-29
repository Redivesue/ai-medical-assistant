#!/bin/bash

# 红蜘蛛AI医疗助手 - 本地启动脚本
# 功能：
#   1. 检查并安装 Python 依赖
#   2. 启动 FastAPI 服务（uvicorn）
#   3. 自动打开浏览器访问首页（可选）

set -e  # 遇到错误立即退出

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  红蜘蛛AI医疗助手 - 本地启动脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 获取脚本所在目录（backend 目录）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${YELLOW}[1/3] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}错误：未找到 python3，请先安装 Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo -e "${GREEN}✓ Python 版本: $(python3 --version)${NC}"

echo ""
echo -e "${YELLOW}[2/3] 安装/更新依赖...${NC}"
if [ -f "requirements.txt" ]; then
    python3 -m pip install --upgrade pip -q
    python3 -m pip install -r requirements.txt
    echo -e "${GREEN}✓ 依赖安装完成${NC}"
else
    echo -e "${RED}错误：未找到 requirements.txt${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[3/3] 启动 FastAPI 服务...${NC}"
echo -e "${GREEN}服务地址: http://127.0.0.1:8000${NC}"
echo -e "${GREEN}健康检查: http://127.0.0.1:8000/health${NC}"
echo -e "${GREEN}API 文档: http://127.0.0.1:8000/docs${NC}"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止服务${NC}"
echo ""

# 检查是否设置了 DEEPSEEK_API_KEY
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  提示：未检测到 DEEPSEEK_API_KEY 环境变量${NC}"
    echo -e "${YELLOW}   如需使用 DeepSeek 功能，请设置：${NC}"
    echo -e "${YELLOW}   export DEEPSEEK_API_KEY='your-api-key'${NC}"
    echo ""
fi

# 启动 uvicorn
# --reload: 开发模式，代码变更自动重启
# --host 0.0.0.0: 允许外部访问（可选，本地开发可改为 127.0.0.1）
# --port 8000: 端口号
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
