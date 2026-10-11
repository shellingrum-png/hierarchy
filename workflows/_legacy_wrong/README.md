# workflows/_legacy_wrong 里的文件为什么废弃

这两个 JSON（`hairstyle_transfer.json` / `hairstyle_transfer_pro.json`）是初版工作流，
**从根上就是错的**，2026-10-09 起不再使用，仅留档对照：

1. **整图重绘，无头发 mask** —— 把整张人像丢进 KSampler，是「画一张新图」，
   不是「只改头发」，脸会变、不再像本人。
2. **无任何 inpaint 节点** —— 真换发的核心（只重绘头发那一片）完全缺失。
3. **Canny 直接吃整张原图** —— 会锁死旧发型轮廓，与「换发型」目标直接矛盾。
4. **pro 版混入 Rembg 抠背景节点** —— 换发流程里出现抠图节点，疑似拼凑。

正确的流程见 `workflows/hairstyle_transfer_inpaint_api.json`：
头发 mask 分割 → `VAEEncodeForInpaint` + `SetLatentNoiseMask` → IPAdapter（参考发型，作用在 mask 内）
→ KSampler（低 denoise）→ 解码。脸保留，只换头发。
