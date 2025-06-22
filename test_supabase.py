#!/usr/bin/env python3
"""
Supabase连接测试脚本
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载环境变量
load_dotenv()

def test_supabase_connection():
    """测试Supabase连接"""
    print("=== Supabase连接测试 ===")
    
    # 获取环境变量
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    supabase_anon_key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"Supabase URL: {supabase_url}")
    print(f"匿名密钥存在: {'是' if supabase_anon_key else '否'}")
    print(f"服务密钥存在: {'是' if supabase_service_key else '否'}")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ 缺少必要的环境变量")
        return False
    
    try:
        print("\n--- 测试匿名客户端连接 ---")
        # 创建匿名客户端 - 使用与main.py相同的配置
        try:
            supabase_client = create_client(
                supabase_url, 
                supabase_anon_key,
                options={
                    "schema": "public",
                    "headers": {},
                    "auto_refresh_token": True,
                    "persist_session": True
                }
            )
            print("✅ 匿名客户端创建成功（完整配置）")
        except Exception as e:
            print(f"⚠️ 完整配置失败，尝试简化配置: {str(e)}")
            # 备用方案：最简配置
            supabase_client = create_client(supabase_url, supabase_anon_key)
            print("✅ 匿名客户端创建成功（简化配置）")
        
        # 测试简单查询
        print("测试查询capture_tools表...")
        result = supabase_client.table("capture_tools").select("id, name").limit(1).execute()
        print(f"✅ 查询成功，返回 {len(result.data)} 条记录")
        if result.data:
            print(f"示例数据: {result.data[0]}")
        
        if supabase_service_key:
            print("\n--- 测试管理员客户端连接 ---")
            # 创建管理员客户端
            try:
                supabase_admin = create_client(
                    supabase_url, 
                    supabase_service_key,
                    options={
                        "schema": "public", 
                        "headers": {},
                        "auto_refresh_token": True,
                        "persist_session": True
                    }
                )
                print("✅ 管理员客户端创建成功（完整配置）")
            except Exception as e:
                print(f"⚠️ 完整配置失败，尝试简化配置: {str(e)}")
                supabase_admin = create_client(supabase_url, supabase_service_key)
                print("✅ 管理员客户端创建成功（简化配置）")
            
            # 测试管理员权限查询
            print("测试查询users表...")
            admin_result = supabase_admin.table("users").select("id").limit(1).execute()
            print(f"✅ 管理员查询成功，返回 {len(admin_result.data)} 条记录")
        
        print("\n🎉 Supabase连接测试全部通过！")
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        
        # 尝试诊断具体问题
        if "SSL" in str(e) or "ssl" in str(e):
            print("💡 提示：这可能是SSL连接问题")
        elif "EOF" in str(e):
            print("💡 提示：这可能是网络连接问题或SSL协议问题")
        elif "timeout" in str(e).lower():
            print("💡 提示：这可能是网络超时问题")
        
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    exit(0 if success else 1) 