#!/bin/bash
# ComfyUI 及相关插件一键安装脚本

echo "========================================="
echo "    ComfyUI 环境一键安装脚本"
echo "========================================="
echo ""

BASE_DIR=$(pwd)
COMFYUI_DIR="$BASE_DIR/ComfyUI"

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "❌ Git 未找到，请先安装 Git"
    exit 1
fi

# 克隆 ComfyUI
if [ ! -d "$COMFYUI_DIR" ]; then
    echo "📥 克隆 ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git
else
    echo "✅ ComfyUI 已存在"
fi

# 安装 ComfyUI 依赖
echo "🔧 安装 ComfyUI 依赖..."
cd "$COMFYUI_DIR"
pip install -r requirements.txt

# 安装插件
echo "📦 安装插件..."
cd custom_nodes

# IP-Adapter Plus
if [ ! -d "ComfyUI_IPAdapter_plus" ]; then
    echo "  - IPAdapter Plus"
    git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
fi

# ControlNet Preprocessors
if [ ! -d "comfy_controlnet_preprocessors" ]; then
    echo "  - ControlNet Preprocessors"
    git clone https://github.com/Fannovel16/comfy_controlnet_preprocessors.git
fi

echo ""
echo "========================================="
echo "✅ 安装完成！"
echo ""
echo "下一步操作："
echo "1. 下载必要的模型文件"
echo "2. 启动 ComfyUI: cd ComfyUI && python main.py"
echo "3. 导入工作流: workflows/hairstyle_transfer.json"
echo "========================================="
