# components/image_handler.py
import os
from PIL import Image
from typing import List


class ImageHandler:
    """图片处理器"""

    @staticmethod
    def get_tab_images(tab_folder: str) -> List[str]:
        """获取吉他谱所有图片文件"""
        images = []
        source_path = f"source/{tab_folder}"
        if os.path.exists(source_path):
            for filename in sorted(os.listdir(source_path)):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    images.append(os.path.join(source_path, filename))
        return images

    @staticmethod
    def count_tab_pages(tab_folder: str) -> int:
        """计算吉他谱总页数"""
        count = 0
        source_path = f"source/{tab_folder}"
        if os.path.exists(source_path):
            for filename in os.listdir(source_path):
                if filename.lower().endswith('.png'):
                    try:
                        page_num = int(filename.split('.')[0])
                        count = max(count, page_num)
                    except ValueError:
                        pass
        return count

    @staticmethod
    def resize_image(image_path: str, max_width: int, max_height: int) -> Image.Image:
        """调整图片大小"""
        try:
            img = Image.open(image_path)
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return img
        except Exception as e:
            print(f"调整图片大小出错: {e}")
            return None

    @staticmethod
    def create_combined_image(tab_folder: str) -> str:
        """创建合并的长图用于全屏显示"""
        try:
            # 获取所有图片路径
            source_path = f"source/{tab_folder}"
            if not os.path.exists(source_path):
                return ""

            # 获取所有PNG图片并按数字排序
            image_files = []
            for filename in sorted(os.listdir(source_path)):
                if filename.lower().endswith('.png'):
                    try:
                        # 按页码排序
                        page_num = int(filename.split('.')[0])
                        image_files.append((page_num, os.path.join(source_path, filename)))
                    except ValueError:
                        image_files.append((filename, os.path.join(source_path, filename)))

            # 按页码排序
            image_files.sort(key=lambda x: x[0])
            image_paths = [path for _, path in image_files]

            if not image_paths:
                return ""

            # 加载所有图片
            images = []
            for path in image_paths:
                try:
                    img = Image.open(path)
                    # 转换为RGB模式（防止RGBA模式合并出错）
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    images.append(img)
                except Exception as e:
                    print(f"打开图片 {path} 出错: {e}")
                    continue

            if not images:
                return ""

            # 计算合并后图片的尺寸
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)

            # 创建新图片
            combined_img = Image.new('RGB', (max_width, total_height), 'white')

            # 粘贴图片
            y_offset = 0
            for img in images:
                # 居中放置图片
                x_offset = (max_width - img.width) // 2
                combined_img.paste(img, (x_offset, y_offset))
                y_offset += img.height

            # 保存到临时文件
            temp_path = f"source/{tab_folder}/combined_fullscreen.png"
            combined_img.save(temp_path, 'PNG')
            return temp_path
        except Exception as e:
            print(f"创建合并图片出错: {e}")
            return ""
