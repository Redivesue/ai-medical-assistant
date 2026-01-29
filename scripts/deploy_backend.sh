#!/bin/bash

# 红蜘蛛AI医疗助手 - 后端部署脚本示例（本地/Render 前准备）

set -e

echo "======================================="
echo "  红蜘蛛AI医疗助手 - 后端部署脚本"
echo "======================================="

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

cd "$BACKEND_DIR"

echo "[1/3] 安装/更新依赖..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "[2/3] 运行 Neo4j 连接测试..."
python3 -c "from app.services.neo4j_client import test_connection; import sys; print('Neo4j test:', test_connection()); sys.exit(0)"

echo "[3/3] 本地启动服务 (开发模式)..."
echo "   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
echo "   健康检查: http://127.0.0.1:8000/health"
echo "   文档:     http://127.0.0.1:8000/docs"

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

