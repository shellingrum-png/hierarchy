# AI 发型替换工具

真换发 = **头发区域分割** + **局部重绘(inpaint)** + **参考图引导**。三步缺一不可。
本仓库用 **ComfyUI + IP-Adapter** 实现：分割出头发 mask，只在 mask 内低重绘幅度地
重绘头发，脸和背景保留。

## ⚠️ 先看清两种模式

| 模式 | 说明 |
|---|---|
| **本地模式**（`PROCESSING_MODE=local`） | **演示/占位**。用 OpenCV 把参考发型图 resize 后泊松融合贴上，**不是真换发**，效果是「融合」。仅供无 GPU 时预览 UI 流程。 |
| **ComfyUI 模式**（`PROCESSING_MODE=comfyui`） | **唯一能出真换发效果的模式**。需要本机跑 ComfyUI + 一块像样的 GPU。 |

> 出融合效果不是 bug，是本地模式的设计结果。要看真效果必须走 ComfyUI 模式。

## 真换发链路

```
用户照 ──┬─→ [BiSeNet face-parsing] ──→ 头发 mask ──────────┐
         │   (server/hair_mask.py)                          │
         └─→ LoadImage ─→ VAEEncodeForInpaint ─→ latent      │
                                                             ↓
参考发型图 ─→ IPAdapterAdvanced(attn_mask=m头发mask) ─→ KSampler(mask内低denoise)
                                                             ↓
                                                    VAEDecode → 结果(脸保留,只换头发)
```

工作流文件：`workflows/hairstyle_transfer_inpaint_api.json`（ComfyUI **API 格式**，非 UI 格式）。

## 项目结构

```
hierarchy/
├── server/
│   ├── app_v2.py              # Web 服务主程序(Flask)
│   ├── comfyui_client.py      # ComfyUI HTTP 客户端(上传/提交/轮询/下载)
│   ├── hair_mask.py           # 头发 mask 分割(BiSeNet)
│   ├── image_processor.py     # 本地演示模式(贴图融合)
│   └── templates/index.html   # 前端界面
├── workflows/
│   ├── hairstyle_transfer_inpaint_api.json   # ✅ 正确的 inpaint 工作流
│   └── _legacy_wrong/         # ❌ 废弃的整图重绘工作流(留档)
├── requirements.txt
└── README.md
```

## 快速开始

### 本地演示模式（无 GPU，只看 UI 流程）

> ⚠️ **Python 版本**：本地演示模式依赖 `mediapipe==0.10.9`，它只有 Python 3.10/3.11 的 wheel。
> 若用 Python 3.12+，本地演示模式装不上——直接用下面的 ComfyUI 模式（真换发链路在 3.12 上正常）。

```bash
pip install -r requirements.txt
cd server && python app_v2.py
# 打开 http://localhost:5000
```

### ComfyUI 真换发模式（推荐，需要 GPU）

> ✅ **已在 Apple Silicon Mac 上实测跑通**（M1/16GB，MPS 加速，无独显）：
> 512×512 出一张约 **4 分钟**，模型共约 **4.5GB**。**不需要 NVIDIA 卡、不需要 ControlNet。**

#### 1. 安装 ComfyUI

```bash
git clone --depth 1 https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt      # 或复用已有 torch 环境
```

#### 2. 安装必需插件

```bash
cd custom_nodes
git clone --depth 1 https://github.com/cubiq/ComfyUI_IPAdapter_plus.git
```

> 头发 mask 由本项目的 `server/hair_mask.py`（facexlib BiSeNet）在服务端生成后上传，
> **无需**再装 ComfyUI 的 face-parsing 自定义节点。

#### 3. 下载模型（仅 3 个，约 4.5GB）

| 模型 | 放到 | 大小 |
|---|---|---|
| `v1-5-pruned-emaonly-fp16.safetensors` | `ComfyUI/models/checkpoints/` | ~2.0G |
| `ip-adapter-plus_sd15.safetensors` | `ComfyUI/models/ipadapter/` | ~97M |
| `CLIP-ViT-H-14-laion2B-s32B-b79K.safetensors` | `ComfyUI/models/clip_vision/` | ~2.4G |

下载源（国内可用镜像，见 `模型下载一步到位.md`）。文件名必须与上表一致——
`IPAdapterUnifiedLoader` 用 preset `PLUS (high strength)` 按文件名正则匹配这三个模型。

#### 4. 启动 ComfyUI 与 Web 服务

```bash
# 终端 1
cd ComfyUI && python main.py          # http://localhost:8188

# 终端 2
export PROCESSING_MODE=comfyui
export COMFYUI_URL=http://127.0.0.1:8188
cd server && python app_v2.py         # http://localhost:5000
```

打开 `http://localhost:5000`，左侧传本人正面照、右侧传发型参考图，点「开始换发型」。

## 调参

工作流 `workflows/hairstyle_transfer_inpaint_api.json` 里几个关键旋钮：

- `KSampler.denoise`（默认 0.65）：**调高**头发变化更大，但过高脸会漂移；**调低**更贴原图但变化小。建议 0.5–0.7。
- `IPAdapterAdvanced.weight`（默认 0.75）：参考发型的强度。过高会把整图风格带走，建议 0.6–0.8。
- `IPAdapterAdvanced.end_at`（默认 0.8）：让参考只在采样前段起作用，保留更多原始结构。
- `VAEEncodeForInpaint.grow_mask_by`（默认 6）：mask 向外扩张的像素数，过渡更自然。

## 故障排除

- **`/status` 返回 `missing_nodes` 非空** → 缺 `ComfyUI_IPAdapter_plus` 插件，按上面第 2 步装。
- **报「未在人像中检测到头发区域」** → 照片没检测到脸，换一张正面、光线充足的照片。
- **结果脸变了/不像本人** → 降低 `denoise`，或降低 `IPAdapterAdvanced.weight`。
- **本地模式结果糊成一团** → 这是贴图融合的正常表现，换用 ComfyUI 模式。

## 许可证

MIT License
