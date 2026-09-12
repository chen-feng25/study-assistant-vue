#!/bin/bash
echo ""
echo "  [学习档案助理] 启动中..."
echo "  =============================="
echo ""

cd "$(dirname "$0")"

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "  [X] 未检测到 Python，请先安装 Python 3.9+"
    echo "  [>] 下载地址: https://www.python.org/downloads/"
    exit 1
fi

PYTHON=$(command -v python3 || command -v python)

# Check dependencies
$PYTHON -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "  [.] 正在安装依赖..."
    $PYTHON -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "  [X] 依赖安装失败，请手动运行: pip install -r requirements.txt"
        exit 1
    fi
    echo "  [OK] 依赖安装完成"
    echo ""
fi

echo "  [>>] 启动服务，请手动打开 http://127.0.0.1:8501"
echo "  [STOP] 按 Ctrl+C 停止服务"
echo ""

$PYTHON server.py
