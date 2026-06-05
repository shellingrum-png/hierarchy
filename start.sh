#!/bin/bash
# 发型替换工具启动脚本

echo "========================================="
echo "    💇 AI 发型替换工具启动器"
echo "========================================="
echo ""

# 检查 Python
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "❌ Python 未找到，请先安装 Python"
    exit 1
fi

echo "✅ Python 已检测到"

# 检查依赖
echo ""
echo "📦 检查依赖..."

check_dependency() {
    $PYTHON -c "import $1" 2>/dev/null
}

# 检查 Flask
if check_dependency flask; then
    echo "  ✅ Flask 已安装"
else
    echo "  ⚠️  Flask 未安装，正在安装..."
    $PYTHON -m pip install flask
fi

echo ""
echo "请选择运行模式："
echo "1) 快速演示模式 (仅需 Pillow，快速体验)"
echo "2) 本地增强模式 (OpenCV + MediaPipe，效果更好)"
echo "3) ComfyUI 高级模式 (AI 生成，质量最佳)"
echo ""
read -p "请输入选项 (1/2/3): " mode

echo ""
echo "========================================="

case $mode in
    1)
        echo "🚀 启动快速演示模式..."
        echo "📱 请打开浏览器访问: http://localhost:5000"
        echo "========================================="
        cd server
        $PYTHON simple_server.py
        ;;
    2)
        echo "🚀 启动本地增强模式..."
        echo "⚠️  需要安装: opencv-python, mediapipe"
        echo "📱 请打开浏览器访问: http://localhost:5000"
        echo "========================================="
        cd server
        $PYTHON app_v2.py
        ;;
    3)
        echo "🚀 启动 ComfyUI 高级模式..."
        echo "⚠️  请确保 ComfyUI 已在 http://localhost:8188 运行"
        echo "📱 请打开浏览器访问: http://localhost:5000"
        echo "========================================="
        export PROCESSING_MODE=comfyui
        cd server
        $PYTHON app_v2.py
        ;;
    *)
        echo "❌ 无效选项，使用默认快速演示模式"
        echo "========================================="
        cd server
        $PYTHON simple_server.py
        ;;
esac
