# 云彩收集手册 - 数据库设计文档

## 1. 数据库表设计

### 1.1 表结构概览

本项目基于 Supabase (PostgreSQL) 设计，包含以下核心表：

- `users` - 用户表
- `capture_tools` - 捕云工具表
- `locations` - 地理位置表
- `weather_records` - 天气记录表
- `cloud_collections` - 云朵收藏表（核心业务表）

### 1.2 表关系图 (ER关系)

```
users (1) -----> (N) cloud_collections
capture_tools (1) -----> (N) cloud_collections
locations (1) -----> (N) cloud_collections
weather_records (1) -----> (N) cloud_collections
```

### 1.3 详细表设计

#### 1.3.1 用户表 (users)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 用户唯一标识 |
| email | VARCHAR(255) | UNIQUE | 用户邮箱（可选） |
| username | VARCHAR(50) | UNIQUE | 用户名（可选） |
| display_name | VARCHAR(100) | | 显示名称 |
| is_anonymous | BOOLEAN | DEFAULT true | 是否匿名用户 |
| device_id | VARCHAR(255) | | 设备标识（匿名用户使用） |
| created_at | TIMESTAMPTZ | DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMPTZ | DEFAULT now() | 更新时间 |
| last_active_at | TIMESTAMPTZ | DEFAULT now() | 最后活跃时间 |

**索引设计：**
- `idx_users_email` ON email
- `idx_users_device_id` ON device_id
- `idx_users_created_at` ON created_at

#### 1.3.2 捕云工具表 (capture_tools)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | VARCHAR(20) | PRIMARY KEY | 工具标识 (broom, hand, catPaw, glassCover) |
| name | VARCHAR(50) | NOT NULL | 工具名称 |
| emoji | VARCHAR(10) | NOT NULL | 工具表情符号 |
| description | TEXT | NOT NULL | 工具描述 |
| sort_order | INTEGER | DEFAULT 0 | 排序顺序 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 创建时间 |

**索引设计：**
- `idx_capture_tools_active_sort` ON (is_active, sort_order)

#### 1.3.3 地理位置表 (locations)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 位置唯一标识 |
| latitude | DECIMAL(10,8) | | 纬度 |
| longitude | DECIMAL(11,8) | | 经度 |
| address | TEXT | | 详细地址 |
| city | VARCHAR(100) | | 城市 |
| country | VARCHAR(100) | | 国家 |
| timezone | VARCHAR(50) | | 时区 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 创建时间 |

**索引设计：**
- `idx_locations_coordinates` ON (latitude, longitude)
- `idx_locations_city` ON city

#### 1.3.4 天气记录表 (weather_records)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 天气记录唯一标识 |
| location_id | UUID | REFERENCES locations(id) | 关联位置 |
| weather_main | VARCHAR(50) | | 主要天气状况 |
| weather_description | VARCHAR(100) | | 详细天气描述 |
| weather_icon | VARCHAR(10) | | 天气图标代码 |
| temperature | DECIMAL(5,2) | | 温度（摄氏度） |
| recorded_at | TIMESTAMPTZ | DEFAULT now() | 记录时间 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 创建时间 |

**索引设计：**
- `idx_weather_records_location` ON location_id
- `idx_weather_records_recorded_at` ON recorded_at

#### 1.3.5 云朵收藏表 (cloud_collections)

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|----------|------|------|
| id | UUID | PRIMARY KEY, DEFAULT gen_random_uuid() | 收藏记录唯一标识 |
| user_id | UUID | REFERENCES users(id) ON DELETE CASCADE | 关联用户 |
| tool_id | VARCHAR(20) | REFERENCES capture_tools(id) | 使用的捕云工具 |
| location_id | UUID | REFERENCES locations(id) | 拍摄地点 |
| weather_id | UUID | REFERENCES weather_records(id) | 天气记录 |
| original_image_url | TEXT | NOT NULL | 原始图片URL |
| cropped_image_url | TEXT | | 裁剪后图片URL |
| thumbnail_url | TEXT | | 缩略图URL |
| cloud_name | VARCHAR(200) | NOT NULL | AI生成的云朵名称 |
| cloud_description | TEXT | | AI生成的云朵描述 |
| keywords | TEXT[] | | 关键词标签数组 |
| image_features | JSONB | | 图像特征分析结果 |
| capture_time | TIMESTAMPTZ | NOT NULL | 拍摄时间 |
| is_favorite | BOOLEAN | DEFAULT false | 是否收藏 |
| is_public | BOOLEAN | DEFAULT false | 是否公开（预留） |
| view_count | INTEGER | DEFAULT 0 | 查看次数 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 创建时间 |
| updated_at | TIMESTAMPTZ | DEFAULT now() | 更新时间 |

**索引设计：**
- `idx_cloud_collections_user` ON user_id
- `idx_cloud_collections_tool` ON tool_id
- `idx_cloud_collections_capture_time` ON capture_time
- `idx_cloud_collections_user_capture_time` ON (user_id, capture_time DESC)
- `idx_cloud_collections_keywords` ON keywords USING GIN
- `idx_cloud_collections_image_features` ON image_features USING GIN

## 2. SQL建表语句

### 2.1 创建用户表

```sql
-- 创建用户表
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    username VARCHAR(50) UNIQUE,
    display_name VARCHAR(100),
    is_anonymous BOOLEAN DEFAULT true,
    device_id VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    last_active_at TIMESTAMPTZ DEFAULT now()
);

-- 创建索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_device_id ON users(device_id);
CREATE INDEX idx_users_created_at ON users(created_at);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2.2 创建捕云工具表

```sql
-- 创建捕云工具表
CREATE TABLE capture_tools (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    emoji VARCHAR(10) NOT NULL,
    description TEXT NOT NULL,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 创建索引
CREATE INDEX idx_capture_tools_active_sort ON capture_tools( sort_order);


### 2.3 创建地理位置表

```sql
-- 创建地理位置表
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    address TEXT,
    city VARCHAR(100),
    country VARCHAR(100),
    timezone VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 创建索引
CREATE INDEX idx_locations_coordinates ON locations(latitude, longitude);
CREATE INDEX idx_locations_city ON locations(city);
```

### 2.4 创建天气记录表

```sql
-- 创建天气记录表
CREATE TABLE weather_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    location_id UUID REFERENCES locations(id),
    weather_main VARCHAR(50),
    weather_description VARCHAR(100),
    weather_icon VARCHAR(10),
    temperature DECIMAL(5,2),
    recorded_at TIMESTAMPTZ DEFAULT now(),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 创建索引
CREATE INDEX idx_weather_records_location ON weather_records(location_id);
CREATE INDEX idx_weather_records_recorded_at ON weather_records(recorded_at);
```

### 2.5 创建云朵收藏表

```sql
-- 创建云朵收藏表
CREATE TABLE cloud_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    tool_id VARCHAR(20) REFERENCES capture_tools(id),
    location_id UUID REFERENCES locations(id),
    weather_id UUID REFERENCES weather_records(id),
    original_image_url TEXT NOT NULL,
    cropped_image_url TEXT,
    thumbnail_url TEXT,
    cloud_name VARCHAR(200) NOT NULL,
    cloud_description TEXT,
    keywords TEXT[],
    image_features JSONB,
    capture_time TIMESTAMPTZ NOT NULL,
    is_favorite BOOLEAN DEFAULT false,
    is_public BOOLEAN DEFAULT false,
    view_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 创建索引
CREATE INDEX idx_cloud_collections_user ON cloud_collections(user_id);
CREATE INDEX idx_cloud_collections_tool ON cloud_collections(tool_id);
CREATE INDEX idx_cloud_collections_capture_time ON cloud_collections(capture_time);
CREATE INDEX idx_cloud_collections_user_capture_time ON cloud_collections(user_id, capture_time DESC);
CREATE INDEX idx_cloud_collections_keywords ON cloud_collections USING GIN(keywords);
CREATE INDEX idx_cloud_collections_image_features ON cloud_collections USING GIN(image_features);

-- 创建更新时间触发器
CREATE TRIGGER update_cloud_collections_updated_at BEFORE UPDATE ON cloud_collections
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2.6 创建RLS (Row Level Security) 策略

```sql
-- 启用RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE cloud_collections ENABLE ROW LEVEL SECURITY;

-- 用户表RLS策略
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id OR is_anonymous = true);

CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

-- 云朵收藏表RLS策略
CREATE POLICY "Users can view own collections" ON cloud_collections
    FOR SELECT USING (
        user_id = auth.uid() OR 
        (SELECT is_anonymous FROM users WHERE id = user_id) = true
    );

CREATE POLICY "Users can insert own collections" ON cloud_collections
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update own collections" ON cloud_collections
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can delete own collections" ON cloud_collections
    FOR DELETE USING (user_id = auth.uid());
```

## 3. 对象存储设计

### 3.1 Storage Buckets 配置

#### 3.1.1 云朵图片存储桶 (cloud-images)

```sql
-- 创建云朵图片存储桶
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'cloud-images',
    'cloud-images',
    true,
    10485760, -- 10MB
    ARRAY['image/jpeg', 'image/png', 'image/webp']
);
```

**存储桶策略：**
```sql
-- 允许所有用户上传图片
CREATE POLICY "Allow authenticated uploads" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'cloud-images' AND auth.role() = 'authenticated');

-- 允许所有用户查看图片
CREATE POLICY "Allow public access" ON storage.objects
    FOR SELECT USING (bucket_id = 'cloud-images');

-- 允许用户删除自己的图片
CREATE POLICY "Allow users to delete own images" ON storage.objects
    FOR DELETE USING (bucket_id = 'cloud-images' AND auth.uid()::text = (storage.foldername(name))[1]);
```

### 3.2 文件夹结构设计

#### 3.2.1 云朵图片文件夹结构

```
cloud-images/
├── original/
│   ├── {user_id}/
│   │   ├── {year}/
│   │   │   ├── {month}/
│   │   │   │   └── {collection_id}_original.{ext}
├── cropped/
│   ├── {user_id}/
│   │   ├── {year}/
│   │   │   ├── {month}/
│   │   │   │   └── {collection_id}_cropped.{ext}
└── thumbnails/
    ├── {user_id}/
    │   ├── {year}/
    │   │   ├── {month}/
    │   │   │   └── {collection_id}_thumb.{ext}
```

#### 3.2.2 文件命名规则

- **原始图片**: `{collection_id}_original.{ext}`
- **裁剪图片**: `{collection_id}_cropped.{ext}`
- **缩略图**: `{collection_id}_thumb.{ext}`

**示例路径：**
```
cloud-images/original/550e8400-e29b-41d4-a716-446655440000/2025/01/abc123def456_original.jpg
cloud-images/cropped/550e8400-e29b-41d4-a716-446655440000/2025/01/abc123def456_cropped.jpg
cloud-images/thumbnails/550e8400-e29b-41d4-a716-446655440000/2025/01/abc123def456_thumb.jpg
```

### 3.3 文件上传处理流程

1. **原始图片上传** → `cloud-images/original/{user_id}/{year}/{month}/`
2. **图片裁剪处理** → `cloud-images/cropped/{user_id}/{year}/{month}/`
3. **生成缩略图** → `cloud-images/thumbnails/{user_id}/{year}/{month}/`
4. **更新数据库记录** → 保存所有图片URL到 `cloud_collections` 表

## 4. 数据库优化建议

### 4.1 性能优化

1. **分区表设计**：对于 `cloud_collections` 表，可按年份进行分区
2. **索引优化**：根据查询模式创建复合索引
3. **数据归档**：定期归档旧数据，保持表大小合理

### 4.2 数据备份策略

1. **自动备份**：利用 Supabase 的自动备份功能
2. **定期导出**：重要数据定期导出到外部存储
3. **版本控制**：数据库结构变更使用迁移脚本管理

### 4.3 监控指标

1. **存储使用量**：监控图片存储空间使用情况
2. **查询性能**：监控慢查询和数据库性能指标
3. **用户活跃度**：跟踪用户使用情况和增长趋势

## 5. 安全考虑

### 5.1 数据安全

1. **RLS策略**：确保用户只能访问自己的数据
2. **输入验证**：所有用户输入进行严格验证
3. **文件类型检查**：上传文件进行类型和大小限制

### 5.2 隐私保护

1. **匿名用户支持**：支持不注册即可使用
2. **数据最小化**：只收集必要的用户信息
3. **数据删除**：提供完整的数据删除功能

---

**注意事项：**
- 所有时间字段使用 `TIMESTAMPTZ` 类型，支持时区
- 使用 UUID 作为主键，避免ID猜测攻击
- JSONB 字段用于存储灵活的结构化数据
- 数组字段用于存储标签等多值数据
- 建议在生产环境中启用数据库连接池和缓存机制 