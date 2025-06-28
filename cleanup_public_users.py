#!/usr/bin/env python3
"""
清理 public.users 表和相关代码
因为我们已经直接使用 auth.uid()，不需要 public.users 表
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 加载环境变量
load_dotenv()

supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not supabase_url or not supabase_service_key:
    raise ValueError("请确保设置了环境变量")

supabase: Client = create_client(supabase_url, supabase_service_key)

def analyze_current_state():
    """分析当前状态"""
    print("🔍 分析当前数据库状态...")
    
    try:
        # 检查 auth.users
        auth_users = supabase.auth.admin.list_users()
        print(f"✅ auth.users 中有 {len(auth_users.users)} 个用户")
        
        # 检查 public.users
        try:
            public_users_result = supabase.table("users").select("id").execute()
            print(f"ℹ️  public.users 中有 {len(public_users_result.data)} 个用户")
        except Exception as e:
            print(f"ℹ️  public.users 表不存在或无法访问: {str(e)}")
        
        # 检查 cloud_collections 中的 user_id
        collections_result = supabase.table("cloud_collections").select("user_id").execute()
        user_ids = {c['user_id'] for c in collections_result.data if c['user_id']}
        auth_user_ids = {user.id for user in auth_users.users}
        
        print(f"✅ cloud_collections 中有 {len(collections_result.data)} 条记录")
        print(f"✅ 其中涉及 {len(user_ids)} 个不同的用户ID")
        
        # 检查是否所有 user_id 都在 auth.users 中
        missing_in_auth = user_ids - auth_user_ids
        if missing_in_auth:
            print(f"⚠️  有 {len(missing_in_auth)} 个用户ID不在 auth.users 中:")
            for uid in missing_in_auth:
                print(f"   - {uid}")
        else:
            print("✅ 所有 cloud_collections 的 user_id 都在 auth.users 中")
            
    except Exception as e:
        print(f"❌ 分析失败: {str(e)}")

def check_dependencies():
    """检查是否有依赖 public.users 的外键约束"""
    print("\n🔍 检查数据库依赖关系...")
    
    check_sql = """
    SELECT 
        tc.table_name, 
        kcu.column_name, 
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
    WHERE 
        constraint_type = 'FOREIGN KEY' 
        AND ccu.table_name = 'users'
        AND tc.table_schema = 'public';
    """
    
    print("⚠️  请在 Supabase Dashboard 的 SQL Editor 中执行以下查询:")
    print("=" * 60)
    print(check_sql)
    print("=" * 60)
    print("这将显示所有引用 public.users 表的外键约束")

def generate_cleanup_sql():
    """生成清理 SQL"""
    print("\n📝 生成清理 SQL 语句...")
    
    cleanup_sql = """
-- 清理 public.users 表的步骤

-- 1. 移除所有引用 users 表的外键约束
-- 注意：根据上面的查询结果，可能需要先删除这些约束

-- 2. 如果 cloud_collections 有外键约束，先删除
DO $$ 
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'cloud_collections_user_id_fkey' 
        AND table_name = 'cloud_collections'
    ) THEN
        ALTER TABLE cloud_collections DROP CONSTRAINT cloud_collections_user_id_fkey;
        RAISE NOTICE '已移除 cloud_collections 外键约束';
    ELSE
        RAISE NOTICE 'cloud_collections 外键约束不存在，跳过';
    END IF;
END $$;

-- 3. 删除 public.users 表
DROP TABLE IF EXISTS users CASCADE;

-- 4. 确保 cloud_collections 的 RLS 策略正确
DROP POLICY IF EXISTS "Users can view own collections" ON cloud_collections;
DROP POLICY IF EXISTS "Users can insert own collections" ON cloud_collections;
DROP POLICY IF EXISTS "Users can update own collections" ON cloud_collections;
DROP POLICY IF EXISTS "Users can delete own collections" ON cloud_collections;

-- 创建新的 RLS 策略，直接使用 auth.uid()
CREATE POLICY "Users can view own collections" ON cloud_collections
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own collections" ON cloud_collections
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own collections" ON cloud_collections
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own collections" ON cloud_collections
    FOR DELETE USING (auth.uid() = user_id);

-- 5. 清理完成提示
DO $$
BEGIN
    RAISE NOTICE '✅ public.users 表清理完成！';
    RAISE NOTICE '现在应用完全基于 auth.users 运行';
END $$;
"""
    
    print("⚠️  请在 Supabase Dashboard 的 SQL Editor 中执行以下 SQL:")
    print("=" * 60)
    print(cleanup_sql)
    print("=" * 60)

def cleanup_local_files():
    """清理本地相关文件"""
    print("\n🗑️  清理本地文件...")
    
    files_to_remove = [
        "user_sync_trigger.sql",
        "sync_users.py",
        "migrate_to_auth_only.py"
    ]
    
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            response = input(f"是否删除 {file_path}？(y/N): ")
            if response.lower() == 'y':
                try:
                    os.remove(file_path)
                    print(f"✅ 已删除 {file_path}")
                except Exception as e:
                    print(f"❌ 删除 {file_path} 失败: {str(e)}")
            else:
                print(f"⏭️  保留 {file_path}")
        else:
            print(f"ℹ️  {file_path} 不存在，跳过")

def main():
    """主函数"""
    print("🚀 开始清理 public.users 表...")
    print("=" * 50)
    
    print("📋 清理步骤:")
    print("1. 分析当前状态")
    print("2. 检查数据库依赖")
    print("3. 生成清理 SQL")
    print("4. 清理本地文件")
    
    response = input("\n是否继续？(Y/n): ")
    if response.lower() == 'n':
        print("❌ 取消清理")
        return
    
    # 执行清理步骤
    analyze_current_state()
    check_dependencies()
    generate_cleanup_sql()
    cleanup_local_files()
    
    print("\n" + "=" * 50)
    print("🎉 清理准备完成！")
    print("\n📝 下一步:")
    print("1. 在 Supabase Dashboard 中执行生成的 SQL 语句")
    print("2. 测试应用功能是否正常")
    print("3. 如果一切正常，你的应用现在完全基于 auth.users 运行")
    print("\n💡 优势:")
    print("- 简化的架构，无需用户同步")
    print("- 直接使用 Supabase Auth 的安全机制")
    print("- 为支付系统做好准备")

if __name__ == "__main__":
    main() 