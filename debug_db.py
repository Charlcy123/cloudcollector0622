#!/usr/bin/env python3
"""
直接查询Supabase数据库，检查cloud_collections表中的数据
"""

import os
from supabase import create_client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化Supabase客户端
supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
supabase_service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    print("❌ 缺少Supabase环境变量")
    print("请检查环境变量 NEXT_PUBLIC_SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY")
    print(f"当前 NEXT_PUBLIC_SUPABASE_URL: {supabase_url}")
    print(f"当前 SUPABASE_SERVICE_ROLE_KEY: {'已设置' if supabase_service_key else '未设置'}")
    exit(1)

supabase = create_client(supabase_url, supabase_service_key)

def main():
    print("🔍 开始查询Supabase数据库...")
    print(f"📡 连接到: {supabase_url}")
    
    try:
        # 1. 查询所有用户
        print("\n👥 查询所有用户:")
        users_result = supabase.table("users").select("id, email, created_at").execute()
        print(f"用户总数: {len(users_result.data)}")
        for user in users_result.data:
            print(f"  - {user['id']} | {user.get('email', '匿名')} | {user['created_at']}")
        
        # 2. 查询所有云朵收藏
        print("\n☁️ 查询所有云朵收藏:")
        collections_result = supabase.table("cloud_collections").select("""
            id, user_id, cloud_name, capture_time, created_at,
            tool:capture_tools(name, emoji)
        """).execute()
        
        print(f"云朵收藏总数: {len(collections_result.data)}")
        for collection in collections_result.data:
            tool_name = collection.get('tool', {}).get('name', '未知工具') if collection.get('tool') else '未知工具'
            tool_emoji = collection.get('tool', {}).get('emoji', '❓') if collection.get('tool') else '❓'
            print(f"  - {collection['id']}")
            print(f"    用户: {collection['user_id']}")
            print(f"    名称: {collection['cloud_name']}")
            print(f"    工具: {tool_emoji} {tool_name}")
            print(f"    时间: {collection['capture_time']}")
            print()
        
        # 3. 按用户分组统计
        print("\n📊 按用户分组统计:")
        user_stats = {}
        for collection in collections_result.data:
            user_id = collection['user_id']
            if user_id not in user_stats:
                user_stats[user_id] = 0
            user_stats[user_id] += 1
        
        for user_id, count in user_stats.items():
            # 查找用户邮箱
            user_email = "未知"
            for user in users_result.data:
                if user['id'] == user_id:
                    user_email = user.get('email', '匿名用户')
                    break
            print(f"  - {user_id} ({user_email}): {count} 个收藏")
        
        # 4. 检查特定用户ID的数据
        target_user_ids = [
            "248b8c2b-09be-443e-99bf-ef53dc48abee",  # 保存时的用户ID
            "908182e6-17da-4a6f-9ea0-fccacaa06188"   # 查询时的用户ID
        ]
        
        print("\n🎯 检查特定用户ID的数据:")
        for user_id in target_user_ids:
            result = supabase.table("cloud_collections").select("*").eq("user_id", user_id).execute()
            print(f"  - 用户 {user_id}: {len(result.data)} 个收藏")
            for collection in result.data:
                print(f"    └─ {collection['cloud_name']} ({collection['created_at']})")
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")

if __name__ == "__main__":
    main() 