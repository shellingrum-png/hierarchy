import os
import json
import uuid
import base64
import requests
from io import BytesIO
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

# ComfyUI API endpoint
COMFYUI_URL = os.getenv('COMFYUI_URL', 'http://127.0.0.1:8188')

def load_workflow():
    with open('workflows/hairstyle_transfer.json', 'r') as f:
        return json.load(f)

def upload_to_comfyui(image_path):
    """Upload image to ComfyUI server"""
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f'{COMFYUI_URL}/upload/image', files=files)
    return response.json()

def queue_prompt(prompt_workflow):
    """Queue prompt in ComfyUI"""
    payload = {'prompt': prompt_workflow}
    response = requests.post(f'{COMFYUI_URL}/prompt', json=payload)
    return response.json()

def get_history(prompt_id):
    """Get execution history"""
    response = requests.get(f'{COMFYUI_URL}/history/{prompt_id}')
    return response.json()

def get_image(filename, subfolder, folder_type):
    """Get generated image from ComfyUI"""
    params = {'filename': filename, 'subfolder': subfolder, 'type': folder_type}
    response = requests.get(f'{COMFYUI_URL}/view', params=params)
    return response.content

def process_hairstyle_transfer(user_photo_path, hairstyle_path):
    """Process hairstyle transfer using ComfyUI API"""
    try:
        # Upload images to ComfyUI
        user_img_name = os.path.basename(user_photo_path)
        hairstyle_img_name = os.path.basename(hairstyle_path)
        
        upload_to_comfyui(user_photo_path)
        upload_to_comfyui(hairstyle_path)
        
        # Load and modify workflow
        workflow = load_workflow()
        
        # Find and update image nodes
        for node_id, node in workflow.items():
            if node['class_type'] == 'LoadImage':
                if 'user' in node.get('widgets_values', [''])[0].lower() or 'photo' in node.get('widgets_values', [''])[0].lower():
                    node['widgets_values'][0] = user_img_name
                elif 'hair' in node.get('widgets_values', [''])[0].lower() or 'style' in node.get('widgets_values', [''])[0].lower():
                    node['widgets_values'][0] = hairstyle_img_name
        
        # Queue prompt
        result = queue_prompt(workflow)
        prompt_id = result.get('prompt_id')
        
        # Wait for completion (simplified)
        import time
        max_wait = 120
        start = time.time()
        
        while time.time() - start < max_wait:
            history = get_history(prompt_id)
            if prompt_id in history:
                outputs = history[prompt_id].get('outputs', {})
                for node_id, node_output in outputs.items():
                    if 'images' in node_output:
                        img_info = node_output['images'][0]
                        img_data = get_image(
                            img_info['filename'],
                            img_info.get('subfolder', ''),
                            img_info.get('type', 'output')
                        )
                        output_path = os.path.join(app.config['OUTPUT_FOLDER'], f'result_{uuid.uuid4().hex[:8]}.png')
                        with open(output_path, 'wb') as f:
                            f.write(img_data)
                        return output_path
            time.sleep(2)
        
        return None
    except Exception as e:
        print(f"Error processing hairstyle transfer: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'user_photo' not in request.files or 'hairstyle_photo' not in request.files:
        return jsonify({'error': 'Missing required files'}), 400
    
    user_photo = request.files['user_photo']
    hairstyle_photo = request.files['hairstyle_photo']
    
    if user_photo.filename == '' or hairstyle_photo.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
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
    output_path = process_hairstyle_transfer(user_path, hairstyle_path)
    
    if output_path and os.path.exists(output_path):
        output_filename = os.path.basename(output_path)
        return jsonify({
            'success': True,
            'result_url': f'/outputs/{output_filename}'
        })
    else:
        return jsonify({'error': 'Processing failed'}), 500

@app.route('/outputs/<filename>')
def outputs(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/health')
def health():
    """Check ComfyUI connection"""
    try:
        response = requests.get(f'{COMFYUI_URL}/system_stats', timeout=5)
        return jsonify({
            'comfyui_connected': True,
            'comfyui_url': COMFYUI_URL,
            'stats': response.json()
        })
    except:
        return jsonify({
            'comfyui_connected': False,
            'comfyui_url': COMFYUI_URL,
            'error': 'Cannot connect to ComfyUI server'
        }), 503

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
