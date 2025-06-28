#!/usr/bin/env python3
"""
调试分享图片文字渲染问题
"""
from PIL import Image, ImageDraw, ImageFont
import os
import io
import base64

def test_font_rendering():
    """测试字体渲染功能"""
    print("=== 测试字体渲染功能 ===")
    
    # 创建测试画布
    canvas = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(canvas)
    
    # 测试文字
    test_texts = [
        "🧹 测试云朵",
        "这是一个测试描述",
        "📅 2025-06-28 11:17:32",
        "📍 北京市朝阳区",
        "云彩收集手册"
    ]
    
    # 尝试加载字体
    font_paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Helvetica.ttc", 
        "/System/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/Times.ttc"
    ]
    
    loaded_font = None
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                loaded_font = ImageFont.truetype(font_path, 24)
                print(f"✅ 成功加载字体: {font_path}")
                break
            except Exception as e:
                print(f"❌ 字体加载失败 {font_path}: {str(e)}")
    
    if not loaded_font:
        print("⚠️ 使用默认字体")
        loaded_font = ImageFont.load_default()
    
    # 绘制测试文字
    y_pos = 50
    for i, text in enumerate(test_texts):
        try:
            # 测试文字边界框
            bbox = draw.textbbox((0, 0), text, font=loaded_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 绘制背景矩形
            draw.rectangle([50, y_pos - 5, 50 + text_width + 10, y_pos + text_height + 5], 
                         fill='lightblue', outline='blue')
            
            # 绘制文字
            draw.text((55, y_pos), text, fill='black', font=loaded_font)
            
            print(f"✅ 文字 '{text}' 绘制成功，宽度: {text_width}, 高度: {text_height}")
            y_pos += 60
            
        except Exception as e:
            print(f"❌ 文字 '{text}' 绘制失败: {str(e)}")
            y_pos += 60
    
    # 保存测试图片
    test_path = "static/shares/font_test.jpg"
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    canvas.save(test_path, 'JPEG', quality=90)
    print(f"📷 字体测试图片已保存: {test_path}")
    
    return test_path

def analyze_existing_share_image(image_path):
    """分析现有的分享图片"""
    print(f"\n=== 分析现有分享图片: {image_path} ===")
    
    if not os.path.exists(image_path):
        print(f"❌ 图片文件不存在: {image_path}")
        return
    
    try:
        img = Image.open(image_path)
        print(f"📏 图片尺寸: {img.size}")
        print(f"🎨 图片模式: {img.mode}")
        print(f"📁 文件大小: {os.path.getsize(image_path)} bytes")
        
        # 转换为RGB模式进行分析
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 检查图片的像素颜色分布
        colors = img.getcolors(maxcolors=256*256*256)
        if colors:
            print(f"🌈 图片包含 {len(colors)} 种不同颜色")
            # 显示最常见的几种颜色
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)[:5]
            print("🎯 最常见的颜色:")
            for count, color in sorted_colors:
                print(f"   颜色 {color}: {count} 像素")
        
        # 检查是否有文字区域（通过检查特定区域的颜色变化）
        # 检查顶部标题区域 (0, 0, width, 50)
        title_region = img.crop((0, 0, img.width, 50))
        title_colors = title_region.getcolors(maxcolors=256*256*256)
        print(f"📝 标题区域包含 {len(title_colors) if title_colors else 0} 种颜色")
        
        # 检查底部信息区域
        bottom_region = img.crop((0, img.height-60, img.width, img.height))
        bottom_colors = bottom_region.getcolors(maxcolors=256*256*256)
        print(f"📍 底部区域包含 {len(bottom_colors) if bottom_colors else 0} 种颜色")
        
    except Exception as e:
        print(f"❌ 分析图片失败: {str(e)}")

def test_simple_share_generation():
    """测试简单的分享图片生成"""
    print("\n=== 测试简单分享图片生成 ===")
    
    # 创建一个简单的原图
    original_img = Image.new('RGB', (400, 300), color='lightblue')
    original_draw = ImageDraw.Draw(original_img)
    original_draw.text((150, 140), "原始云朵图片", fill='white')
    
    # 转换为base64
    buffer = io.BytesIO()
    original_img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    img_base64 = base64.b64encode(img_data).decode('utf-8')
    original_image_url = f"data:image/png;base64,{img_base64}"
    
    # 模拟分享图片生成逻辑
    canvas_size = (800, 800)
    canvas = Image.new('RGB', canvas_size, color='white')
    
    # 调整原图尺寸
    new_width, new_height = 700, 525  # 保持4:3比例
    resized_image = original_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # 粘贴原图
    paste_x = (canvas_size[0] - new_width) // 2
    paste_y = 50
    canvas.paste(resized_image, (paste_x, paste_y))
    
    # 创建绘图对象
    draw = ImageDraw.Draw(canvas)
    
    # 加载字体
    font = None
    font_paths = ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Helvetica.ttc"]
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 24)
                print(f"✅ 使用字体: {font_path}")
                break
            except:
                continue
    
    if not font:
        font = ImageFont.load_default()
        print("⚠️ 使用默认字体")
    
    # 绘制各个文字元素
    # 1. 标题背景
    draw.rectangle([0, 0, canvas_size[0], 40], fill='#f8f9fa')
    
    # 2. 标题文字
    title_text = "🧹 测试云朵名称"
    try:
        title_bbox = draw.textbbox((0, 0), title_text, font=font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (canvas_size[0] - title_width) // 2
        draw.text((title_x, 8), title_text, fill='#2d3748', font=font)
        print(f"✅ 标题绘制成功: {title_text}")
    except Exception as e:
        print(f"❌ 标题绘制失败: {str(e)}")
        draw.text((50, 8), title_text, fill='#2d3748', font=font)
    
    # 3. 描述文字
    desc_text = "这是一个测试描述文字，用来验证文字是否正确显示。"
    desc_y = paste_y + new_height + 20
    try:
        desc_bbox = draw.textbbox((0, 0), desc_text, font=font)
        desc_width = desc_bbox[2] - desc_bbox[0]
        desc_x = (canvas_size[0] - desc_width) // 2
        draw.text((desc_x, desc_y), desc_text, fill='#4a5568', font=font)
        print(f"✅ 描述绘制成功")
    except Exception as e:
        print(f"❌ 描述绘制失败: {str(e)}")
        draw.text((20, desc_y), desc_text, fill='#4a5568', font=font)
    
    # 4. 底部信息
    bottom_y = canvas_size[1] - 60
    draw.rectangle([0, bottom_y, canvas_size[0], canvas_size[1]], fill='#f7fafc')
    
    time_text = "📅 2025-06-28 11:17:32"
    location_text = "📍 测试地点"
    brand_text = "云彩收集手册"
    
    try:
        draw.text((20, bottom_y + 10), time_text, fill='#718096', font=font)
        draw.text((20, bottom_y + 30), location_text, fill='#718096', font=font)
        draw.text((canvas_size[0] - 120, bottom_y + 20), brand_text, fill='#a0aec0', font=font)
        print("✅ 底部信息绘制成功")
    except Exception as e:
        print(f"❌ 底部信息绘制失败: {str(e)}")
    
    # 保存测试图片
    test_path = "static/shares/debug_test.jpg"
    canvas.save(test_path, 'JPEG', quality=90)
    print(f"📷 调试测试图片已保存: {test_path}")
    
    return test_path

def main():
    """主函数"""
    print("🔍 开始调试分享图片文字渲染问题\n")
    
    # 1. 测试字体渲染
    font_test_path = test_font_rendering()
    
    # 2. 分析现有的分享图片
    existing_images = [
        "static/shares/share_4f414c5b.jpg",
        "static/shares/share_124475c8.jpg",
        "static/shares/share_da7d42e9.jpg"
    ]
    
    for img_path in existing_images:
        if os.path.exists(img_path):
            analyze_existing_share_image(img_path)
    
    # 3. 测试简单的分享图片生成
    debug_test_path = test_simple_share_generation()
    
    print(f"\n🎯 调试完成！请检查以下测试图片：")
    print(f"   字体测试: {font_test_path}")
    print(f"   调试测试: {debug_test_path}")
    print(f"\n💡 建议：")
    print(f"   1. 在浏览器中访问: http://localhost:8000/{font_test_path}")
    print(f"   2. 在浏览器中访问: http://localhost:8000/{debug_test_path}")
    print(f"   3. 对比这些图片与实际生成的分享图片")

if __name__ == "__main__":
    main() 