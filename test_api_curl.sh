#!/bin/bash

# 云彩收集手册 - curl API测试脚本
# 这个脚本使用curl命令测试各种API接口

# 设置API基础地址
BASE_URL="http://localhost:8000"

# 颜色输出函数
print_success() {
    echo -e "\033[32m✅ $1\033[0m"
}

print_error() {
    echo -e "\033[31m❌ $1\033[0m"
}

print_info() {
    echo -e "\033[34mℹ️  $1\033[0m"
}

print_header() {
    echo -e "\n\033[36m=== $1 ===\033[0m"
}

# 生成测试用的设备ID
DEVICE_ID=$(uuidgen)

echo "🚀 开始使用curl测试云彩收集手册API"
echo "📱 测试设备ID: $DEVICE_ID"

# 1. 测试API服务状态
print_header "测试API服务状态"
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/docs")
if [ "$response" -eq 200 ]; then
    print_success "API服务已启动"
    print_info "文档地址: $BASE_URL/docs"
else
    print_error "无法连接到API服务 (状态码: $response)"
    print_info "请确保后端服务已启动: python main.py"
    exit 1
fi

# 2. 测试创建用户
print_header "测试用户管理API"
print_info "创建测试用户..."

user_response=$(curl -s -X POST "$BASE_URL/api/users" \
    -H "Content-Type: application/json" \
    -d "{
        \"device_id\": \"$DEVICE_ID\",
        \"display_name\": \"curl测试用户\"
    }")

if echo "$user_response" | grep -q "id"; then
    print_success "用户创建成功"
    USER_ID=$(echo "$user_response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    print_info "用户ID: $USER_ID"
else
    print_error "用户创建失败"
    echo "响应: $user_response"
fi

# 3. 测试获取捕云工具
print_header "测试捕云工具API"
tools_response=$(curl -s "$BASE_URL/api/capture-tools")

if echo "$tools_response" | grep -q "broom"; then
    print_success "获取捕云工具列表成功"
    tool_count=$(echo "$tools_response" | grep -o '"id"' | wc -l)
    print_info "工具数量: $tool_count"
else
    print_error "获取捕云工具失败"
fi

# 4. 测试天气API
print_header "测试天气API"
print_info "查询北京天气..."

weather_response=$(curl -s "$BASE_URL/api/weather/current?latitude=39.9042&longitude=116.4074&units=metric")

if echo "$weather_response" | grep -q "temperature"; then
    print_success "天气API测试成功"
    temperature=$(echo "$weather_response" | grep -o '"temperature":[^,}]*' | cut -d':' -f2)
    weather_desc=$(echo "$weather_response" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
    print_info "天气: $weather_desc, 温度: ${temperature}°C"
else
    print_error "天气API测试失败"
    echo "响应: $weather_response"
fi

# 5. 测试云朵命名API
print_header "测试云朵命名API"
print_info "使用扫帚工具为积云命名..."

cloud_name_response=$(curl -s -X POST "$BASE_URL/api/cloud/name" \
    -H "Content-Type: application/json" \
    -d '{
        "tool": "broom",
        "imageFeatures": {
            "shape": "积云",
            "color": "白色",
            "texture": "蓬松"
        },
        "context": {
            "time": "下午3点",
            "weather": "晴朗",
            "location": "北京"
        }
    }')

if echo "$cloud_name_response" | grep -q "name"; then
    print_success "云朵命名API测试成功"
    cloud_name=$(echo "$cloud_name_response" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    cloud_desc=$(echo "$cloud_name_response" | grep -o '"description":"[^"]*"' | cut -d'"' -f4)
    print_info "云朵名称: $cloud_name"
    print_info "描述: $cloud_desc"
else
    print_error "云朵命名API测试失败"
    echo "响应: $cloud_name_response"
fi

# 6. 测试云朵描述API
print_header "测试云朵描述API"
description_response=$(curl -s -X POST "$BASE_URL/api/cloud/description" \
    -H "Content-Type: application/json" \
    -d '{
        "cloudName": "魔法棉花糖云",
        "imageFeatures": {
            "shape": "积云",
            "color": "白色",
            "texture": "蓬松"
        },
        "tool": "broom"
    }')

if echo "$description_response" | grep -q "description"; then
    print_success "云朵描述API测试成功"
else
    print_error "云朵描述API测试失败"
fi

echo -e "\n🎉 curl API测试完成！"
echo "💡 更多API详情请访问: $BASE_URL/docs" 