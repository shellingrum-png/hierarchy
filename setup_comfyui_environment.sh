#!/bin/bash
# ComfyUI 发型替换环境配置脚本

set -e

echo "========================================="
echo "    💇 AI 发型替换 - 环境配置工具"
echo "========================================="
echo ""

BASE_DIR=$(pwd)
COMFYUI_DIR="$BASE_DIR/ComfyUI"

# 检查 ComfyUI 目录已存在
if [ -d "$COMFYUI_DIR" ]; then
    echo "✅ ComfyUI 目录已存在"
else
    echo "📥 正在下载 ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git --depth 1
fi

# 进入 ComfyUI 目录
cd "$COMFYUI_DIR"

# 安装依赖
echo ""
echo "📦 安装 Python 依赖..."
python3 -m pip install torch torchvision torchaudio
python3 -m pip install -r requirements.txt

# 安装插件
echo ""
echo "🔌 安装插件..."
cd custom_nodes

if [ ! -d "ComfyUI_IPAdapter_plus" ]; then
    echo "  - IP-Adapter Plus"
    git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
fi

if [ ! -d "comfyui_controlnet_aux" ]; then
    echo "  - ControlNet Auxiliary Preprocessors"
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
fi

echo ""
echo "✅ 插件安装完成！"

# 创建模型目录（已存在会自动忽略）
cd ..
mkdir -p models/checkpoints models/ipadapter models/clip_vision models/controlnet models/vae

echo ""
echo "========================================="
echo "🎉 基础环境配置完成！"
echo "========================================="
echo ""
echo "📋 下一步："
echo ""
echo "1. 下载模型文件（参考 MODEL_DOWNLOAD_GUIDE.md）"
echo "2. 将模型放入对应的目录"
echo "3. 运行 ComfyUI："
echo "   cd ComfyUI && python main.py"
echo "4. 导入工作流：workflows/hairstyle_transfer_pro.json"
echo ""
echo "========================================="
