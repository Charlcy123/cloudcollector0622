#!/usr/bin/env python3
"""
测试描述长度的脚本
"""

import requests
import json
import base64

def test_api_description_length():
    print("=== 测试API描述长度 ===")
    
    # 测试数据 - 使用不需要图片的API
    url = "http://localhost:8000/api/cloud/name"
    
    test_data = {
        "tool": "broom",
        "imageFeatures": {
            "shape": "积云",
            "color": "白色",
            "texture": "蓬松"
        },
        "context": {
            "time": "2025-01-26T13:00:00.000Z",
            "weather": "晴天",
            "location": "测试地点"
        }
    }
    
    try:
        print("发送请求...")
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== API响应结果 ===")
            print(f"名称: {result.get('name', 'N/A')}")
            print(f"描述: {result.get('description', 'N/A')}")
            print(f"描述长度: {len(result.get('description', ''))}")
            print(f"风格: {result.get('style', 'N/A')}")
            
            # 检查是否被截断
            description = result.get('description', '')
            if len(description) > 0:
                print(f"\n=== 描述详细信息 ===")
                print(f"首50字符: {description[:50]}")
                print(f"末50字符: {description[-50:]}")
                print(f"是否以省略号结尾: {'是' if description.endswith('...') or description.endswith('。') else '否'}")
                
                # 检查是否看起来被截断了
                if len(description) < 20:
                    print("⚠️  描述太短，可能被截断")
                elif not (description.endswith('！') or description.endswith('。') or description.endswith('？')):
                    print("⚠️  描述没有完整的结尾标点，可能被截断")
                else:
                    print("✅ 描述看起来是完整的")
                    
                # 测试多次，看看是否一致
                print(f"\n=== 多次测试验证 ===")
                for i in range(3):
                    test_response = requests.post(url, json=test_data, timeout=30)
                    if test_response.status_code == 200:
                        test_result = test_response.json()
                        test_desc = test_result.get('description', '')
                        print(f"测试{i+1}: 长度={len(test_desc)}, 描述={test_desc[:30]}...")
            
        else:
            print(f"请求失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {str(e)}")

if __name__ == "__main__":
    test_api_description_length() 