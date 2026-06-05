# 🚀 ComfyUI 发型替换工具 - 完整部署指南

## 📋 项目概述

基于 ComfyUI + IP-Adapter + ControlNet 的智能发型替换工具，支持上传人脸照片和发型参考图，AI 自动完成发型替换。

## 🎯 功能特性

- 👤 上传人脸照片
- 💇 上传发型参考图
- ✨ IP-Adapter 特征迁移
- 🎭 ControlNet 姿态保持
- 🖼️ 前端交互界面

---

## 🖥️ 环境要求

### 服务器配置
- **系统**: Ubuntu 22.04 LTS / CentOS 7+ / OpenCloudOS
- **CPU**: 8核以上
- **内存**: 16GB+
- **GPU**: NVIDIA T4/RTX 3090/A10 等（推荐，CPU 也能跑但很慢）
- **硬盘**: 50GB+ 可用空间

### 本地环境
- Python 3.10+
- Git
- 浏览器（Chrome/Firefox/Safari）

---

## 📦 快速部署

### 方式一：Ubuntu 一键部署脚本

```bash
# 1. SSH 登录服务器
ssh root@你的服务器IP

# 2. 执行一键部署（复制下面整段）
base64 -d <<< 'IyEvYmluL2Jhc2gKIyA9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KCiMgICAgIPCfkocgQUkg5Y+R5Z6L5pu/5o2i5bel5YW3IC0g5LiA6ZSu6YOo572yCiMgICAyDvUugSu5piv56S+5LqR5Y+R5pu/5a2Q6YOo6K6/5LqRCiMgPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0KCnNldCAtZQoKIyDpopzoibLovpPlh7oKUkVEPSdcMDMzWzA7MzFtJwpHSkVFTj0nXDAzM1swOzMybScKWUVMTE9XPSdcMDMzWzE7MzNtJwpOQz0nXDAzM1swbScKCmxvZygpIHsgZWNobyAtZSAiJHtHUkVFTn1bJChkYXRlICcrJUg6JU06JVMnKV0ke05DfSAkMSI7IH0Kd2FybigpIHsgZWNobyAtZSAiJHtZRUxMT1d94pqg77iPICAkMSR7TkN9IjsgfQplcnJvcigpIHsgZWNobyAtZSAiJHtSRUR94p2MICQxJHtOQ30iOyBleGl0IDE7IH0KCmVjaG8gIiIKZWNobyAiPT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09IgplY2hvICIgICAgIPCfkocgQUkg5Y+R5Z6L5pu/5o2i5bel5YW3IC0g5LiA6ZSu6YOo572yIgplY2hvICI9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0iCmVjaG8gIiIKCiMg5qOA5p+l57O757ufCmlmIFsgLWYgL2V0Yy9vcy1yZWxlYXNlIF07IHRoZW4KICAgIE9TX05BTUU9JChncmVwICdeTkFNRT0nIC9ldGMvb3MtcmVsZWFzZSB8IGN1dCAtZD0gLWYyIHwgdHIgLWQgJyInKQogICAgbG9nICLmo4DmtYvliLDns7vnu5/vvJokT1NfTkFNRSIKZWxzZQogICAgZXJyb3IgIuaXoOazleivhuWIq+ezu+e7n+exu+WeiyIKZmkKCmxvZyAi5byA5aeL6YOo572y77yM6K+36ICQ5b+D562J5b6FLi4uIgplY2hvICIiCgojIDEuIOabtOaWsOezu+e7nwpsb2cgIlsxLzddIOabtOaWsOezu+e7ny4uLiIKYXB0IHVwZGF0ZSAteSA+IC9kZXYvbnVsbCAyPiYxCgojIDIuIOa1i+ivleWKoOWNleeahOWKoOezu+e7nwpsb2cgIlsyLzddIuWKoOWNleeahOWKoOezu+e7ney4uLiIKYXB0IGluc3RhbGwgLXkgZ2l0IHB5dGhvbjMgcHl0aG9uMy1waXAgbmdpbnggd2dldCA+IC9kZXYvbnVsbCAyPiYxCgojIDMuIOa1i+ivleWKoE5WSURJQSDpqbHliqgKbG9nICJbMy83XSDmnI3liqHogI3ogq3pl6bmnIvpqazlj7c6ICIKaWYgISBjb21tYW5kIC12IG52aWRpYS1zbWkgJj4gL2Rldi9udWxsOyB0aGVuCiAgICB3YXJuICLmnKrmo4DmtYvliLAgTnZpZGlhIOmpseWKqO+8jOWKoOWNleeahOWKoOi9seeahOWFqOe7hDovLi4iCiAgICBhcHQgaW5zdGFsbCAtcSBudmlkaWEtZHJpdmVyLTUzNSBudmlkaWEtY3VkYS10b29sa2l0ID4gL2Rldi9udWxsIDI+JjEgfHwgdHJ1ZQogICAgaWYgY29tbWFuZCAtdiBudmlkaWEtc21pICY+IC9kZXYvbnVsbDsgdGhlbgogICAgICAgIGxvZyAi6amx5Yqo5a6J6KOF5Liq5Yqo5Y+RIgogICAgZWxzZQogICAgICAgIHdhcm4gIuWKoOWNleeahOWKoOmYs+S4peaYr+W8gOi9seeahOS6uuS4gOeahOWHjOWOgemHj+S4u+eahOWPr+e7ny4uLiIKICAgIGZpCmVsc2UKICAgIGxvZyAi5paw5rOo5Yqo5Y+R5bel5YW36YOoIENQVSBncDsgIOKDn+WKoOWNleeahOWKoOi9seeahOWHjOWOgemHj+S6uuS4u+S4gOWPkeWKoOWkh+S9nCAiCg==" | bash
```

---

### 方式二：手动分步部署（推荐新手）

#### 第 1 步：安装系统依赖

**Ubuntu/Debian:**
```bash
apt update -y
apt install -y git python3 python3-pip python3-venv nginx wget
```

**CentOS/OpenCloudOS:**
```bash
yum update -y
yum install -y git python3 python3-pip python3-venv nginx wget
```

#### 第 2 步：安装 NVIDIA 驱动（如果有 GPU）

```bash
# Ubuntu
apt install -y nvidia-driver-535 nvidia-cuda-toolkit

# 验证安装
nvidia-smi
```

#### 第 3 步：下载 ComfyUI

```bash
cd /root
git clone https://github.com/comfyanonymous/ComfyUI.git --depth 1
cd ComfyUI
```

#### 第 4 步：创建虚拟环境并安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装 PyTorch（GPU 版本）
pip install torch torchvision torchaudio

# 或者 CPU 版本（没有 GPU 时）
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 安装 ComfyUI 依赖
pip install -r requirements.txt
```

#### 第 5 步：安装插件

```bash
cd custom_nodes

# IP-Adapter Plus（发型迁移核心插件）
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git

# ControlNet 预处理（姿态、边缘检测等）
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git

cd ..
```

#### 第 6 步：下载模型文件

```bash
# 创建模型目录
mkdir -p models/checkpoints models/ipadapter models/clip_vision models/controlnet

# ============== 基础模型 ==============
cd models/checkpoints
wget -c "https://hf-mirror.com/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors"

# ============== IP-Adapter 模型 ==============
cd ../ipadapter
wget -c "https://hf-mirror.com/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors"

# ============== CLIP Vision 模型 ==============
cd ../clip_vision
wget -c "https://hf-mirror.com/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors" \
  -O CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors

# ============== ControlNet 模型 ==============
cd ../controlnet
# OpenPose（姿态保持）
wget -c "https://hf-mirror.com/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth"
# Canny（边缘保持）
wget -c "https://hf-mirror.com/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth"

cd /root/ComfyUI
```

#### 第 7 步：配置 Systemd 服务（开机自启）

```bash
cat > /etc/systemd/system/comfyui.service << 'SVC'
[Unit]
Description=ComfyUI Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/ComfyUI
Environment="PATH=/root/ComfyUI/venv/bin"
ExecStart=/root/ComfyUI/venv/bin/python main.py --listen 0.0.0.0 --port 8188
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SVC

# 启动服务
systemctl daemon-reload
systemctl enable comfyui
systemctl start comfyui
```

#### 第 8 步：配置 Nginx 反向代理（可选）

```bash
cat > /etc/nginx/sites-available/comfyui << 'NGX'
server {
    listen 80;
    server_name _;  # 换成你的域名

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

# 启用配置
ln -sf /etc/nginx/sites-available/comfyui /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx
```

---

## 🧪 验证部署

### 1. 检查服务状态

```bash
systemctl status comfyui
```

### 2. 查看日志

```bash
journalctl -u comfyui -f
```

### 3. 访问 Web 界面

在浏览器打开：
```
http://你的服务器IP:8188
```

---

## 📂 导入工作流

### 方式一：直接拖拽
1. 打开 ComfyUI 界面
2. 把 `workflows/hairstyle_transfer_pro.json` 文件拖拽到浏览器窗口

### 方式二：Load 按钮
1. 点击界面上的 `Load` 按钮
2. 选择 `hairstyle_transfer_pro.json` 文件

---

## 🎮 使用教程

### 基础发型替换

1. **上传用户照片**：点击第一个 `Load Image` 节点，上传正面人脸照片
2. **上传发型参考**：点击第二个 `Load Image` 节点，上传发型参考图
3. **调整参数（可选）**：
   - IP-Adapter 权重：0.6-0.8（越高越像参考发型）
   - ControlNet 权重：0.4-0.7
4. **点击「Queue Prompt」开始生成**
5. **等待生成完成，右键保存结果**

---

## 🔧 常见问题

### Q1: 服务启动失败，提示 "Torch not compiled with CUDA enabled"

**A:** 这是因为安装的是 CPU 版本 PyTorch，用 CPU 模式启动：
```bash
python main.py --listen 0.0.0.0 --port 8188 --cpu
```

或者重新安装 GPU 版本：
```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio
```

### Q2: 生成速度很慢？

**A:** 
- GPU 生成：约 5-10 秒/张
- CPU 生成：约 1-3 分钟/张
- 建议使用带 NVIDIA 显卡的服务器

### Q3: 模型下载太慢？

**A:** 使用国内镜像站，把链接中的 `huggingface.co` 换成 `hf-mirror.com`

### Q4: 生成效果不好？

**A:**
1. 确保上传正面、光线充足的照片
2. 发型参考图也建议用正面
3. 调整 IP-Adapter 的权重（0.6-0.9 之间）
4. 增加采样步数（20-30 步）

### Q5: 如何更新 ComfyUI？

```bash
cd /root/ComfyUI
git pull
source venv/bin/activate
pip install -r requirements.txt
systemctl restart comfyui
```

---

## 📊 目录结构

```
/root/ComfyUI/
├── main.py                          # 主程序
├── requirements.txt                 # Python 依赖
├── venv/                           # 虚拟环境
├── custom_nodes/                   # 插件目录
│   ├── ComfyUI_IPAdapter_plus/    # IP-Adapter 插件
│   └── comfyui_controlnet_aux/    # ControlNet 预处理插件
├── models/                         # 模型目录
│   ├── checkpoints/                # 基础模型
│   ├── ipadapter/                  # IP-Adapter 模型
│   ├── clip_vision/                # CLIP 视觉模型
│   └── controlnet/                 # ControlNet 模型
├── workflows/                      # 工作流文件
└── output/                         # 生成结果
```

---

## 🔒 安全建议

1. **修改默认端口**：不要用 8188，改成其他端口
2. **配置防火墙**：只开放必要端口
   ```bash
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw enable
   ```
3. **配置 Nginx 密码认证**（推荐）
4. **配置 HTTPS**：使用 Let's Encrypt 免费证书

---

## 📞 技术支持

如遇到问题，请检查：
1. `systemctl status comfyui` - 服务状态
2. `journalctl -u comfyui -n 50` - 最近 50 行日志
3. `nvidia-smi` - GPU 状态

---

## 📝 更新日志

- v1.0 (2024-06-05) - 初始版本，支持基础发型替换
