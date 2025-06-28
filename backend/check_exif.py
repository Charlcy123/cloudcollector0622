#!/usr/bin/env python3
"""
检查图片EXIF信息的简单脚本
"""

import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def check_image_exif(image_path):
    """检查单张图片的EXIF信息"""
    try:
        print(f"\n=== 检查图片: {os.path.basename(image_path)} ===")
        
        # 打开图片
        image = Image.open(image_path)
        
        # 获取EXIF数据
        exif_data = image._getexif()
        
        if not exif_data:
            print("❌ 该图片没有EXIF数据")
            return False
        
        print("✅ 图片包含EXIF数据")
        
        has_gps = False
        has_datetime = False
        
        # 遍历EXIF数据
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            
            # 检查GPS信息
            if tag_name == 'GPSInfo':
                has_gps = True
                print("🌍 发现GPS信息:")
                for gps_tag, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    print(f"  {gps_tag_name}: {gps_value}")
            
            # 检查拍摄时间
            elif tag_name in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                has_datetime = True
                print(f"📅 拍摄时间 ({tag_name}): {value}")
            
            # 检查相机信息
            elif tag_name in ['Make', 'Model']:
                print(f"📱 设备信息 ({tag_name}): {value}")
        
        if not has_gps:
            print("❌ 没有GPS位置信息")
        
        if not has_datetime:
            print("❌ 没有拍摄时间信息")
        
        return has_gps
        
    except Exception as e:
        print(f"❌ 检查图片失败: {str(e)}")
        return False

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法: python check_exif.py <图片文件路径>")
        print("或者: python check_exif.py <包含图片的文件夹路径>")
        return
    
    path = sys.argv[1]
    
    if os.path.isfile(path):
        # 检查单个文件
        check_image_exif(path)
    elif os.path.isdir(path):
        # 检查文件夹中的所有图片
        image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif'}
        found_gps = False
        
        print(f"扫描文件夹: {path}")
        
        for filename in os.listdir(path):
            file_path = os.path.join(path, filename)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(filename.lower())
                if ext in image_extensions:
                    if check_image_exif(file_path):
                        found_gps = True
        
        if found_gps:
            print("\n🎉 找到包含GPS信息的图片！")
        else:
            print("\n😔 没有找到包含GPS信息的图片")
    else:
        print(f"❌ 路径不存在: {path}")

if __name__ == "__main__":
    main() 