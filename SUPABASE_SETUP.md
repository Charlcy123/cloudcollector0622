# Supabase JWT 认证集成指南

## 概述

本项目已集成完整的 Supabase 用户认证系统，包括：

- 前端：邮箱+密码注册、登录、登出
- 后端：JWT Token 验证和用户身份识别
- 安全的 API 认证机制

## 环境变量配置

### 前端环境变量 (.env.local)

```bash
# Supabase 配置
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key

# API 配置
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 后端环境变量 (.env)

```bash
# Supabase 配置
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_JWT_SECRET=your-jwt-secret

# 其他配置
ARK_API_KEY=your-ark-api-key
```

## 获取 Supabase 配置

1. **登录 Supabase Dashboard**
   - 访问 https://supabase.com
   - 登录并进入你的项目

2. **获取 API 配置**
   - 进入 `Settings` > `API`
   - 复制以下信息：
     - `Project URL` → `NEXT_PUBLIC_SUPABASE_URL`
     - `anon public` → `NEXT_PUBLIC_SUPABASE_ANON_KEY`
     - `service_role secret` → `SUPABASE_SERVICE_ROLE_KEY`

3. **获取 JWT Secret**
   - 在同一页面找到 `JWT Settings`
   - 复制 `JWT Secret` → `SUPABASE_JWT_SECRET`

## 前端使用方法

### 1. 注册新用户

```typescript
import { useAuth } from '@/contexts/AuthContext'

function RegisterComponent() {
  const { signUp } = useAuth()
  
  const handleRegister = async (email: string, password: string) => {
    try {
      await signUp(email, password)
      // 注册成功，用户需要验证邮箱
    } catch (error) {
      console.error('注册失败:', error)
    }
  }
}
```

### 2. 用户登录

```typescript
import { useAuth } from '@/contexts/AuthContext'

function LoginComponent() {
  const { signIn } = useAuth()
  
  const handleLogin = async (email: string, password: string) => {
    try {
      await signIn(email, password)
      // 登录成功
    } catch (error) {
      console.error('登录失败:', error)
    }
  }
}
```

### 3. 调用认证API

```typescript
import { api } from '@/lib/api'

// 自动携带JWT Token的API调用
const response = await api.get('/api/v2/my-collections')
const collections = await response.json()
```

### 4. 获取当前用户状态

```typescript
import { useAuth } from '@/contexts/AuthContext'

function UserProfile() {
  const { user, session, loading } = useAuth()
  
  if (loading) return <div>加载中...</div>
  if (!user) return <div>请先登录</div>
  
  return (
    <div>
      <h1>欢迎，{user.email}</h1>
      <p>用户ID: {user.id}</p>
    </div>
  )
}
```

## 后端使用方法

### 1. 需要认证的路由

```python
from auth import get_current_user

@app.get("/api/protected-route")
async def protected_route(current_user: dict = Depends(get_current_user)):
    user_id = current_user["sub"]
    user_email = current_user.get("email")
    return {"message": f"Hello {user_email}!", "user_id": user_id}
```

### 2. 可选认证的路由

```python
from auth import get_optional_user

@app.get("/api/public-route")
async def public_route(user: Optional[dict] = Depends(get_optional_user)):
    if user:
        return {"message": f"Hello {user.get('email')}!", "user_id": user["sub"]}
    else:
        return {"message": "Hello anonymous user!"}
```

### 3. 只需要用户ID的路由

```python
from auth import get_current_user_id

@app.get("/api/my-data")
async def get_my_data(user_id: str = Depends(get_current_user_id)):
    # 直接使用 user_id
    return {"user_id": user_id, "data": "some data"}
```

## API 端点说明

### 认证测试端点

- `GET /api/auth/test` - 测试JWT认证是否正常
- `GET /api/auth/profile` - 获取当前用户信息

### JWT认证版本的云朵收藏API

- `POST /api/v2/cloud-collections` - 创建云朵收藏
- `GET /api/v2/my-collections` - 获取我的收藏列表
- `PATCH /api/v2/cloud-collections/{id}/favorite` - 切换收藏状态
- `DELETE /api/v2/cloud-collections/{id}` - 删除收藏

### 兼容性说明

- 原有的 `/api/cloud-collections` 等端点仍然可用（基于device_id）
- 新的 `/api/v2/` 端点使用JWT认证，更安全
- 建议新功能使用JWT认证版本

## 测试认证功能

### 1. 启动服务

```bash
# 启动后端
python main.py

# 启动前端
npm run dev
```

### 2. 测试流程

1. 访问 http://localhost:3000
2. 点击右上角的"注册"按钮
3. 填写邮箱和密码进行注册
4. 检查邮箱验证邮件（开发环境可能在垃圾邮件中）
5. 验证邮箱后登录
6. 登录成功后可以看到用户头像和菜单

### 3. API测试

```bash
# 首先登录获取token（在浏览器开发者工具中）
# 然后测试认证API

curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/auth/test
```

## 故障排除

### 1. JWT验证失败

- 检查 `SUPABASE_JWT_SECRET` 是否正确
- 确认token没有过期
- 验证token格式是否正确

### 2. 登录失败

- 检查邮箱是否已验证
- 确认密码是否正确
- 查看Supabase Dashboard中的用户状态

### 3. API调用失败

- 确认请求头中包含正确的Authorization
- 检查token是否有效
- 查看服务器日志获取详细错误信息

## 安全注意事项

1. **JWT Secret保护**：绝不要在前端代码或公开仓库中暴露JWT Secret
2. **HTTPS使用**：生产环境必须使用HTTPS
3. **Token过期**：合理设置token过期时间
4. **权限控制**：确保用户只能访问自己的数据

## 下一步扩展

1. **角色权限**：可以基于用户角色实现更细粒度的权限控制
2. **社交登录**：集成Google、GitHub等第三方登录
3. **多因素认证**：添加短信或邮箱二次验证
4. **API限流**：基于用户身份实现API调用限制 