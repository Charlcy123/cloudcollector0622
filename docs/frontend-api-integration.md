# 前后端联调集成指南

## 🎯 概述

本文档介绍如何将 React/Next.js 前端与 FastAPI 后端进行集成，包括 API 封装、组件使用和配置说明。

## 📁 文件结构

```
project/
├── utils/
│   └── api.ts                    # API 封装函数
├── components/
│   ├── CloudCapture.tsx          # 云朵捕获组件
│   └── CloudCollectionList.tsx   # 云朵收藏列表组件
├── .env.local                    # 环境变量配置
└── main.py                       # FastAPI 后端
```

## ⚙️ 环境配置

### 1. 环境变量设置

创建 `.env.local` 文件（如果不存在）：

```env
# 后端 API 地址
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# 如果需要的话，可以添加其他配置
NEXT_PUBLIC_APP_NAME=云彩收集手册
NEXT_PUBLIC_DEBUG=true
```

### 2. 后端 CORS 配置

确保你的 FastAPI 后端（`main.py`）包含 CORS 配置：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js 开发服务器
        "http://127.0.0.1:3000",
        "https://your-domain.com",  # 生产环境域名
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔧 API 封装说明

### 核心功能模块

`utils/api.ts` 文件包含以下主要功能模块：

1. **用户管理 API** (`userAPI`)
   - `createOrGetUser()` - 创建或获取用户
   - `getUser()` - 获取用户信息
   - `updateUser()` - 更新用户信息

2. **捕云工具 API** (`captureToolAPI`)
   - `getCaptureTools()` - 获取所有捕云工具

3. **AI 服务 API** (`aiAPI`)
   - `generateCloudNameFromUpload()` - 基于图片生成云朵名称
   - `generateCloudDescriptionFromUpload()` - 基于图片生成云朵描述
   - `generateCloudName()` - 基于 base64 生成云朵名称
   - `generateCloudDescription()` - 基于 base64 生成云朵描述

4. **天气服务 API** (`weatherAPI`)
   - `getCurrentWeather()` - 获取当前天气信息

5. **云朵收藏 API** (`cloudCollectionAPI`)
   - `createCloudCollection()` - 创建云朵收藏
   - `getUserCloudCollections()` - 获取用户收藏列表
   - `getCloudCollection()` - 获取单个收藏详情
   - `toggleFavorite()` - 切换收藏状态
   - `deleteCloudCollection()` - 删除收藏

### 工具函数

- `getCurrentLocation()` - 获取用户地理位置
- `formatDateTime()` - 格式化日期时间
- `isValidImageFile()` - 验证图片文件
- `getDeviceId()` / `getUserId()` - 获取设备/用户标识

## 🎨 组件使用指南

### CloudCapture 组件

完整的云朵捕获功能组件，包含：

- 用户初始化和工具选择
- 图片上传和预览
- AI 名称和描述生成
- 天气信息获取
- 收藏保存功能

**使用方式：**

```tsx
import CloudCapture from '@/components/CloudCapture';

export default function CapturePage() {
  return (
    <div>
      <CloudCapture className="my-custom-class" />
    </div>
  );
}
```

### CloudCollectionList 组件

云朵收藏列表组件，包含：

- 收藏列表展示（网格/列表视图）
- 工具和收藏状态筛选
- 分页功能
- 收藏切换和删除操作

**使用方式：**

```tsx
import CloudCollectionList from '@/components/CloudCollectionList';

export default function CollectionPage() {
  return (
    <div>
      {/* 显示当前用户的收藏 */}
      <CloudCollectionList />
      
      {/* 显示特定用户的收藏 */}
      <CloudCollectionList userId="specific-user-id" />
    </div>
  );
}
```

## 🚀 启动指南

### 1. 启动后端服务

```bash
# 进入项目目录
cd /path/to/your/project

# 启动 FastAPI 服务
python main.py
# 或者使用 uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

后端将在 `http://localhost:8000` 启动

### 2. 启动前端服务

```bash
# 在项目根目录
npm run dev
# 或者
yarn dev
```

前端将在 `http://localhost:3000` 启动

## 🔍 调试和测试

### API 调试

1. **检查网络请求**
   - 打开浏览器开发者工具
   - 查看 Network 标签页
   - 确认 API 请求是否正常发送

2. **后端 API 文档**
   - 访问 `http://localhost:8000/docs`
   - 查看 Swagger 自动生成的 API 文档
   - 可以直接在文档中测试 API

3. **错误处理**
   - 组件会显示详细的错误信息
   - 检查浏览器控制台的日志
   - 查看后端日志输出

### 常见问题排查

1. **CORS 错误**
   ```
   Access to fetch at 'http://localhost:8000/api/...' from origin 'http://localhost:3000' has been blocked by CORS policy
   ```
   - 确保后端正确配置了 CORS
   - 检查 `allow_origins` 是否包含前端地址

2. **API 地址错误**
   ```
   TypeError: Failed to fetch
   ```
   - 检查 `.env.local` 中的 `NEXT_PUBLIC_API_BASE_URL`
   - 确保后端服务正在运行

3. **类型错误**
   ```
   TypeScript error: Property 'xxx' does not exist on type 'yyy'
   ```
   - 检查 API 响应格式是否与类型定义匹配
   - 更新类型定义或 API 实现

## 🎯 最佳实践

### 1. 错误处理

```tsx
const handleApiCall = async () => {
  try {
    setLoading(true);
    const response = await someAPI.call();
    
    if (response.success && response.data) {
      // 处理成功情况
      setData(response.data);
      setSuccess('操作成功');
    } else {
      // 处理业务错误
      setError(response.error || '操作失败');
    }
  } catch (error) {
    // 处理网络或其他错误
    setError('请求失败，请稍后重试');
    console.error('API call error:', error);
  } finally {
    setLoading(false);
  }
};
```

### 2. 加载状态管理

```tsx
const [isLoading, setIsLoading] = useState(false);

return (
  <Button disabled={isLoading} onClick={handleApiCall}>
    {isLoading ? (
      <>
        <Loader2 className="h-4 w-4 animate-spin mr-2" />
        处理中...
      </>
    ) : (
      '提交'
    )}
  </Button>
);
```

### 3. 数据缓存

对于不经常变化的数据（如捕云工具列表），可以考虑使用缓存：

```tsx
// 使用 React Query 或 SWR 进行数据缓存
import useSWR from 'swr';

const { data: captureTools, error } = useSWR(
  'capture-tools',
  () => captureToolAPI.getCaptureTools()
);
```

## 📝 扩展开发

### 添加新的 API 端点

1. **在后端添加新的路由**
2. **在 `utils/api.ts` 中添加对应的函数**
3. **更新类型定义**
4. **在组件中使用新的 API 函数**

### 示例：添加用户统计 API

```typescript
// 在 api.ts 中添加
export const userAPI = {
  // ... 现有函数
  
  async getUserStats(userId: string): Promise<ApiResponse<UserStats>> {
    return apiRequest(`/api/users/${userId}/stats`);
  }
};

// 类型定义
export interface UserStats {
  total_collections: number;
  favorite_collections: number;
  total_views: number;
  created_at: string;
}
```

## 🔧 生产环境配置

### 环境变量

```env
# .env.local (开发环境)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# .env.production (生产环境)
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.com
```

### 构建和部署

```bash
# 构建前端
npm run build

# 启动生产服务
npm start
```

---

## 📞 支持

如果在集成过程中遇到问题，请检查：

1. 后端服务是否正常运行
2. CORS 配置是否正确
3. 环境变量是否正确设置
4. API 端点是否与后端匹配

希望这个集成指南能帮助您顺利完成前后端联调！🎉 