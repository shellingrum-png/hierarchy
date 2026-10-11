import os
import sys
import json
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from image_processor import get_image_processor
from hair_mask import generate_hair_mask
from comfyui_client import ComfyUIClient, ComfyUIError

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../uploads'
app.config['OUTPUT_FOLDER'] = '../outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# ComfyUI API endpoint
COMFYUI_URL = os.getenv('COMFYUI_URL', 'http://127.0.0.1:8188')
PROCESSING_MODE = os.getenv('PROCESSING_MODE', 'local')  # 'local' or 'comfyui'

_comfyui = ComfyUIClient(COMFYUI_URL)

def is_comfyui_available():
    """Check if ComfyUI server is running"""
    return _comfyui.is_available()

def process_with_comfyui(user_path, hairstyle_path, output_path, mask_path=None):
    """真换发：头发 mask 局部重绘（ComfyUI + IP-Adapter + inpaint）。"""
    if mask_path is None:
        mask_path = user_path + '.mask.png'

    if not generate_hair_mask(user_path, mask_path):
        raise ComfyUIError('未在人像中检测到头发区域，无法进行局部重绘')

    return _comfyui.transfer_hairstyle(user_path, hairstyle_path, mask_path, output_path)

def process_with_local(user_path, hairstyle_path, output_path):
    """Process using local image processor"""
    processor = get_image_processor()
    return processor.transfer_hairstyle(user_path, hairstyle_path, output_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'user_photo' not in request.files or 'hairstyle_photo' not in request.files:
        return jsonify({'error': '缺少必要的文件'}), 400
    
    user_photo = request.files['user_photo']
    hairstyle_photo = request.files['hairstyle_photo']
    
    if user_photo.filename == '' or hairstyle_photo.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    # Save uploaded files
    user_ext = os.path.splitext(user_photo.filename)[1]
    hairstyle_ext = os.path.splitext(hairstyle_photo.filename)[1]
    
    user_filename = f'user_{uuid.uuid4().hex[:8]}{user_ext}'
    hairstyle_filename = f'hairstyle_{uuid.uuid4().hex[:8]}{hairstyle_ext}'
    
    user_path = os.path.join(app.config['UPLOAD_FOLDER'], user_filename)
    hairstyle_path = os.path.join(app.config['UPLOAD_FOLDER'], hairstyle_filename)
    
    user_photo.save(user_path)
    hairstyle_photo.save(hairstyle_path)
    
    # Process images
    output_filename = f'result_{uuid.uuid4().hex[:8]}.png'
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)

    if PROCESSING_MODE == 'comfyui':
        if not is_comfyui_available():
            return jsonify({'error': f'ComfyUI 未运行，请先启动：{COMFYUI_URL}'}), 503
        try:
            process_with_comfyui(user_path, hairstyle_path, output_path)
            mode_used = 'comfyui'
        except ComfyUIError as e:
            return jsonify({'error': f'换发型失败：{e}'}), 500
    else:
        try:
            if not process_with_local(user_path, hairstyle_path, output_path):
                return jsonify({'error': '本地演示模式处理失败'}), 500
        except Exception as e:
            return jsonify({
                'error': f'本地演示模式不可用：{e}。'
                         '本地模式依赖 mediapipe==0.10.9（需 Python 3.10/3.11）；'
                         '真实换发请改用 ComfyUI 模式。'
            }), 500
        mode_used = 'local-demo'

    if os.path.exists(output_path):
        return jsonify({
            'success': True,
            'result_url': f'/outputs/{output_filename}',
            'mode': mode_used
        })
    return jsonify({'error': '图片处理失败，请重试'}), 500

@app.route('/outputs/<filename>')
def outputs(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/status')
def status():
    """Check server status"""
    available = is_comfyui_available()
    return jsonify({
        'comfyui_available': available,
        'comfyui_url': COMFYUI_URL,
        'processing_mode': PROCESSING_MODE,
        'missing_nodes': _comfyui.missing_nodes() if available else None
    })

if __name__ == '__main__':
    print(f"Starting Hairstyle Transfer Server...")
    print(f"Processing mode: {PROCESSING_MODE}")
    print(f"ComfyUI available: {is_comfyui_available()}")
    print(f"Server running at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
