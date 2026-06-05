import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
import io
import os

class SimpleHairstyleTransfer:
    """简易发型替换工具 - 用于演示和当 ComfyUI 不可用时"""
    
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
    def detect_face_landmarks(self, image):
        """检测人脸关键点"""
        with self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        ) as face_mesh:
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if not results.multi_face_landmarks:
                return None
            return results.multi_face_landmarks[0]
    
    def get_hair_region(self, image, landmarks):
        """根据人脸关键点估计头发区域"""
        h, w = image.shape[:2]
        points = []
        
        # 额头区域的关键点
        forehead_indices = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162]
        
        for idx in forehead_indices:
            pt = landmarks.landmark[idx]
            points.append([int(pt.x * w), int(pt.y * h)])
        
        points = np.array(points, dtype=np.int32)
        
        # 创建头发区域掩码 - 扩展到头顶
        mask = np.zeros((h, w), dtype=np.uint8)
        x, y, w_rect, h_rect = cv2.boundingRect(points)
        
        # 扩展到头顶
        hair_top = max(0, y - h_rect // 2)
        hair_height = h_rect + (y - hair_top)
        
        # 创建椭圆掩码近似头发区域
        center_x = x + w_rect // 2
        center_y = hair_top + hair_height // 3
        axes_x = w_rect // 2 + 20
        axes_y = hair_height // 2 + 30
        
        cv2.ellipse(mask, (center_x, center_y), (axes_x, axes_y), 0, 0, 360, 255, -1)
        
        return mask, (x, hair_top, w_rect, hair_height + 20)
    
    def transfer_hairstyle(self, user_img_path, hairstyle_img_path, output_path):
        """简化的发型替换 - 主要用于演示"""
        # 读取图片
        user_img = cv2.imread(user_img_path)
        hair_img = cv2.imread(hairstyle_img_path)
        
        if user_img is None or hair_img is None:
            return False
        
        # 调整大小
        target_height = 512
        user_img = cv2.resize(user_img, (int(user_img.shape[1] * target_height / user_img.shape[0]), target_height))
        
        # 检测人脸
        landmarks = self.detect_face_landmarks(user_img)
        
        if landmarks is not None:
            # 获取头发区域
            hair_mask, (x, y, w, h) = self.get_hair_region(user_img, landmarks)
            
            # 调整发型图片大小
            hair_resized = cv2.resize(hair_img, (w, h))
            
            # 创建混合效果
            hair_mask_cropped = hair_mask[y:y+h, x:x+w]
            hair_mask_3ch = cv2.cvtColor(hair_mask_cropped, cv2.COLOR_GRAY2BGR) / 255.0
            
            # 确保区域在图像范围内
            if y + h <= user_img.shape[0] and x + w <= user_img.shape[1]:
                user_roi = user_img[y:y+h, x:x+w]
                
                # 颜色匹配 - 简单的色彩转移
                hair_resized = self.color_transfer(hair_resized, user_roi)
                
                # 泊松融合
                center = (x + w // 2, y + h // 2)
                try:
                    result = cv2.seamlessClone(
                        hair_resized, user_img, hair_mask_cropped, center, cv2.NORMAL_CLONE
                    )
                except:
                    # 如果融合失败，使用简单混合
                    result = user_img.copy()
                    mixed = (hair_resized * 0.7 + user_roi * 0.3).astype(np.uint8)
                    result[y:y+h, x:x+w] = mixed
                    
                cv2.imwrite(output_path, result)
                return True
        
        # 如果没有检测到人脸或融合失败，创建一个简单的合成效果
        result = self.simple_composite(user_img, hair_img)
        cv2.imwrite(output_path, result)
        return True
    
    def color_transfer(self, source, target):
        """简单的颜色迁移"""
        source_lab = cv2.cvtColor(source, cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target, cv2.COLOR_BGR2LAB).astype(np.float32)
        
        src_mean, src_std = cv2.meanStdDev(source_lab)
        tgt_mean, tgt_std = cv2.meanStdDev(target_lab)
        
        result_lab = ((source_lab - src_mean.reshape(1, 1, 3)) * (tgt_std / src_std).reshape(1, 1, 3)) + tgt_mean.reshape(1, 1, 3)
        result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
        
        return cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
    
    def simple_composite(self, user_img, hair_img):
        """简单的图像合成"""
        h, w = user_img.shape[:2]
        hair_resized = cv2.resize(hair_img, (w, int(h * 0.4)))
        
        result = user_img.copy()
        
        # 把发型图片放在顶部
        hair_h = hair_resized.shape[0]
        if hair_h <= result.shape[0]:
            # 半透明叠加
            alpha = 0.6
            result[:hair_h, :] = cv2.addWeighted(result[:hair_h, :], 1 - alpha, hair_resized, alpha, 0)
        
        return result

def get_image_processor():
    return SimpleHairstyleTransfer()
