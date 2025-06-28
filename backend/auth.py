"""
Supabase JWT认证工具模块

本模块提供了验证Supabase JWT Token的功能，包括：
1. 从请求头中提取JWT Token
2. 验证Token的真伪和有效期
3. 从Token中提取用户信息
"""

import os
import jwt
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 创建HTTPBearer实例，用于从请求头中提取Bearer Token
security = HTTPBearer()

def get_supabase_jwt_secret() -> str:
    """
    从环境变量获取Supabase JWT Secret
    
    Returns:
        str: Supabase JWT Secret
        
    Raises:
        ValueError: 如果环境变量中没有设置SUPABASE_JWT_SECRET
    """
    jwt_secret = os.getenv("SUPABASE_JWT_SECRET")
    if not jwt_secret:
        raise ValueError("SUPABASE_JWT_SECRET environment variable is not set")
    return jwt_secret

def verify_supabase_token(token: str) -> Dict[str, Any]:
    """
    验证Supabase JWT Token
    
    Args:
        token (str): JWT Token字符串
        
    Returns:
        Dict[str, Any]: 解码后的Token payload，包含用户信息
        
    Raises:
        HTTPException: Token无效、过期或验证失败时抛出401错误
    """
    try:
        # 获取JWT Secret
        jwt_secret = get_supabase_jwt_secret()
        
        # 验证并解码JWT Token
        # algorithm="HS256" 是Supabase使用的签名算法
        # verify_exp=True 验证Token是否过期
        # verify_aud=False 不验证audience（Supabase的Token可能不包含aud字段）
        payload = jwt.decode(
            token, 
            jwt_secret, 
            algorithms=["HS256"],
            verify_exp=True,
            options={"verify_aud": False}
        )
        
        # 检查Token是否包含必要的用户信息
        if "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        # Token已过期
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        # Token无效
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except Exception as e:
        # 其他验证错误
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    从请求中获取当前登录用户信息
    
    这个函数作为FastAPI的依赖项使用，会自动：
    1. 从请求头中提取Bearer Token
    2. 验证Token的有效性
    3. 返回用户信息
    
    Args:
        credentials: FastAPI自动注入的认证凭据
        
    Returns:
        Dict[str, Any]: 用户信息，包含以下字段：
            - sub: 用户ID (Supabase User ID)
            - email: 用户邮箱
            - exp: Token过期时间
            - iat: Token签发时间
            - 其他Supabase Token中的字段
            
    Raises:
        HTTPException: 认证失败时抛出401错误
        
    Usage:
        @app.get("/api/protected-route")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user["sub"]
            user_email = current_user.get("email")
            return {"message": f"Hello {user_email}!", "user_id": user_id}
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is required"
        )
    
    # 验证Token并返回用户信息
    return verify_supabase_token(credentials.credentials)

def get_current_user_id(current_user: Dict[str, Any] = Depends(get_current_user)) -> str:
    """
    从当前用户信息中提取用户ID
    
    这是一个便捷函数，当你只需要用户ID时可以使用
    
    Args:
        current_user: 当前用户信息（由get_current_user提供）
        
    Returns:
        str: 用户ID (Supabase User ID)
        
    Usage:
        @app.get("/api/my-data")
        async def get_my_data(user_id: str = Depends(get_current_user_id)):
            # 使用user_id查询用户相关数据
            return {"user_id": user_id, "data": "some data"}
    """
    return current_user["sub"]

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))) -> Optional[Dict[str, Any]]:
    """
    可选的用户认证，不强制要求登录
    
    当API既支持登录用户又支持游客访问时使用
    
    Args:
        credentials: 可选的认证凭据
        
    Returns:
        Optional[Dict[str, Any]]: 用户信息（如果已登录）或None（如果未登录）
        
    Usage:
        @app.get("/api/public-data")
        async def get_public_data(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                user_id = user["sub"]
                # 返回个性化数据
            else:
                # 返回公共数据
    """
    if not credentials:
        return None
    
    try:
        return verify_supabase_token(credentials.credentials)
    except HTTPException:
        # 如果Token无效，返回None而不是抛出异常
        return None

# 示例：如何在路由中使用这些认证函数
"""
from fastapi import FastAPI, Depends
from auth import get_current_user, get_current_user_id, get_optional_user

app = FastAPI()

# 需要登录的路由
@app.get("/api/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["sub"],
        "email": current_user.get("email"),
        "profile": "user profile data"
    }

# 只需要用户ID的路由
@app.get("/api/my-collections")
async def get_my_collections(user_id: str = Depends(get_current_user_id)):
    return {"user_id": user_id, "collections": []}

# 可选登录的路由
@app.get("/api/collections")
async def get_collections(user: Optional[dict] = Depends(get_optional_user)):
    if user:
        # 返回用户个人收藏
        return {"personal_collections": [], "user_id": user["sub"]}
    else:
        # 返回公共收藏
        return {"public_collections": []}
""" 