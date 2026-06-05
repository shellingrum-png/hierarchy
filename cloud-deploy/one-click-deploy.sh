#!/bin/bash
# =========================================
#    💇 AI 发型替换工具 - 一键部署脚本
# =========================================
# 使用方法：在服务器上运行：
# curl -s https://raw.githubusercontent.com/xxx/xxx/main/one-click-deploy.sh | bash
# 或者直接复制整个脚本到服务器运行

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; exit 1; }

echo ""
echo "========================================="
echo "    💇 AI 发型替换工具 - 一键部署"
echo "========================================="
echo ""

# 检查是否是 root
if [ "$EUID" -ne 0 ]; then 
    warn "建议使用 root 用户运行，否则部分命令需要 sudo"
fi

# 检查 Ubuntu
if [ ! -f /etc/os-release ] || ! grep -q "Ubuntu" /etc/os-release; then
    error "此脚本只支持 Ubuntu 系统"
fi

log "开始部署，请耐心等待..."
echo ""

# 1. 更新系统
log "[1/7] 更新系统..."
apt update -y > /dev/null 2>&1

# 2. 安装 NVIDIA 驱动
log "[2/7] 安装 NVIDIA 驱动（大约 5-10 分钟）..."
if ! command -v nvidia-smi &> /dev/null; then
    apt install -y nvidia-driver-535 nvidia-cuda-toolkit -qq > /dev/null 2>&1
    log "驱动安装完成！"
else
    log "检测到 NVIDIA 驱动已安装"
    nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits | head -1
fi

# 3. 安装基础依赖
log "[3/7] 安装系统依赖..."
apt install -y git python3-pip python3-venv nginx -qq > /dev/null 2>&1

# 4. 克隆 ComfyUI
log "[4/7] 下载 ComfyUI..."
cd /root
if [ -d "ComfyUI" ]; then
    warn "ComfyUI 目录已存在，跳过"
else
    git clone https://github.com/comfyanonymous/ComfyUI.git --depth 1 -q
fi

# 5. 安装 Python 依赖
log "[5/7] 安装 Python 依赖..."
cd ComfyUI
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

log "安装 PyTorch (CUDA)..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 -q > /dev/null 2>&1

log "安装 ComfyUI 依赖..."
pip install -r requirements.txt -q > /dev/null 2>&1

# 6. 安装插件
log "[6/7] 安装插件..."
cd custom_nodes

if [ ! -d "ComfyUI_IPAdapter_plus" ]; then
    git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git -q
fi
if [ ! -d "comfyui_controlnet_aux" ]; then
    git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git -q
fi

# 7. 下载模型
log "[7/7] 下载模型（后台并行下载中）..."
cd ../models

# 基础模型
cd checkpoints
if [ ! -f "v1-5-pruned-emaonly.safetensors" ]; then
    wget -q -c "https://hf-mirror.com/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors" &
fi

# IP-Adapter
cd ../ipadapter
if [ ! -f "ip-adapter-plus_sd15.safetensors" ]; then
    wget -q -c "https://hf-mirror.com/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors" &
fi

# CLIP Vision
cd ../clip_vision
if [ ! -f "CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors" ]; then
    wget -q -c "https://hf-mirror.com/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors" -O CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors &
fi

# ControlNet
cd ../controlnet
if [ ! -f "control_v11p_sd15_openpose.pth" ]; then
    wget -q -c "https://hf-mirror.com/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth" &
fi
if [ ! -f "control_v11p_sd15_canny.pth" ]; then
    wget -q -c "https://hf-mirror.com/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth" &
fi

# 8. 配置服务
log "配置 Systemd 服务..."
cat > /etc/systemd/system/comfyui.service << 'SVC'
[Unit]
Description=ComfyUI Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ComfyUI
Environment="PATH=/root/ComfyUI/venv/bin"
ExecStart=/root/ComfyUI/venv/bin/python main.py --listen 127.0.0.1 --port 8188
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVC

# 9. 配置 Nginx
log "配置 Nginx 反向代理..."
cat > /etc/nginx/sites-available/comfyui << 'NGX'
server {
    listen 80;
    server_name _;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8188;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_buffering off;
        proxy_cache_bypass $http_upgrade;
        
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
NGX

ln -sf /etc/nginx/sites-available/comfyui /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t > /dev/null 2>&1
systemctl restart nginx

# 10. 启动服务
log "启动 ComfyUI 服务..."
systemctl daemon-reload
systemctl enable comfyui
systemctl start comfyui

# 配置防火墙
ufw allow 22/tcp > /dev/null 2>&1
ufw allow 80/tcp > /dev/null 2>&1
ufw --force enable > /dev/null 2>&1

# 获取公网 IP
PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || echo "你的服务器IP")

echo ""
echo "========================================="
echo -e "✅ ${GREEN}部署完成！${NC}"
echo "========================================="
echo ""
echo "🌐 访问地址：http://$PUBLIC_IP"
echo ""
echo "📋 常用命令："
echo "   查看状态：systemctl status comfyui"
echo "   查看日志：journalctl -u comfyui -f"
echo "   重启服务：systemctl restart comfyui"
echo ""
echo "📦 模型正在后台下载，请等待 5-10 分钟后再使用"
echo "   查看下载进度：ls -lh /root/ComfyUI/models/*/"
echo ""
echo "🎨 工作流文件路径：/root/ComfyUI/workflows/"
echo ""
echo "========================================="

# 上传工作流文件
mkdir -p /root/ComfyUI/workflows
