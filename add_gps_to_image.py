#!/usr/bin/env python3
"""
给图片添加GPS信息的测试工具
"""

import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS
import piexif

def add_gps_to_image(input_path, output_path, latitude, longitude):
    """给图片添加GPS信息"""
    try:
        # 打开原图片
        image = Image.open(input_path)
        
        # 转换GPS坐标为EXIF格式
        def decimal_to_dms(decimal_degree):
            """将十进制度数转换为度分秒格式"""
            degrees = int(abs(decimal_degree))
            minutes_float = (abs(decimal_degree) - degrees) * 60
            minutes = int(minutes_float)
            seconds = (minutes_float - minutes) * 60
            
            return ((degrees, 1), (minutes, 1), (int(seconds * 1000), 1000))
        
        # 准备GPS数据
        lat_dms = decimal_to_dms(latitude)
        lon_dms = decimal_to_dms(longitude)
        lat_ref = 'N' if latitude >= 0 else 'S'
        lon_ref = 'E' if longitude >= 0 else 'W'
        
        # 创建EXIF数据
        exif_dict = {
            "0th": {},
            "Exif": {},
            "GPS": {
                piexif.GPSIFD.GPSLatitude: lat_dms,
                piexif.GPSIFD.GPSLatitudeRef: lat_ref,
                piexif.GPSIFD.GPSLongitude: lon_dms,
                piexif.GPSIFD.GPSLongitudeRef: lon_ref,
                piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0)
            },
            "1st": {},
            "thumbnail": None
        }
        
        # 添加拍摄时间
        from datetime import datetime
        now = datetime.now()
        datetime_str = now.strftime("%Y:%m:%d %H:%M:%S")
        exif_dict["0th"][piexif.ImageIFD.DateTime] = datetime_str
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = datetime_str
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = datetime_str
        
        # 转换为字节
        exif_bytes = piexif.dump(exif_dict)
        
        # 保存图片
        image.save(output_path, exif=exif_bytes)
        
        print(f"✅ 成功给图片添加GPS信息:")
        print(f"   输入: {input_path}")
        print(f"   输出: {output_path}")
        print(f"   GPS: {latitude}, {longitude}")
        print(f"   时间: {datetime_str}")
        
        return True
        
    except Exception as e:
        print(f"❌ 添加GPS信息失败: {str(e)}")
        return False

def main():
    """主函数"""
    if len(sys.argv) != 5:
        print("使用方法: python add_gps_to_image.py <输入图片> <输出图片> <纬度> <经度>")
        print("例如: python add_gps_to_image.py input.jpg output.jpg 39.9042 116.4074")
        print("(上面的坐标是北京天安门)")
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    
    try:
        latitude = float(sys.argv[3])
        longitude = float(sys.argv[4])
    except ValueError:
        print("❌ 纬度和经度必须是数字")
        return
    
    if not os.path.exists(input_path):
        print(f"❌ 输入文件不存在: {input_path}")
        return
    
    add_gps_to_image(input_path, output_path, latitude, longitude)

if __name__ == "__main__":
    main() 