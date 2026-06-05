#!/bin/bash
# ComfyUI 启动脚本（虚拟环境版本）

echo "========================================="
echo "    💇 AI 发型替换工具 - ComfyUI"
echo "========================================="
echo ""

cd ComfyUI

# 激活虚拟环境
source venv/bin/activate

echo "✅ 虚拟环境已激活"
echo ""
echo "🚀 正在启动 ComfyUI..."
echo "🌐 请打开浏览器访问：http://127.0.0.1:8188"
echo ""
echo "💡 导入工作流："
echo "   点击 Load 按钮，选择 ../workflows/hairstyle_transfer_pro.json"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================="
echo ""

python main.py --listen 127.0.0.1 --port 8188
