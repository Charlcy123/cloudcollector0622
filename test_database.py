#!/usr/bin/env python3
"""
直接查询数据库中的云朵收藏数据
"""

import requests
import json

def test_database_directly():
    """使用后端API直接查询数据库"""
    
    print("=== 测试数据库查询 ===")
    base_url = "http://localhost:8000"
    
    # 目标用户ID
    target_user_id = "908182e6-17da-4a6f-9ea0-fccacaa06188"
    
    try:
        # 1. 使用老版本的API查询（不需要JWT认证）
        print("1. 测试老版本API...")
        old_api_url = f"{base_url}/api/users/{target_user_id}/cloud-collections"
        response = requests.get(old_api_url)
        
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   收藏数量: {data.get('total', 0)}")
            print(f"   收藏列表: {len(data.get('collections', []))}")
            
            if data.get('collections'):
                print("   最近的收藏:")
                for i, collection in enumerate(data['collections'][:3]):
                    print(f"     {i+1}. {collection['cloud_name']} (ID: {collection['id']})")
        else:
            print(f"   错误: {response.text}")
            
    except Exception as e:
        print(f"   错误: {e}")
    
    print("\n" + "="*50)
    
    try:
        # 2. 查询所有用户的收藏统计
        print("2. 查询所有用户收藏统计...")
        
        # 这个需要遍历一些用户ID来查看是否有数据
        test_user_ids = [
            target_user_id,
            "test-user-1",
            "test-user-2"
        ]
        
        for user_id in test_user_ids:
            url = f"{base_url}/api/users/{user_id}/cloud-collections?page_size=1"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                total = data.get('total', 0)
                if total > 0:
                    print(f"   用户 {user_id}: {total} 个收藏")
            
    except Exception as e:
        print(f"   错误: {e}")

if __name__ == "__main__":
    test_database_directly() 