#!/usr/bin/env python3
"""
最终清理脚本 - 删除重复的函数
"""

import re
from pathlib import Path

def remove_duplicate_function():
    """删除重复的create_cloud_collection_from_image_upload函数"""
    
    main_py_path = Path("main.py")
    content = main_py_path.read_text(encoding='utf-8')
    
    # 查找第二个重复的函数（从line 2825开始的那个）
    # 这个函数从 "# ============== JWT认证版本的云朵收藏API ==============" 开始
    # 到下一个函数定义结束
    
    pattern = r'# ============== JWT认证版本的云朵收藏API ==============\n\n@app\.post\("/api/v2/cloud/create-from-image-upload".*?\n.*?async def create_cloud_collection_from_image_upload\([\s\S]*?raise HTTPException\(\s*status_code=500,\s*detail=f"创建云朵收藏失败: \{str\(e\)\}"\s*\)\n\n'
    
    # 删除匹配的内容
    content = re.sub(pattern, '', content, count=1)
    
    main_py_path.write_text(content, encoding='utf-8')
    print("✅ 删除重复的create_cloud_collection_from_image_upload函数")

def rename_remaining_function():
    """重命名剩余的函数"""
    
    main_py_path = Path("main.py")
    content = main_py_path.read_text(encoding='utf-8')
    
    # 重命名 create_cloud_collection_from_image_upload_v2 为 create_cloud_collection_from_image_upload
    content = re.sub(
        r'async def create_cloud_collection_from_image_upload_v2\(',
        'async def create_cloud_collection_from_image_upload(',
        content
    )
    
    main_py_path.write_text(content, encoding='utf-8')
    print("✅ 重命名函数完成")

def main():
    print("🧹 开始最终清理...")
    print()
    
    print("步骤 1: 删除重复的函数...")
    remove_duplicate_function()
    print()
    
    print("步骤 2: 重命名剩余的函数...")
    rename_remaining_function()
    print()
    
    print("🎉 最终清理完成！")

if __name__ == "__main__":
    main() 