# AI 发型替换工具

基于 **ComfyUI + IP-Adapter + ControlNet** 的智能发型替换工具。

## 功能特性

- 👤 上传您的正面照片
- 💇 上传发型参考图片
- ✨ AI 自动完成发型替换
- 🎨 支持两种处理模式：
  - **本地模式**：使用 OpenCV + MediaPipe 进行快速演示
  - **ComfyUI 模式**：使用 IP-Adapter + ControlNet 实现高质量生成

## 项目结构

```
comfyui-ip-adapter-controlnet/
├── server/
│   ├── app_v2.py              # Web 服务器主程序
│   ├── image_processor.py     # 本地图像处理模块
│   ├── templates/
│   │   └── index.html         # 前端界面
│   └── static/                # 静态资源
├── workflows/
│   └── hairstyle_transfer.json # ComfyUI 工作流
├── uploads/                   # 上传文件目录
├── outputs/                   # 结果输出目录
├── models/                    # ComfyUI 模型目录
├── requirements.txt           # Python 依赖
└── README.md
```

## 快速开始

### 方式一：本地演示模式（推荐快速体验）

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 启动服务器：
```bash
cd server
python app_v2.py
```

3. 打开浏览器访问：`http://localhost:5000`

### 方式二：ComfyUI 高级模式（高质量生成）

#### 1. 安装 ComfyUI

```bash
# 克隆 ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# 安装依赖
pip install -r requirements.txt
```

#### 2. 安装必要的插件

**IP-Adapter 插件：**
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
```

**ControlNet 辅助插件：**
```bash
git clone https://github.com/Fannovel16/comfy_controlnet_preprocessors.git
```

#### 3. 下载模型文件

将以下模型放入 ComfyUI 的相应目录：

**基础模型：**
- `v1-5-pruned-emaonly.ckpt` → `ComfyUI/models/checkpoints/`

**IP-Adapter 模型：**
- `ip-adapter-plus_sd15.bin` → `ComfyUI/models/ipadapter/`
- `ip-adapter-plus-face_sd15.bin` → `ComfyUI/models/ipadapter/`

**ControlNet 模型：**
- `control_sd15_openpose.pth` → `ComfyUI/models/controlnet/`
- `control_sd15_canny.pth` → `ComfyUI/models/controlnet/`
- `control_sd15_depth.pth` → `ComfyUI/models/controlnet/`

**CLIP Vision 模型：**
- `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` → `ComfyUI/models/clip_vision/`

#### 4. 启动 ComfyUI

```bash
cd ComfyUI
python main.py
```

ComfyUI 将在 `http://localhost:8188` 启动

#### 5. 导入工作流

- 在 ComfyUI 界面中点击 `Load`
- 选择 `workflows/hairstyle_transfer.json`
- 或者直接将 JSON 文件拖拽到界面中

#### 6. 启动发型替换工具

```bash
# 设置环境变量使用 ComfyUI 模式
export PROCESSING_MODE=comfyui
export COMFYUI_URL=http://127.0.0.1:8188

cd server
python app_v2.py
```

## 使用说明

1. 打开网页 `http://localhost:5000`
2. 在左侧上传您的正面照片（建议光线充足，无遮挡）
3. 在右侧上传您喜欢的发型参考图片
4. 点击「开始换发型 ✨」按钮
5. 等待 AI 处理完成（通常需要 30-60 秒）
6. 查看并下载结果

## 使用提示

- ✅ 使用正面、光线充足的照片效果最佳
- ✅ 发型参考图建议选择正面的高清图片
- ✅ 避免佩戴帽子、墨镜等遮挡面部的配饰
- ❌ 避免侧脸或模糊的照片
- ❌ 避免极端光照条件

## 技术架构

### 本地模式
- **MediaPipe**：人脸关键点检测
- **OpenCV**：图像处理和泊松融合
- **色彩迁移**：保持肤色一致性

### ComfyUI 模式
- **IP-Adapter**：提取发型参考的特征并迁移到目标图像
- **ControlNet (OpenPose)**：保持人脸姿态和结构
- **ControlNet (Canny)**：保持边缘和轮廓
- **ControlNet (Depth)**：保持深度信息

## 工作流说明

ComfyUI 工作流包含以下核心节点：

1. **模型加载**：Stable Diffusion v1.5 + VAE
2. **参考图像加载**：用户照片 + 发型参考
3. **IP-Adapter**：特征提取和迁移
4. **ControlNet**：多层控制（OpenPose + Canny + Depth）
5. **采样器**：图像生成
6. **输出**：保存结果

## 故障排除

### ComfyUI 连接失败
- 确认 ComfyUI 已在 `http://localhost:8188` 运行
- 检查端口是否被占用
- 查看 ComfyUI 控制台输出

### 模型加载失败
- 确认所有模型文件已放在正确的目录
- 检查模型文件名是否与工作流中配置的一致
- 确保磁盘空间充足

### 生成效果不佳
- 尝试使用更高质量的参考图片
- 调整 IP-Adapter 的权重（默认 0.8）
- 调整 ControlNet 的权重（OpenPose 0.6，Canny 0.4）

## 许可证

MIT License
