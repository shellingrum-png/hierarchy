import os
import sys
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from PIL import Image
import io
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '../uploads'
app.config['OUTPUT_FOLDER'] = '../outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def simple_hairstyle_composite(user_img_path, hair_img_path, output_path):
    """简单的发型合成演示"""
    user_img = Image.open(user_img_path).convert('RGBA')
    hair_img = Image.open(hair_img_path).convert('RGBA')
    
    # 调整用户图片大小
    target_size = 512
    user_img.thumbnail((target_size, target_size))
    
    # 调整发型图片大小
    hair_width = int(user_img.width * 0.8)
    hair_img = hair_img.resize((hair_width, int(hair_width * hair_img.height / hair_img.width)))
    
    # 创建结果图片
    result = Image.new('RGBA', user_img.size, (0, 0, 0, 0))
    result.paste(user_img, (0, 0))
    
    # 将发型放在顶部 (简化演示)
    hair_x = (user_img.width - hair_img.width) // 2
    hair_y = int(user_img.height * 0.05)
    
    # 半透明叠加效果
    result.paste(hair_img, (hair_x, hair_y), hair_img if hair_img.mode == 'RGBA' else None)
    
    # 保存结果
    result = result.convert('RGB')
    result.save(output_path)
    return True

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
    
    success = simple_hairstyle_composite(user_path, hairstyle_path, output_path)
    
    if success and os.path.exists(output_path):
        return jsonify({
            'success': True,
            'result_url': f'/outputs/{output_filename}',
            'mode': 'demo'
        })
    else:
        return jsonify({'error': '图片处理失败，请重试'}), 500

@app.route('/outputs/<filename>')
def outputs(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

@app.route('/status')
def status():
    return jsonify({
        'mode': 'demo',
        'status': 'running'
    })

if __name__ == '__main__':
    print("="*50)
    print("    💇 AI 发型替换工具 (演示版)")
    print("="*50)
    print("")
    print("🌐 服务器启动中...")
    print("📱 请打开浏览器访问: http://localhost:5000")
    print("")
    print("⚠️  注意: 这是演示版本，使用简单的图像合成")
    print("   如需高质量 AI 生成，请配置 ComfyUI")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=True)
