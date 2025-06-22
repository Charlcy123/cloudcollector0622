#!/usr/bin/env python3
"""
Supabase连接测试脚本 - SSL修复版本
"""
import os
import ssl
import httpx
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_supabase_with_httpx():
    """使用httpx直接测试Supabase REST API"""
    print("=== Supabase REST API 直接测试 ===")
    
    # 获取环境变量
    supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
    supabase_anon_key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
    
    print(f"Supabase URL: {supabase_url}")
    print(f"匿名密钥存在: {'是' if supabase_anon_key else '否'}")
    
    if not supabase_url or not supabase_anon_key:
        print("❌ 缺少必要的环境变量")
        return False
    
    # 构建REST API URL
    rest_url = f"{supabase_url}/rest/v1"
    
    # 设置请求头
    headers = {
        "apikey": supabase_anon_key,
        "Authorization": f"Bearer {supabase_anon_key}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n--- 使用httpx测试REST API ---")
        
        # 创建SSL上下文，跳过SSL验证（仅用于测试）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        async with httpx.AsyncClient(
            verify=False,  # 跳过SSL验证
            timeout=30.0
        ) as client:
            # 测试查询capture_tools表
            print("测试查询capture_tools表...")
            response = await client.get(
                f"{rest_url}/capture_tools?select=id,name&limit=1",
                headers=headers
            )
            
            print(f"HTTP状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 查询成功，返回 {len(data)} 条记录")
                if data:
                    print(f"示例数据: {data[0]}")
                
                print("\n🎉 Supabase REST API连接测试成功！")
                return True
            else:
                print(f"❌ 查询失败: {response.status_code}")
                print(f"响应内容: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ REST API测试失败: {str(e)}")
        print(f"错误类型: {type(e).__name__}")
        return False

def test_supabase_python_client():
    """测试Supabase Python客户端（使用环境变量强制跳过SSL验证）"""
    print("\n=== Supabase Python客户端测试（SSL修复） ===")
    
    # 临时设置环境变量来跳过SSL验证
    original_ssl_verify = os.environ.get("PYTHONHTTPSVERIFY")
    os.environ["PYTHONHTTPSVERIFY"] = "0"
    
    try:
        from supabase import create_client, Client
        
        supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        supabase_anon_key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
        
        # 创建客户端
        supabase_client = create_client(supabase_url, supabase_anon_key)
        print("✅ Python客户端创建成功")
        
        # 测试查询
        print("测试查询capture_tools表...")
        result = supabase_client.table("capture_tools").select("id, name").limit(1).execute()
        print(f"✅ 查询成功，返回 {len(result.data)} 条记录")
        if result.data:
            print(f"示例数据: {result.data[0]}")
        
        print("🎉 Supabase Python客户端测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ Python客户端测试失败: {str(e)}")
        return False
    finally:
        # 恢复原始SSL验证设置
        if original_ssl_verify is not None:
            os.environ["PYTHONHTTPSVERIFY"] = original_ssl_verify
        else:
            os.environ.pop("PYTHONHTTPSVERIFY", None)

async def main():
    """主测试函数"""
    print("开始Supabase连接诊断...\n")
    
    # 测试1: 直接REST API
    rest_success = await test_supabase_with_httpx()
    
    # 测试2: Python客户端（SSL修复）
    client_success = test_supabase_python_client()
    
    print(f"\n=== 测试结果总结 ===")
    print(f"REST API测试: {'✅ 成功' if rest_success else '❌ 失败'}")
    print(f"Python客户端测试: {'✅ 成功' if client_success else '❌ 失败'}")
    
    if rest_success or client_success:
        print("\n💡 建议：")
        if rest_success and not client_success:
            print("- REST API可以正常工作，但Python客户端有SSL问题")
            print("- 可以考虑在生产环境中配置SSL证书或使用代理")
        elif client_success:
            print("- 可以通过设置环境变量 PYTHONHTTPSVERIFY=0 来跳过SSL验证")
            print("- 注意：这会降低安全性，仅建议在开发环境使用")
    else:
        print("\n❌ 所有测试都失败了，可能的原因：")
        print("- 网络连接问题")
        print("- Supabase服务不可用")
        print("- API密钥配置错误")
    
    return rest_success or client_success

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 