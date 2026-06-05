#!/bin/bash
# =========================================
#    💇 AI 发型替换工具 - 腾讯云全自动部署
# =========================================
# 此脚本放在云服务器的 User Data 中，开机自动执行

set -x

# 日志输出
exec > /var/log/comfyui-deploy.log 2>&1

echo "[$(date)] 开始部署 ComfyUI 发型替换工具..."

# 1. 更新系统
apt update -y
apt upgrade -y

# 2. 安装 NVIDIA 驱动
echo "[$(date)] 安装 NVIDIA 驱动..."
apt install -y nvidia-driver-535 nvidia-cuda-toolkit

# 3. 安装基础依赖
echo "[$(date)] 安装系统依赖..."
apt install -y git python3-pip python3-venv nginx apache2-utils

# 4. 等待驱动生效（需要重启）
echo "[$(date)] 第一次配置完成，准备重启..."

# 创建重启后继续执行的脚本
cat > /root/continue-deploy.sh << 'EOF'
#!/bin/bash
set -x
exec > /var/log/comfyui-deploy-2.log 2>&1

echo "[$(date)] 重启后继续部署..."

cd /root

# 5. 克隆 ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git --depth 1
cd ComfyUI

# 6. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 7. 安装 PyTorch (CUDA 版本)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 8. 安装 ComfyUI 依赖
pip install -r requirements.txt

# 9. 安装插件
cd custom_nodes
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git

# 10. 下载模型（使用国内镜像加速）
cd ../models

# 基础模型
cd checkpoints
wget -q --show-progress https://hf-mirror.com/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors &

# IP-Adapter 模型
cd ../ipadapter
wget -q --show-progress https://hf-mirror.com/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors &

# CLIP Vision 模型
cd ../clip_vision
wget -q --show-progress https://hf-mirror.com/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors -O CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors &

# ControlNet 模型
cd ../controlnet
wget -q --show-progress https://hf-mirror.com/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth &
wget -q --show-progress https://hf-mirror.com/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth &

# 等待所有下载完成
wait

echo "[$(date)] 所有模型下载完成！"

# 11. 创建 Systemd 服务
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

# 12. 配置 Nginx 反向代理
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

# 13. 启用 Nginx 配置
ln -sf /etc/nginx/sites-available/comfyui /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

# 14. 启动服务
systemctl daemon-reload
systemctl enable comfyui
systemctl start comfyui

# 15. 配置防火墙
ufw allow 22/tcp
ufw allow 80/tcp
ufw --force enable

echo "========================================="
echo "✅ 部署完成！"
echo "========================================="
echo ""
echo "访问地址：http://$(curl -s ifconfig.me)"
echo ""
echo "查看服务状态：systemctl status comfyui"
echo "查看日志：journalctl -u comfyui -f"
echo "查看部署日志：cat /var/log/comfyui-deploy-2.log"
echo ""
echo "========================================="

EOF

chmod +x /root/continue-deploy.sh

# 添加开机自启（第二次启动时运行）
cat > /etc/rc.local << 'RC'
#!/bin/bash
if [ ! -f /root/.deploy-done ]; then
    bash /root/continue-deploy.sh
    touch /root/.deploy-done
fi
exit 0
RC
chmod +x /etc/rc.local

echo "[$(date)] 第一阶段完成，正在重启..."
reboot
