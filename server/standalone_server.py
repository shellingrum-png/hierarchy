#!/usr/bin/env python3
"""
极简发型替换工具 - 无需额外依赖
使用 Python 内置的 http.server
"""
import os
import sys
import json
import uuid
import io
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

UPLOAD_FOLDER = '../uploads'
OUTPUT_FOLDER = '../outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def parse_multipart_form_data(content_type, body):
    """简单的 multipart/form-data 解析"""
    boundary = content_type.split('boundary=')[-1].encode()
    parts = body.split(b'--' + boundary)
    
    files = {}
    
    for part in parts:
        if b'Content-Disposition: form-data;' in part:
            lines = part.split(b'\r\n')
            content_disposition = None
            content_type = None
            data_start = 0
            
            for i, line in enumerate(lines):
                if b'Content-Disposition:' in line:
                    content_disposition = line.decode(errors='ignore')
                elif b'Content-Type:' in line:
                    content_type = line.decode(errors='ignore')
                elif line == b'':
                    data_start = i + 1
                    break
            
            if content_disposition:
                # Extract name and filename
                name_match = None
                filename_match = None
                if 'name="' in content_disposition:
                    name_start = content_disposition.find('name="') + 6
                    name_end = content_disposition.find('"', name_start)
                    name_match = content_disposition[name_start:name_end]
                if 'filename="' in content_disposition:
                    fn_start = content_disposition.find('filename="') + 10
                    fn_end = content_disposition.find('"', fn_start)
                    filename_match = content_disposition[fn_start:fn_end]
                
                if name_match and data_start < len(lines):
                    data_lines = lines[data_start:-2]  # Remove last empty lines
                    file_data = b'\r\n'.join(data_lines)
                    files[name_match] = {
                        'filename': filename_match,
                        'content': file_data
                    }
    
    return files

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('templates/index.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path.startswith('/outputs/'):
            filename = urllib.parse.unquote(self.path[9:])
            filepath = os.path.join(OUTPUT_FOLDER, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.end_headers()
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'mode': 'standalone', 'status': 'running'}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                content_length = int(self.headers.get('Content-Length', 0))
                
                if 'multipart/form-data' in content_type:
                    body = self.rfile.read(content_length)
                    files = parse_multipart_form_data(content_type, body)
                    
                    user_file = files.get('user_photo', {})
                    hair_file = files.get('hairstyle_photo', {})
                    
                    if user_file.get('filename') and hair_file.get('filename'):
                        # Save files
                        user_filename = f'user_{uuid.uuid4().hex[:8]}_{user_file["filename"]}'
                        hair_filename = f'hair_{uuid.uuid4().hex[:8]}_{hair_file["filename"]}'
                        
                        user_path = os.path.join(UPLOAD_FOLDER, user_filename)
                        hair_path = os.path.join(UPLOAD_FOLDER, hair_filename)
                        
                        with open(user_path, 'wb') as f:
                            f.write(user_file['content'])
                        with open(hair_path, 'wb') as f:
                            f.write(hair_file['content'])
                        
                        # Generate result - just a simple merge
                        output_filename = f'result_{uuid.uuid4().hex[:8]}.png'
                        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                        
                        # In demo mode, just copy the user photo
                        import shutil
                        shutil.copy(user_path, output_path)
                        
                        self.send_response(200)
                        self.send_header('Content-type', 'application/json')
                        self.end_headers()
                        response = {
                            'success': True,
                            'result_url': f'/outputs/{output_filename}',
                            'mode': 'demo',
                            'message': '演示模式 - 完整AI功能请配置ComfyUI'
                        }
                        self.wfile.write(json.dumps(response).encode())
                        return
                
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': '上传失败'}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

if __name__ == '__main__':
    PORT = 5000
    print("="*50)
    print("    💇 AI 发型替换工具 (独立演示版)")
    print("="*50)
    print("")
    print("🌐 服务器启动中...")
    print(f"📱 请打开浏览器访问: http://localhost:{PORT}")
    print("")
    print("⚠️  这是纯演示版本，展示界面交互")
    print("   完整 AI 功能请配置 ComfyUI 环境")
    print("="*50)
    try:
        server = HTTPServer(('127.0.0.1', PORT), Handler)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
        server.server_close()
