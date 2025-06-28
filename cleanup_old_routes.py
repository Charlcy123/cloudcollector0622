#!/usr/bin/env python3
"""
清理旧路由的脚本
删除所有Header-based的API路由，只保留JWT认证的版本
"""

import re
from pathlib import Path

def remove_old_routes():
    """删除旧的Header-based路由"""
    
    main_py_path = Path("main.py")
    if not main_py_path.exists():
        print("❌ main.py 文件不存在")
        return
    
    content = main_py_path.read_text(encoding='utf-8')
    
    # 要删除的旧路由函数
    old_routes_to_remove = [
        # 删除旧的云朵收藏路由
        r'@app\.post\("/api/v2/cloud-collections".*?\n.*?async def create_cloud_collection_v2\(.*?\n.*?\):.*?\n.*?""".*?""".*?\n.*?try:.*?\n.*?except Exception as e:.*?\n.*?raise HTTPException.*?\n\n',
        
        # 删除旧的用户收藏列表路由
        r'@app\.get\("/api/users/\{user_id\}/cloud-collections".*?\n.*?async def get_user_cloud_collections\(.*?\n.*?\):.*?\n.*?""".*?""".*?\n.*?try:.*?\n.*?except Exception as e:.*?\n.*?raise HTTPException.*?\n\n',
        
        # 删除旧的收藏状态切换路由
        r'@app\.patch\("/api/v2/cloud-collections/\{collection_id\}/favorite".*?\n.*?async def toggle_cloud_collection_favorite_v2\(.*?\n.*?\):.*?\n.*?""".*?""".*?\n.*?try:.*?\n.*?except Exception as e:.*?\n.*?raise HTTPException.*?\n\n',
        
        # 删除旧的删除收藏路由
        r'@app\.delete\("/api/v2/cloud-collections/\{collection_id\}".*?\n.*?async def delete_cloud_collection_v2\(.*?\n.*?\):.*?\n.*?""".*?""".*?\n.*?try:.*?\n.*?except Exception as e:.*?\n.*?raise HTTPException.*?\n\n',
    ]
    
    # 手动删除具体的重复函数
    # 1. 删除第一个create_cloud_collection_v2 (保留create_cloud_collection_jwt)
    pattern1 = r'@app\.post\("/api/v2/cloud-collections", response_model=CloudCollectionResponse\)\nasync def create_cloud_collection_v2\([\s\S]*?raise HTTPException\(status_code=500, detail=f"创建云朵收藏失败: \{str\(e\)\}"\)\n\n'
    content = re.sub(pattern1, '', content, count=1)
    
    # 2. 删除get_user_cloud_collections (保留get_my_cloud_collections和get_user_cloud_collections_v2)
    pattern2 = r'@app\.get\("/api/users/\{user_id\}/cloud-collections", response_model=CloudCollectionListResponse\)\nasync def get_user_cloud_collections\([\s\S]*?raise HTTPException\(status_code=500, detail=f"获取用户云朵收藏失败: \{str\(e\)\}"\)\n\n'
    content = re.sub(pattern2, '', content, count=1)
    
    # 3. 删除第一个toggle_cloud_collection_favorite_v2 (保留toggle_cloud_collection_favorite_jwt)
    pattern3 = r'@app\.patch\("/api/v2/cloud-collections/\{collection_id\}/favorite"\)\nasync def toggle_cloud_collection_favorite_v2\([\s\S]*?raise HTTPException\(status_code=500, detail=f"更新收藏状态失败: \{str\(e\)\}"\)\n\n'
    content = re.sub(pattern3, '', content, count=1)
    
    # 4. 删除第一个delete_cloud_collection_v2 (保留delete_cloud_collection_jwt)
    pattern4 = r'@app\.delete\("/api/v2/cloud-collections/\{collection_id\}"\)\nasync def delete_cloud_collection_v2\([\s\S]*?raise HTTPException\(status_code=500, detail=f"删除云朵收藏失败: \{str\(e\)\}"\)\n\n'
    content = re.sub(pattern4, '', content, count=1)
    
    # 5. 删除重复的create_cloud_collection_from_image_upload_v2 (保留create_cloud_collection_from_image_upload_jwt)
    pattern5 = r'@app\.post\("/api/v2/cloud/create-from-image-upload", response_model=CloudCollectionResponse\)\nasync def create_cloud_collection_from_image_upload_v2\([\s\S]*?raise HTTPException\(status_code=500, detail=f"创建云朵收藏失败: \{str\(e\)\}"\)\n\n'
    content = re.sub(pattern5, '', content, count=1)
    
    main_py_path.write_text(content, encoding='utf-8')
    print("✅ 旧路由清理完成")

def rename_jwt_functions():
    """重命名JWT函数，去掉_jwt后缀"""
    
    main_py_path = Path("main.py")
    content = main_py_path.read_text(encoding='utf-8')
    
    # 重命名函数
    renames = {
        'create_cloud_collection_jwt': 'create_cloud_collection',
        'get_my_cloud_collections': 'get_my_cloud_collections',  # 保持不变
        'toggle_cloud_collection_favorite_jwt': 'toggle_cloud_collection_favorite',
        'delete_cloud_collection_jwt': 'delete_cloud_collection',
        'create_cloud_collection_from_image_upload_jwt': 'create_cloud_collection_from_image_upload',
        'get_user_cloud_collections_v2': 'get_user_cloud_collections',
    }
    
    for old_name, new_name in renames.items():
        content = re.sub(
            f'async def {old_name}\\(',
            f'async def {new_name}(',
            content
        )
    
    main_py_path.write_text(content, encoding='utf-8')
    print("✅ 函数重命名完成")

def add_auth_import():
    """确保导入了get_current_user"""
    
    main_py_path = Path("main.py")
    content = main_py_path.read_text(encoding='utf-8')
    
    if 'from auth import get_current_user' not in content:
        # 在FastAPI导入后添加
        content = re.sub(
            r'(from fastapi import.*?\n)',
            r'\1from auth import get_current_user\n',
            content,
            flags=re.MULTILINE
        )
        main_py_path.write_text(content, encoding='utf-8')
        print("✅ 添加auth导入")
    else:
        print("✅ auth导入已存在")

def main():
    """主清理流程"""
    print("🧹 开始清理旧路由...")
    print()
    
    print("步骤 1: 添加必要的导入...")
    add_auth_import()
    print()
    
    print("步骤 2: 删除重复的旧路由...")
    remove_old_routes()
    print()
    
    print("步骤 3: 重命名JWT函数...")
    rename_jwt_functions()
    print()
    
    print("🎉 清理完成！")
    print()
    print("📝 现在你的应用只使用JWT认证的API路由：")
    print("   - POST /api/v2/cloud-collections")
    print("   - GET /api/v2/my-collections")
    print("   - GET /api/v2/users/my-collections")
    print("   - PATCH /api/v2/cloud-collections/{collection_id}/favorite")
    print("   - DELETE /api/v2/cloud-collections/{collection_id}")
    print("   - POST /api/v2/cloud/create-from-image-upload")
    print("   - POST /api/v2/storage/*")

if __name__ == "__main__":
    main() 