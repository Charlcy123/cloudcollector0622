 # 云彩收集手册 - 第三方 API 技术设计文档

## 1. OpenAI API 集成

### 1.1 云朵命名生成 API

**接口名称**: `generateCloudName`

**请求路径**: `/api/cloud/name`

**请求方法**: `POST`

**依赖服务**: OpenAI API (GPT-4)

**请求参数**:
```json
{
  "tool": "string",      // 捕云工具类型：broom, hand, catPaw, glassCover
  "imageFeatures": {     // 云朵图像特征
    "shape": "string",   // 云朵形状描述
    "color": "string",   // 云朵颜色描述
    "texture": "string"  // 云朵纹理描述
  },
  "context": {
    "time": "string",    // 拍摄时间
    "weather": "string", // 天气状况
    "location": "string" // 拍摄地点
  }
}
```

**示例返回**:
```json
{
  "success": true,
  "data": {
    "name": "飞行棉花糖咒语云",
    "description": "一朵蓬松的白云，像被施了魔法的棉花糖，在天空中轻盈飘动",
    "style": "fantasy"  // 命名风格：fantasy, emotional, cute, artistic
  }
}
```

**错误返回**:
```json
{
  "success": false,
  "error": {
    "code": "NamingFailed",
    "message": "这朵云太有个性了，AI 看傻了！"
  }
}
```

### 1.2 云朵描述生成 API

**接口名称**: `generateCloudDescription`

**请求路径**: `/api/cloud/description`

**请求方法**: `POST`

**依赖服务**: OpenAI API (GPT-4)

**请求参数**:
```json
{
  "cloudName": "string",  // 已生成的云朵名称
  "imageFeatures": {      // 云朵图像特征
    "shape": "string",
    "color": "string",
    "texture": "string"
  },
  "tool": "string"        // 使用的捕云工具
}
```

**示例返回**:
```json
{
  "success": true,
  "data": {
    "description": "这朵云像一只慵懒的橘猫，在午后的阳光下伸着懒腰，让人忍不住想伸手摸摸它蓬松的毛发。",
    "mood": "relaxed",    // 描述的情感基调
    "keywords": ["慵懒", "温暖", "治愈"]  // 关键词标签
  }
}
```

## 2. Hugging Face API 集成

### 2.1 云朵图像分析 API

**接口名称**: `analyzeCloudImage`

**请求路径**: `/api/cloud/analyze`

**请求方法**: `POST`

**依赖服务**: Hugging Face API (图像分类模型)

**请求参数**:
```json
{
  "image": "base64string",  // Base64 编码的图片数据
  "options": {
    "detectShape": true,    // 是否检测形状
    "detectColor": true,    // 是否检测颜色
    "detectTexture": true   // 是否检测纹理
  }
}
```

**示例返回**:
```json
{
  "success": true,
  "data": {
    "features": {
      "shape": "cumulus",      // 云朵形状类型
      "color": "white",        // 主要颜色
      "texture": "fluffy",     // 纹理特征
      "confidence": 0.95       // 识别置信度
    },
    "metadata": {
      "width": 1920,
      "height": 1080,
      "format": "jpeg"
    }
  }
}
```

**错误返回**:
```json
{
  "success": false,
  "error": {
    "code": "AnalysisFailed",
    "message": "无法识别云朵特征，请确保图片清晰且包含云朵"
  }
}
```

## 3. OpenWeatherMap API 集成

### 3.1 实时天气数据获取 API

**接口名称**: `getWeatherData`

**请求路径**: `/api/weather/current`

**请求方法**: `GET`

**依赖服务**: OpenWeatherMap API

**请求参数**:
```json
{
  "location": {
    "latitude": "number",  // 纬度
    "longitude": "number"  // 经度
  },
  "units": "metric"        // 单位制：metric（公制）, imperial（英制）
}
```

**示例返回**:
```json
{
  "success": true,
  "data": {
    "weather": {
      "main": "Clouds",           // 主要天气状况
      "description": "scattered clouds", // 详细天气描述
      "icon": "03d"              // 天气图标代码
    },
    "clouds": {
      "all": 40                  // 云量百分比
    },
    "visibility": 10000,         // 能见度（米）
    "wind": {
      "speed": 3.5,             // 风速（米/秒）
      "deg": 200                // 风向（度）
    },
    "main": {
      "temp": 22.5,             // 温度（摄氏度）
      "humidity": 65,           // 湿度（百分比）
      "pressure": 1012          // 气压（百帕）
    },
    "sys": {
      "sunrise": 1600000000,    // 日出时间（Unix时间戳）
      "sunset": 1600040000      // 日落时间（Unix时间戳）
    }
  }
}
```

**错误返回**:
```json
{
  "success": false,
  "error": {
    "code": "WeatherDataFailed",
    "message": "无法获取天气数据，请稍后重试"
  }
}
```

## 注意事项

1. API 调用频率限制
   - OpenAI API: 根据账户等级限制
   - Hugging Face API: 根据模型和账户类型限制
   - OpenWeatherMap API: 免费版每分钟 60 次调用限制

2. 错误处理
   - 所有 API 调用需要实现重试机制
   - 需要处理网络超时、服务不可用等异常情况
   - 实现优雅的降级策略

3. 安全性
   - API 密钥需要安全存储
   - 所有 API 调用需要实现速率限制
   - 图片数据需要进行安全验证
   - 实现请求签名验证

4. 性能优化
   - 图片上传前进行压缩
   - 实现请求缓存机制
   - 考虑使用 CDN 加速图片传输
   - 天气数据本地缓存（建议缓存时间：10分钟）

5. 天气 API 注意事项
   - 需要注册 OpenWeatherMap 账号并获取 API Key
   - 建议实现天气数据缓存机制，避免频繁调用
   - 考虑使用 WebSocket 实现实时天气更新
   - 注意处理时区转换，确保时间显示准确
   - 实现天气数据本地存储，支持离线查看