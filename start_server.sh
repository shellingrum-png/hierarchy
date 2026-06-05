#!/bin/bash
# 发型替换工具启动脚本

echo "========================================="
echo "    💇 AI 发型替换工具启动器"
echo "========================================="
echo ""

# 检查 Python 是否安装
if ! command -v python &> /dev/null; then
    echo "❌ Python 未找到，请先安装 Python"
    exit 1
fi

# 检查依赖是否安装
echo "📦 检查依赖..."
python -c "import flask" 2>/dev/null || {
    echo "🔧 安装 Python 依赖..."
    pip install -r requirements.txt
}

echo ""
echo "请选择运行模式："
echo "1) 本地演示模式 (快速体验，不需要 ComfyUI)"
echo "2) ComfyUI 高级模式 (需要运行 ComfyUI)"
echo ""
read -p "请输入选项 (1/2): " mode

case $mode in
    1)
        echo ""
        echo "🚀 启动本地演示模式..."
        export PROCESSING_MODE=local
        ;;
    2)
        echo ""
        echo "🚀 启动 ComfyUI 高级模式..."
        export PROCESSING_MODE=comfyui
        echo "⚠️  请确保 ComfyUI 已在 http://localhost:8188 运行"
        ;;
    *)
        echo "❌ 无效选项，使用默认本地模式"
        export PROCESSING_MODE=local
        ;;
esac

echo ""
echo "========================================="
echo "🌐 服务器启动中..."
echo "📱 请打开浏览器访问: http://localhost:5000"
echo "========================================="
echo ""

cd server
python app_v2.py
