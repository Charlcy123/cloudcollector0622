#!/usr/bin/env python3
"""
数据库初始化脚本
用于插入初始的捕云工具数据和其他基础数据
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载环境变量
load_dotenv()

# 初始化 Supabase 客户端
supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("请确保设置了 SUPABASE_URL 和 SUPABASE_SERVICE_ROLE_KEY 环境变量")

supabase: Client = create_client(supabase_url, supabase_service_key)

def init_capture_tools():
    """初始化捕云工具数据"""
    
    # 定义4种捕云工具的基础数据
    capture_tools_data = [
        {
            "id": "broom",
            "name": "扫帚",
            "emoji": "🧹",
            "description": "魔法世界的经典工具，能够捕获最具幻想色彩的云朵，让每朵云都带有童话般的魔力",
            "sort_order": 1
        },
        {
            "id": "hand", 
            "name": "手",
            "emoji": "🤚",
            "description": "最直接的捕云方式，用心去感受云朵的温度，捕获最贴近生活的云朵名称",
            "sort_order": 2
        },
        {
            "id": "catPaw",
            "name": "猫爪",
            "emoji": "🐾", 
            "description": "轻柔而可爱的捕云方式，专门用来捕获那些毛茸茸、让人想要撸一把的云朵",
            "sort_order": 3
        },
        {
            "id": "glassCover",
            "name": "玻璃罩",
            "emoji": "🫙",
            "description": "优雅而神秘的捕云工具，能够捕获最具艺术气息和诗意的云朵名称",
            "sort_order": 4
        }
    ]
    
    try:
        # 检查是否已有数据
        result = supabase.table("capture_tools").select("id").execute()
        existing_ids = {tool["id"] for tool in result.data}
        
        # 只插入不存在的工具
        new_tools = [tool for tool in capture_tools_data if tool["id"] not in existing_ids]
        
        if new_tools:
            result = supabase.table("capture_tools").insert(new_tools).execute()
            print(f"✅ 成功插入 {len(new_tools)} 个捕云工具")
            for tool in new_tools:
                print(f"   - {tool['emoji']} {tool['name']} ({tool['id']})")
        else:
            print("ℹ️  捕云工具数据已存在，跳过插入")
            
    except Exception as e:
        print(f"❌ 插入捕云工具数据失败: {str(e)}")
        raise

def check_database_connection():
    """检查数据库连接"""
    try:
        # 尝试查询一个表来测试连接
        result = supabase.table("capture_tools").select("count", count="exact").execute()
        print(f"✅ 数据库连接成功，当前有 {result.count} 个捕云工具")
        return True
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def create_sample_user():
    """创建示例用户（仅用于测试）"""
    try:
        sample_user = {
            "device_id": "sample_device_123",
            "display_name": "示例用户",
            "is_anonymous": True
        }
        
        # 检查是否已存在
        result = supabase.table("users").select("id").eq("device_id", "sample_device_123").execute()
        
        if not result.data:
            result = supabase.table("users").insert(sample_user).execute()
            print(f"✅ 创建示例用户成功: {result.data[0]['display_name']}")
        else:
            print("ℹ️  示例用户已存在，跳过创建")
            
    except Exception as e:
        print(f"❌ 创建示例用户失败: {str(e)}")

def main():
    """主函数：执行数据库初始化"""
    print("🚀 开始初始化数据库...")
    print("=" * 50)
    
    # 1. 检查数据库连接
    print("1. 检查数据库连接...")
    if not check_database_connection():
        return
    
    # 2. 初始化捕云工具数据
    print("\n2. 初始化捕云工具数据...")
    init_capture_tools()
    
    # 3. 创建示例用户（可选）
    print("\n3. 创建示例用户...")
    create_sample_user()
    
    print("\n" + "=" * 50)
    print("🎉 数据库初始化完成！")
    print("\n您现在可以：")
    print("- 启动 FastAPI 服务器: python main.py")
    print("- 查看 API 文档: http://localhost:8000/docs")
    print("- 使用云彩收集手册应用")

if __name__ == "__main__":
    main() 