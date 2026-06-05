import os
import sys
import json
import uuid
import requests
from flask import Flask, render_template, request, jsonify, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from image_processor import get_image_processor

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../uploads'
app.config['OUTPUT_FOLDER'] = '../outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# ComfyUI API endpoint
COMFYUI_URL = os.getenv('COMFYUI_URL', 'http://127.0.0.1:8188')
PROCESSING_MODE = os.getenv('PROCESSING_MODE', 'local')  # 'local' or 'comfyui'

def is_comfyui_available():
    """Check if ComfyUI server is running"""
    try:
        response = requests.get(f'{COMFYUI_URL}/system_stats', timeout=3)
        return response.status_code == 200
    except:
        return False

def process_with_comfyui(user_path, hairstyle_path, output_path):
    """Process using ComfyUI"""
    try:
        # 这里简化处理 - 实际需要正确配置的 ComfyUI 工作流
        # 真实场景中，应该调用完整的 ComfyUI API
        return False
    except Exception as e:
        print(f"ComfyUI error: {e}")
        return False

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
    
    success = False
    mode_used = 'local'
    
    # Try ComfyUI first if enabled
    if PROCESSING_MODE == 'comfyui' and is_comfyui_available():
        success = process_with_comfyui(user_path, hairstyle_path, output_path)
        mode_used = 'comfyui'
    
    # Fallback to local processing
    if not success:
        success = process_with_local(user_path, hairstyle_path, output_path)
        mode_used = 'local'
    
    if success and os.path.exists(output_path):
        return jsonify({
            'success': True,
            'result_url': f'/outputs/{output_filename}',
            'mode': mode_used
        })
    else:
        return jsonify({'error': '图片处理失败，请重试'}), 500

@app.route('/outputs/<filename>')
def outputs(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/status')
def status():
    """Check server status"""
    return jsonify({
        'comfyui_available': is_comfyui_available(),
        'comfyui_url': COMFYUI_URL,
        'processing_mode': PROCESSING_MODE
    })

if __name__ == '__main__':
    print(f"Starting Hairstyle Transfer Server...")
    print(f"Processing mode: {PROCESSING_MODE}")
    print(f"ComfyUI available: {is_comfyui_available()}")
    print(f"Server running at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
