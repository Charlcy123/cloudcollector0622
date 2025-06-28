#!/usr/bin/env python3
"""
测试分享图片生成功能
"""
import requests
import json
import base64
from datetime import datetime
from PIL import Image
import io

# API基础URL
BASE_URL = "http://localhost:8000"

def create_test_image_base64():
    """创建一个测试图片的base64数据"""
    # 创建一个简单的测试图片
    img = Image.new('RGB', (200, 150), color='lightblue')
    
    # 在图片上添加一些内容
    from PIL import ImageDraw
    draw = ImageDraw.Draw(img)
    draw.rectangle([50, 50, 150, 100], fill='white', outline='blue', width=2)
    draw.text((70, 70), "Test Cloud", fill='black')
    
    # 转换为base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_data = buffer.getvalue()
    img_base64 = base64.b64encode(img_data).decode('utf-8')
    
    return f"data:image/png;base64,{img_base64}"

def test_share_image():
    """测试分享图片生成"""
    print("=== 测试分享图片生成功能 ===")
    
    # 创建测试图片
    test_image_base64 = create_test_image_base64()
    print(f"测试图片base64长度: {len(test_image_base64)}")
    
    # 测试数据
    test_data = {
        "image_url": test_image_base64,
        "cloud_name": "测试云朵",
        "description": "这是一个用来测试分享图片生成功能的云朵，它看起来像一团棉花糖，软软的，很想戳一下。",
        "tool_icon": "🧹",
        "captured_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": "北京市朝阳区"
    }
    
    try:
        # 发送请求
        print(f"发送请求到: {BASE_URL}/api/share/generate")
        print(f"请求数据: {json.dumps({**test_data, 'image_url': test_data['image_url'][:50] + '...'}, ensure_ascii=False, indent=2)}")
        
        response = requests.post(
            f"{BASE_URL}/api/share/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 分享图片生成成功!")
            print(f"分享图片URL: {result['share_image_url']}")
            
            # 尝试访问生成的图片
            img_response = requests.get(result['share_image_url'])
            if img_response.status_code == 200:
                print(f"✅ 分享图片可以正常访问，大小: {len(img_response.content)} bytes")
            else:
                print(f"❌ 分享图片无法访问，状态码: {img_response.status_code}")
                
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_share_image() 