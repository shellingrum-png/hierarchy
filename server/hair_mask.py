"""头发 mask 分割。

用 facexlib 的 BiSeNet face-parsing 在人像上分割出头发类别，产出二值 mask。
喂给 ComfyUI 的 inpaint 工作流做「只重绘头发区」，这是换发型与贴图融合的分水岭。

CelebAMask-HQ 风格 19 类里 hair 的索引是 17（脸颊等类别也常被涂成 255，
但掩码的**值**只是可视化用色，按索引取头发才是关键）。
"""
import os

import cv2
import numpy as np

HAIR_CLASS = 17

_MODEL = None
_DETECTOR = None
_DEVICE = None


def _device():
    global _DEVICE
    if _DEVICE is None:
        import torch
        if torch.backends.mps.is_available():
            _DEVICE = 'mps'
        elif torch.cuda.is_available():
            _DEVICE = 'cuda'
        else:
            _DEVICE = 'cpu'
    return _DEVICE


def _get_model():
    global _MODEL
    if _MODEL is None:
        from facexlib.parsing import init_parsing_model
        _MODEL = init_parsing_model(model_name='bisenet', device=_device())
    return _MODEL


def _get_detector():
    global _DETECTOR
    if _DETECTOR is None:
        from facexlib.detection import init_detection_model
        _DETECTOR = init_detection_model('retinaface_mobile0.25', device=_device())
    return _DETECTOR


def _detect_box(img_bgr):
    """RetinaFace 检测最大人脸，返回包围盒并向外扩，覆盖头发/头顶。"""
    import torch

    with torch.no_grad():
        dets = _get_detector().detect_faces(img_bgr)

    h, w = img_bgr.shape[:2]
    if dets is None or len(dets) == 0:
        return 0, 0, w, h

    areas = (dets[:, 2] - dets[:, 0]) * (dets[:, 3] - dets[:, 1])
    x1, y1, x2, y2 = dets[int(areas.argmax()), :4]
    bw, bh = x2 - x1, y2 - y1
    pad_x, pad_top, pad_bottom = int(bw * 0.6), int(bh * 0.8), int(bh * 0.25)
    return (max(0, int(x1) - pad_x), max(0, int(y1) - pad_top),
            min(w, int(x2) + pad_x), min(h, int(y2) + pad_bottom))


def generate_hair_mask(image_path, output_path, blur=9, dilate=0):
    """生成头发二值 mask PNG（白色=头发），返回是否含非空头发区域。"""
    import torch
    from torchvision import transforms
    from facexlib.utils import img2tensor

    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(image_path)
    h, w = img.shape[:2]

    x1, y1, x2, y2 = _detect_box(img)
    crop = img[y1:y2, x1:x2]
    crop_resized = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_LINEAR)

    tensor = img2tensor(crop_resized.astype('float32') / 255., bgr2rgb=True, float32=True)
    transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5), inplace=True)(tensor)
    tensor = torch.unsqueeze(tensor, 0).to(_device())

    with torch.no_grad():
        out = _get_model()(tensor)[0]
    parsing = out.argmax(dim=1).squeeze().cpu().numpy().astype(np.uint8)

    hair = (parsing == HAIR_CLASS).astype(np.uint8) * 255
    hair = cv2.resize(hair, (x2 - x1, y2 - y1), interpolation=cv2.INTER_NEAREST)

    mask = np.zeros((h, w), dtype=np.uint8)
    mask[y1:y2, x1:x2] = hair

    if dilate > 0:
        mask = cv2.dilate(mask, np.ones((dilate, dilate), np.uint8), iterations=1)
    if blur > 0:
        k = blur if blur % 2 == 1 else blur + 1
        mask = cv2.GaussianBlur(mask, (k, k), 0)

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    cv2.imwrite(output_path, mask)
    return bool((mask > 127).any())


if __name__ == '__main__':
    import sys
    src, dst = sys.argv[1], sys.argv[2]
    ok = generate_hair_mask(src, dst)
    print(f'mask -> {dst} (has_hair={ok}, device={_device()})')
