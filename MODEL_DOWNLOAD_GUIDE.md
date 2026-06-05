# 📦 模型下载清单

## 必须下载的模型文件

### 1. 基础模型 (Checkpoint)
**文件：** `v1-5-pruned-emaonly.ckpt` 或 `.safetensors`
- 下载地址：https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors
- 放置位置：`ComfyUI/models/checkpoints/`

### 2. IP-Adapter 模型
**文件：** `ip-adapter-plus_sd15.safetensors`
- 下载地址：https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus_sd15.safetensors
- 放置位置：`ComfyUI/models/ipadapter/`

**文件：** `ip-adapter-plus-face_sd15.safetensors` (可选，人脸效果更好)
- 下载地址：https://huggingface.co/h94/IP-Adapter/resolve/main/models/ip-adapter-plus-face_sd15.safetensors
- 放置位置：`ComfyUI/models/ipadapter/`

### 3. CLIP Vision 模型
**文件：** `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`
- 下载地址：https://huggingface.co/h94/IP-Adapter/resolve/main/models/image_encoder/model.safetensors
- 重命名为：`CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors`
- 放置位置：`ComfyUI/models/clip_vision/`

### 4. ControlNet 模型

**OpenPose (姿态控制)**
- 文件：`control_v11p_sd15_openpose.pth`
- 下载地址：https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_openpose.pth
- 放置位置：`ComfyUI/models/controlnet/`

**Canny (边缘检测)**
- 文件：`control_v11p_sd15_canny.pth`
- 下载地址：https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11p_sd15_canny.pth
- 放置位置：`ComfyUI/models/controlnet/`

**Depth (深度图，可选)**
- 文件：`control_v11f1p_sd15_depth.pth`
- 下载地址：https://huggingface.co/lllyasviel/ControlNet-v1-1/resolve/main/control_v11f1p_sd15_depth.pth
- 放置位置：`ComfyUI/models/controlnet/`

## 🔌 需要安装的插件

### 1. IP-Adapter Plus
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
```

### 2. ControlNet Auxiliary Preprocessors
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/Fannovel16/comfyui_controlnet_aux.git
```

### 3. FaceTools (可选，人脸增强)
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/joelurolmaya/comfyui_facetools.git
```

## 📁 完整目录结构

```
ComfyUI/
├── models/
│   ├── checkpoints/
│   │   └── v1-5-pruned-emaonly.safetensors
│   ├── ipadapter/
│   │   ├── ip-adapter-plus_sd15.safetensors
│   │   └── ip-adapter-plus-face_sd15.safetensors
│   ├── clip_vision/
│   │   └── CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors
│   ├── controlnet/
│   │   ├── control_v11p_sd15_openpose.pth
│   │   ├── control_v11p_sd15_canny.pth
│   │   └── control_v11f1p_sd15_depth.pth
│   └── vae/
│       └── (可选) vae-ft-mse-840000-ema-pruned.safetensors
└── custom_nodes/
    ├── ComfyUI_IPAdapter_plus/
    ├── comfyui_controlnet_aux/
    └── (可选) comfyui_facetools/
```

## 🚀 启动 ComfyUI

```bash
cd ComfyUI
python main.py
```

然后打开浏览器访问：http://127.0.0.1:8188

## 📥 导入工作流

1. 在 ComfyUI 界面点击 `Load` 按钮
2. 选择 `workflows/hairstyle_transfer_pro.json`
3. 或者直接把 JSON 文件拖拽到浏览器窗口中

## 💡 使用提示

1. **用户照片**：建议使用正面、光线充足、无遮挡的人脸照片
2. **发型参考**：建议使用正面、高清、清晰可见发型的照片
3. **参数调整**：
   - IP-Adapter 权重：0.6-0.9 (越高越像参考发型)
   - ControlNet 权重：0.4-0.7 (越高姿态保持越好)
   - 采样步数：20-30 步
   - CFG：6-8
