"""ComfyUI HTTP 客户端：把 inpaint 工作流跑起来。

链路：上传(人像/发型参考/头发mask) → 载入 API 格式工作流模板 →
替换 LoadImage 文件名 + 随机 seed → POST /prompt → 轮询 /history →
下载结果图。全图重绘是错的，这里跑的是「头发 mask 内局部重绘」。
"""
import json
import os
import random
import time
import uuid

import requests

WORKFLOW_JSON = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'workflows', 'hairstyle_transfer_inpaint_api.json')

# 这些工作流里的 LoadImage 节点，按 node id 对应固定的图片角色。
IMAGE_INPUTS = {'5': 'user', '6': 'hairstyle', '7': 'mask'}

# 工作流用到的自定义节点，缺一个就跑不通，提前报清楚。
REQUIRED_NODE_CLASSES = [
    'IPAdapterUnifiedLoader',
    'IPAdapterAdvanced',
    'VAEEncodeForInpaint',
    'SetLatentNoiseMask',
    'ImageToMask',
]


class ComfyUIError(RuntimeError):
    pass


class ComfyUIClient:
    def __init__(self, base_url='http://127.0.0.1:8188', timeout=180):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

    def _get(self, path):
        return requests.get(f'{self.base_url}{path}', timeout=10)

    def is_available(self):
        try:
            return self._get('/system_stats').status_code == 200
        except requests.RequestException:
            return False

    def object_info(self):
        return self._get('/object_info').json()

    def missing_nodes(self):
        ours = set(REQUIRED_NODE_CLASSES)
        try:
            available = set(self.object_info().keys())
        except requests.RequestException:
            return list(ours)
        return sorted(ours - available)

    def upload_image(self, path, name=None):
        name = name or os.path.basename(path)
        with open(path, 'rb') as f:
            files = {'image': (name, f, 'image/png')}
            data = {'overwrite': 'true'}
            r = requests.post(f'{self.base_url}/upload/image', files=files, data=data, timeout=30)
        r.raise_for_status()
        return r.json()['name']

    def _load_workflow(self, image_names, seed, denoise):
        wf = json.load(open(WORKFLOW_JSON, encoding='utf-8'))
        for node_id, role in IMAGE_INPUTS.items():
            if node_id in wf and role in image_names:
                wf[node_id]['inputs']['image'] = image_names[role]
        wf['3']['inputs']['seed'] = seed
        if denoise is not None:
            wf['3']['inputs']['denoise'] = denoise
        return wf

    def _submit(self, workflow, client_id):
        r = requests.post(f'{self.base_url}/prompt',
                          json={'prompt': workflow, 'client_id': client_id}, timeout=30)
        if r.status_code != 200:
            raise ComfyUIError(f'提交工作流被拒 ({r.status_code}): {r.text[:500]}')
        return r.json()['prompt_id']

    def _wait_history(self, prompt_id):
        deadline = time.time() + self.timeout
        while time.time() < deadline:
            try:
                hist = self._get(f'/history/{prompt_id}').json()
            except requests.RequestException:
                hist = {}
            if prompt_id in hist:
                entry = hist[prompt_id]
                status = entry.get('status', {})
                if status.get('status_str') == 'error' or not status.get('completed', True):
                    messages = status.get('messages')
                    if status.get('status_str') == 'error':
                        raise ComfyUIError(f'ComfyUI 执行出错: {messages}')
                return entry
            time.sleep(1)
        raise ComfyUIError('等待 ComfyUI 结果超时')

    def _download_output(self, history_entry, output_path):
        images = []
        for node_output in history_entry.get('outputs', {}).values():
            images.extend(node_output.get('images', []))
        if not images:
            raise ComfyUIError('ComfyUI 未返回结果图')
        img = images[0]
        params = {'filename': img['filename'], 'subfolder': img.get('subfolder', ''),
                  'type': img.get('type', 'output')}
        r = requests.get(f'{self.base_url}/view', params=params, timeout=60)
        r.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(r.content)
        return True

    def transfer_hairstyle(self, user_path, hairstyle_path, mask_path, output_path,
                           seed=None, denoise=None):
        missing = self.missing_nodes()
        if missing:
            raise ComfyUIError(
                'ComfyUI 缺少必需节点: ' + ', '.join(missing) +
                '（需安装 ComfyUI_IPAdapter_plus）')

        token = uuid.uuid4().hex[:8]
        names = {
            'user': self.upload_image(user_path, f'user_{token}.png'),
            'hairstyle': self.upload_image(hairstyle_path, f'hairstyle_{token}.png'),
            'mask': self.upload_image(mask_path, f'mask_{token}.png'),
        }
        seed = random.randint(0, 2**31 - 1) if seed is None else seed
        workflow = self._load_workflow(names, seed, denoise)
        prompt_id = self._submit(workflow, uuid.uuid4().hex)
        entry = self._wait_history(prompt_id)
        return self._download_output(entry, output_path)
