#!/usr/bin/env python3
"""
专门测试字体渲染问题
"""
from PIL import Image, ImageDraw, ImageFont
import os

def test_different_fonts():
    """测试不同字体的渲染效果"""
    print("=== 测试不同字体渲染效果 ===")
    
    # 创建测试画布
    canvas = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(canvas)
    
    # 测试文字
    test_text = "🧹 测试云朵名称"
    
    # 字体列表
    font_tests = [
        ("默认字体", None),
        ("PingFang", "/System/Library/Fonts/PingFang.ttc"),
        ("Helvetica", "/System/Library/Fonts/Helvetica.ttc"),
        ("Arial", "/System/Library/Fonts/Arial.ttf"),
        ("Times", "/System/Library/Fonts/Times.ttc"),
    ]
    
    y_pos = 50
    
    for font_name, font_path in font_tests:
        print(f"\n--- 测试字体: {font_name} ---")
        
        # 加载字体
        font = None
        if font_path is None:
            font = ImageFont.load_default()
            print("✅ 使用默认字体")
        elif os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 24)
                print(f"✅ 字体加载成功: {font_path}")
            except Exception as e:
                print(f"❌ 字体加载失败: {str(e)}")
                font = ImageFont.load_default()
        else:
            print(f"❌ 字体文件不存在: {font_path}")
            font = ImageFont.load_default()
        
        # 绘制背景矩形
        draw.rectangle([50, y_pos - 5, 750, y_pos + 35], fill='lightgray', outline='black')
        
        # 绘制文字标签
        draw.text((60, y_pos), f"{font_name}:", fill='black', font=font)
        
        # 绘制测试文字
        try:
            # 计算文字宽度
            bbox = draw.textbbox((0, 0), test_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # 绘制文字
            draw.text((200, y_pos), test_text, fill='blue', font=font)
            
            # 绘制文字边界框
            draw.rectangle([200, y_pos, 200 + text_width, y_pos + text_height], 
                         fill=None, outline='red', width=1)
            
            print(f"✅ 文字绘制成功，宽度: {text_width}, 高度: {text_height}")
            
        except Exception as e:
            print(f"❌ 文字绘制失败: {str(e)}")
            # 尝试简单绘制
            draw.text((200, y_pos), test_text, fill='red', font=font)
        
        y_pos += 60
    
    # 保存测试图片
    test_path = "static/shares/font_comparison.jpg"
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    canvas.save(test_path, 'JPEG', quality=90)
    print(f"\n📷 字体对比图片已保存: {test_path}")
    
    return test_path

def test_simple_text_rendering():
    """测试最简单的文字渲染"""
    print("\n=== 测试最简单的文字渲染 ===")
    
    # 创建简单画布
    canvas = Image.new('RGB', (400, 300), color='white')
    draw = ImageDraw.Draw(canvas)
    
    # 使用默认字体
    font = ImageFont.load_default()
    
    # 绘制简单文字
    texts = [
        ("Hello World", 'black'),
        ("测试中文", 'red'),
        ("🧹 Emoji Test", 'blue'),
        ("Mixed 混合 🌟", 'green')
    ]
    
    y_pos = 50
    for text, color in texts:
        try:
            draw.text((50, y_pos), text, fill=color, font=font)
            print(f"✅ 文字 '{text}' 绘制成功")
        except Exception as e:
            print(f"❌ 文字 '{text}' 绘制失败: {str(e)}")
        y_pos += 40
    
    # 保存测试图片
    simple_path = "static/shares/simple_text_test.jpg"
    canvas.save(simple_path, 'JPEG', quality=90)
    print(f"📷 简单文字测试图片已保存: {simple_path}")
    
    return simple_path

def test_share_image_minimal():
    """测试最小化的分享图片生成"""
    print("\n=== 测试最小化分享图片生成 ===")
    
    # 创建画布
    canvas = Image.new('RGB', (800, 800), color='white')
    draw = ImageDraw.Draw(canvas)
    
    # 使用默认字体
    font = ImageFont.load_default()
    
    # 绘制标题背景
    draw.rectangle([0, 0, 800, 40], fill='lightblue')
    
    # 绘制标题文字 - 使用最简单的方法
    title_text = "测试云朵"
    draw.text((50, 10), title_text, fill='black', font=font)
    print("✅ 标题绘制完成")
    
    # 绘制原图区域（用颜色块代替）
    draw.rectangle([50, 50, 750, 550], fill='lightgreen', outline='gray', width=2)
    draw.text((350, 300), "原图区域", fill='black', font=font)
    print("✅ 原图区域绘制完成")
    
    # 绘制描述文字
    desc_text = "这是一个测试描述"
    draw.text((50, 570), desc_text, fill='darkblue', font=font)
    print("✅ 描述绘制完成")
    
    # 绘制底部背景
    draw.rectangle([0, 740, 800, 800], fill='lightgray')
    
    # 绘制底部信息
    time_text = "时间: 2025-06-28 11:17:32"
    location_text = "地点: 测试地点"
    brand_text = "云彩收集手册"
    
    draw.text((20, 750), time_text, fill='black', font=font)
    draw.text((20, 770), location_text, fill='black', font=font)
    draw.text((600, 760), brand_text, fill='gray', font=font)
    print("✅ 底部信息绘制完成")
    
    # 保存图片
    minimal_path = "static/shares/minimal_share_test.jpg"
    canvas.save(minimal_path, 'JPEG', quality=90)
    print(f"📷 最小化分享图片已保存: {minimal_path}")
    
    return minimal_path

def main():
    """主函数"""
    print("🔍 开始测试字体渲染问题\n")
    
    # 1. 测试不同字体
    font_comparison_path = test_different_fonts()
    
    # 2. 测试简单文字渲染
    simple_text_path = test_simple_text_rendering()
    
    # 3. 测试最小化分享图片
    minimal_share_path = test_share_image_minimal()
    
    print(f"\n🎯 测试完成！生成的图片：")
    print(f"   字体对比: {font_comparison_path}")
    print(f"   简单文字: {simple_text_path}")
    print(f"   最小分享: {minimal_share_path}")
    
    print(f"\n💡 请检查这些图片，看看文字是否正确显示")
    print(f"   如果这些测试图片都能正常显示文字，说明字体本身没问题")
    print(f"   问题可能在于分享图片生成的具体逻辑")

if __name__ == "__main__":
    main() 