import asyncio
import httpx
import json
import base64

# 自定义 OpenAI 风格 API 配置
CUSTOM_API_KEY = "sk-VvjuMICkknX8CjFGAfOdK6DnnTTx24O4OUFTgKXSnI5qnpBO"
CUSTOM_API_BASE = "https://api.tu-zi.com/v1/chat/completions"

# 本地API配置
LOCAL_API_BASE = "http://127.0.0.1:8000"

async def test_cloud_name_from_image():
    """测试直接从图像生成云朵名称的新API"""
    print("🧪 测试直接从图像生成云朵名称...")
    
    # 创建一个测试图像 (1x1像素的白色PNG)
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    payload = {
        "tool": "hand",
        "image": test_image_b64,
        "context": {
            "time": "下午2点",
            "weather": "晴朗",
            "location": "公园"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LOCAL_API_BASE}/api/cloud/name-from-image",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 图像命名API响应:")
                print(f"   名称: {data['name']}")
                print(f"   描述: {data['description']}")
                print(f"   风格: {data['style']}")
                return True
            else:
                print(f"❌ 图像命名API调用失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 图像命名API调用异常: {str(e)}")
        return False

async def test_cloud_description_from_image():
    """测试直接从图像生成云朵描述的新API"""
    print("🧪 测试直接从图像生成云朵描述...")
    
    # 创建一个测试图像
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    # 测试两种场景：有云朵名称 和 无云朵名称
    test_cases = [
        {
            "name": "有云朵名称",
            "payload": {
                "tool": "catPaw",
                "image": test_image_b64,
                "context": {
                    "time": "傍晚6点",
                    "weather": "多云",
                    "location": "阳台"
                },
                "cloudName": "软绵绵的猫爪云"
            }
        },
        {
            "name": "无云朵名称",
            "payload": {
                "tool": "broom",
                "image": test_image_b64,
                "context": {
                    "time": "上午10点",
                    "weather": "晴朗",
                    "location": "山顶"
                }
            }
        }
    ]
    
    results = []
    for test_case in test_cases:
        print(f"   测试场景: {test_case['name']}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{LOCAL_API_BASE}/api/cloud/description-from-image",
                    json=test_case["payload"],
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ 成功:")
                    print(f"      描述: {data['description']}")
                    print(f"      关键词: {data['keywords']}")
                    results.append(True)
                else:
                    print(f"   ❌ 失败: {response.status_code}")
                    print(f"      响应: {response.text}")
                    results.append(False)
                    
        except Exception as e:
            print(f"   ❌ 异常: {str(e)}")
            results.append(False)
    
    return all(results)

async def test_text_api():
    """测试文本生成API"""
    print("🧪 测试文本生成API...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CUSTOM_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": "为一朵白色蓬松的积云起一个富有创意的名字"
            }
        ],
        "temperature": 1.1,
        "top_p": 0.9,
        "frequency_penalty": 0.8,
        "presence_penalty": 0.6,
        "max_tokens": 100
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                print(f"✅ 文本API响应: {content}")
                return True
            else:
                print(f"❌ 文本API调用失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 文本API调用异常: {str(e)}")
        return False

async def test_image_api():
    """测试图像分析API（使用base64编码的测试图像）"""
    print("🧪 测试图像分析API...")
    
    # 创建一个简单的测试图像（1x1像素的白色PNG）
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CUSTOM_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "请描述这张图片的内容"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{test_image_b64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                print(f"✅ 图像API响应: {content}")
                return True
            else:
                print(f"❌ 图像API调用失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                return False
    except Exception as e:
        print(f"❌ 图像API调用异常: {str(e)}")
        return False

async def test_different_models():
    """测试不同的模型名称"""
    models_to_test = [
        "gpt-4o-fast",
        "gpt-4o", 
        "gpt-4",
        "gpt-3.5-turbo",
        "text-davinci-003",
        "claude-3-haiku"
    ]
    
    print("🧪 测试不同模型名称...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CUSTOM_API_KEY}"
    }
    
    for model in models_to_test:
        print(f"   尝试模型: {model}")
        
        payload = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, how are you?"
                }
            ],
            "max_tokens": 50
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    print(f"   ✅ {model} 成功: {content[:50]}...")
                    return model  # 返回第一个成功的模型
                else:
                    print(f"   ❌ {model} 失败: {response.status_code}")
                    
        except Exception as e:
            print(f"   ❌ {model} 异常: {str(e)}")
    
    return None

async def test_cloud_name_without_weather():
    """测试没有天气信息时的云朵命名"""
    print("🧪 测试没有天气信息时的云朵命名...")
    
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    # 测试场景：没有weather字段
    payload = {
        "tool": "broom",
        "image": test_image_b64,
        "context": {
            "time": "黄昏时分",
            # 注意：故意不提供weather字段
            "location": "海边"
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LOCAL_API_BASE}/api/cloud/name-from-image",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 无天气信息命名成功:")
                print(f"   名称: {data['name']}")
                print(f"   描述: {data['description']}")
                print(f"   风格: {data['style']}")
                return True
            else:
                print(f"❌ 无天气信息命名失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 无天气信息命名异常: {str(e)}")
        return False

async def test_cloud_description_without_weather():
    """测试没有天气信息时的云朵描述"""
    print("🧪 测试没有天气信息时的云朵描述...")
    
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    # 测试场景：没有weather字段
    payload = {
        "tool": "glassCover",
        "image": test_image_b64,
        "context": {
            "time": "午夜12点",
            # 注意：故意不提供weather字段
            "location": "屋顶"
        },
        "cloudName": "午夜展览品"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LOCAL_API_BASE}/api/cloud/description-from-image",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 无天气信息描述成功:")
                print(f"   描述: {data['description']}")
                print(f"   关键词: {data['keywords']}")
                return True
            else:
                print(f"❌ 无天气信息描述失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 无天气信息描述异常: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🚀 开始测试云朵收集手册API...")
    print(f"🌐 远程API地址: {CUSTOM_API_BASE}")
    print(f"🏠 本地API地址: {LOCAL_API_BASE}")
    print(f"🔑 API密钥: {CUSTOM_API_KEY[:20]}...（已隐藏）")
    print()
    
    # 测试基础的远程API
    print("📡 测试远程自定义OpenAI风格API:")
    text_result = await test_text_api()
    image_result = await test_image_api()
    print()
    
    # 测试新的本地API端点
    print("🏠 测试本地云朵命名和描述API:")
    name_result = await test_cloud_name_from_image()
    print()
    description_result = await test_cloud_description_from_image()
    print()
    
    # 测试没有天气信息时的云朵命名和描述
    print("🧪 测试没有天气信息时的云朵命名和描述...")
    name_without_weather_result = await test_cloud_name_without_weather()
    print()
    description_without_weather_result = await test_cloud_description_without_weather()
    print()
    
    # 总结
    print("📊 测试结果总结:")
    print(f"   远程文本API: {'✅ 正常' if text_result else '❌ 失败'}")
    print(f"   远程图像API: {'✅ 正常' if image_result else '❌ 失败'}")
    print(f"   本地云朵命名API: {'✅ 正常' if name_result else '❌ 失败'}")
    print(f"   本地云朵描述API: {'✅ 正常' if description_result else '❌ 失败'}")
    print(f"   无天气信息命名API: {'✅ 正常' if name_without_weather_result else '❌ 失败'}")
    print(f"   无天气信息描述API: {'✅ 正常' if description_without_weather_result else '❌ 失败'}")
    
    if name_result and description_result and name_without_weather_result and description_without_weather_result:
        print()
        print("🎉 新的图像直接输入API 测试通过！")
        print("📝 现在用户可以直接上传图像，系统会自动:")
        print("   1. 分析图像中的云朵特征")
        print("   2. 结合天气信息和工具风格")
        print("   3. 生成富有创意的云朵名称和描述")
        print()
        print("🔧 API使用方式:")
        print("   • 云朵命名: POST /api/cloud/name-from-image")
        print("   • 云朵描述: POST /api/cloud/description-from-image")
        print("   • 传统方式: POST /api/cloud/name (向后兼容)")
    else:
        print("⚠️  部分API测试失败，请检查配置和网络连接。")

if __name__ == "__main__":
    asyncio.run(main()) 