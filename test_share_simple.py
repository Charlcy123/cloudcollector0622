#!/usr/bin/env python3
"""
简单的分享图片功能测试
"""
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
from datetime import datetime

def create_simple_share_image(cloud_name: str, description: str, tool_icon: str, 
                            captured_at: str, location: str) -> str:
    """创建简单的分享图片"""
    
    # 创建画布 (800x600)
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 尝试使用系统字体，如果没有就使用默认字体
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 32)
        text_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 20)
        small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 16)
    except:
        # 如果找不到中文字体，使用默认字体
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 绘制背景渐变（简单的从上到下的颜色变化）
    for y in range(height):
        # 从浅蓝到白色的渐变
        blue_intensity = int(200 * (1 - y / height))
        color = (blue_intensity + 55, blue_intensity + 55, 255)
        draw.line([(0, y), (width, y)], fill=color)
    
    # 绘制标题区域
    title_y = 50
    title_text = f"{tool_icon} 云彩收集手册"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, title_y), title_text, fill='white', font=title_font)
    
    # 绘制云朵名称
    name_y = 150
    name_bbox = draw.textbbox((0, 0), cloud_name, font=title_font)
    name_width = name_bbox[2] - name_bbox[0]
    name_x = (width - name_width) // 2
    draw.text((name_x, name_y), cloud_name, fill='#2C3E50', font=title_font)
    
    # 绘制描述文字（支持换行）
    desc_y = 220
    desc_lines = []
    words = description.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        test_bbox = draw.textbbox((0, 0), test_line, font=text_font)
        test_width = test_bbox[2] - test_bbox[0]
        
        if test_width <= width - 100:  # 留边距
            current_line = test_line
        else:
            if current_line:
                desc_lines.append(current_line.strip())
            current_line = word + " "
    
    if current_line:
        desc_lines.append(current_line.strip())
    
    # 如果描述太长，只显示前3行
    desc_lines = desc_lines[:3]
    
    for i, line in enumerate(desc_lines):
        line_bbox = draw.textbbox((0, 0), line, font=text_font)
        line_width = line_bbox[2] - line_bbox[0]
        line_x = (width - line_width) // 2
        draw.text((line_x, desc_y + i * 30), line, fill='#34495E', font=text_font)
    
    # 绘制时间和地点信息
    info_y = height - 100
    time_text = f"拍摄时间: {captured_at}"
    location_text = f"拍摄地点: {location}"
    
    draw.text((50, info_y), time_text, fill='#7F8C8D', font=small_font)
    draw.text((50, info_y + 25), location_text, fill='#7F8C8D', font=small_font)
    
    # 绘制底部标识
    footer_text = "云彩收集手册 - 记录天空的每一刻"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=small_font)
    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_x = (width - footer_width) // 2
    draw.text((footer_x, height - 30), footer_text, fill='#95A5A6', font=small_font)
    
    # 保存图片
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"share_{timestamp}.jpg"
    filepath = os.path.join("static", "shares", filename)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    # 保存图片
    img.save(filepath, "JPEG", quality=90)
    
    return f"http://localhost:8000/static/shares/{filename}"

def test_share_image_generation():
    """测试分享图片生成"""
    print("=== 测试分享图片生成功能 ===")
    
    # 测试数据
    test_data = {
        "cloud_name": "飞天葱花云",
        "description": "它正准备飞进月亮里搅拌奶油！预言：今晚你会和星星交换秘密，顺便弄丢了一个苹果核！",
        "tool_icon": "🧹",
        "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": "北京市朝阳区"
    }
    
    try:
        # 生成分享图片
        share_url = create_simple_share_image(**test_data)
        print(f"✅ 分享图片生成成功!")
        print(f"📷 图片URL: {share_url}")
        print(f"📁 本地路径: {share_url.replace('http://localhost:8000/', '')}")
        
        return share_url
        
    except Exception as e:
        print(f"❌ 分享图片生成失败: {str(e)}")
        return None

if __name__ == "__main__":
    test_share_image_generation() 