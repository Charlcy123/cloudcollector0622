#!/usr/bin/env python3
"""
图片上传调试脚本
用于测试云朵识别 API 的文件上传功能
"""

import requests
import base64
import json
from pathlib import Path

def test_upload_with_file(api_url, image_path):
    """测试使用真实文件上传"""
    print(f"=== 测试文件上传 ===")
    print(f"API URL: {api_url}")
    print(f"图片路径: {image_path}")
    
    # 检查文件是否存在
    if not Path(image_path).exists():
        print(f"❌ 错误：文件不存在 {image_path}")
        return False
    
    # 准备上传数据
    files = {
        'file': ('test_cloud.jpg', open(image_path, 'rb'), 'image/jpeg')
    }
    
    data = {
        'tool': 'broom',
        'time': '18:00',
        'location': '上海',
        'weather': '晴天'
    }
    
    try:
        print("发送请求...")
        response = requests.post(api_url, files=files, data=data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 上传成功！")
            result = response.json()
            print(f"云朵名称: {result.get('name')}")
            print(f"描述: {result.get('description')}")
            return True
        else:
            print(f"❌ 上传失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {str(e)}")
        return False
    finally:
        # 关闭文件
        if 'file' in files:
            files['file'][1].close()

def test_upload_with_base64(api_url, image_path):
    """测试使用 base64 编码上传（备用方案）"""
    print(f"\n=== 测试 Base64 上传 ===")
    
    if not Path(image_path).exists():
        print(f"❌ 错误：文件不存在 {image_path}")
        return False
    
    try:
        # 读取并编码图片
        with open(image_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # 使用 /api/cloud/name-from-image 端点
        base64_url = api_url.replace('name-from-image-upload', 'name-from-image')
        
        payload = {
            "tool": "broom",
            "image": image_base64,
            "context": {
                "time": "18:00",
                "location": "上海",
                "weather": "晴天"
            }
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        print("发送 Base64 请求...")
        response = requests.post(base64_url, headers=headers, json=payload, timeout=30)
        
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ Base64 上传成功！")
            result = response.json()
            print(f"云朵名称: {result.get('name')}")
            print(f"描述: {result.get('description')}")
            return True
        else:
            print(f"❌ Base64 上传失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Base64 请求异常: {str(e)}")
        return False

def create_test_image():
    """创建一个测试图片文件"""
    try:
        from PIL import Image, ImageDraw
        
        # 创建一个简单的测试图片
        img = Image.new('RGB', (300, 200), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # 画一些简单的"云朵"
        draw.ellipse([50, 50, 150, 100], fill='white')
        draw.ellipse([120, 60, 220, 110], fill='white')
        draw.ellipse([80, 80, 180, 130], fill='white')
        
        test_path = 'test_cloud_image.jpg'
        img.save(test_path)
        print(f"✅ 创建测试图片: {test_path}")
        return test_path
        
    except ImportError:
        print("❌ PIL 未安装，无法创建测试图片")
        return None

def main():
    # API 配置
    LOCAL_API = "http://127.0.0.1:8000/api/cloud/name-from-image-upload"
    ZEABUR_API = "https://your-zeabur-domain.zeabur.app/api/cloud/name-from-image-upload"  # 替换为你的实际域名
    
    print("🌤️  云朵识别 API 上传测试")
    print("=" * 50)
    
    # 尝试创建测试图片
    test_image = create_test_image()
    
    if not test_image:
        print("请手动提供一个测试图片路径:")
        test_image = input("图片路径: ").strip()
        
        if not test_image:
            print("❌ 未提供图片路径，退出测试")
            return
    
    # 选择测试的 API
    print("\n选择要测试的 API:")
    print("1. 本地 API (127.0.0.1:8000)")
    print("2. Zeabur 部署的 API")
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        api_url = LOCAL_API
    elif choice == "2":
        zeabur_domain = input("请输入你的 Zeabur 域名 (例: xxx.zeabur.app): ").strip()
        if zeabur_domain:
            api_url = f"https://{zeabur_domain}/api/cloud/name-from-image-upload"
        else:
            print("❌ 未提供域名，使用本地 API")
            api_url = LOCAL_API
    else:
        print("使用本地 API")
        api_url = LOCAL_API
    
    # 执行测试
    print(f"\n🚀 开始测试: {api_url}")
    
    success1 = test_upload_with_file(api_url, test_image)
    success2 = test_upload_with_base64(api_url, test_image)
    
    print(f"\n📊 测试结果:")
    print(f"文件上传: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"Base64上传: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if not success1 and not success2:
        print("\n💡 调试建议:")
        print("1. 检查 API 服务是否正常运行")
        print("2. 检查图片文件是否存在且可读")
        print("3. 检查网络连接")
        print("4. 查看服务器日志获取更多信息")

if __name__ == "__main__":
    main() 