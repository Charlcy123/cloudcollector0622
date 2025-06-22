#!/usr/bin/env python3
"""
云彩收集手册 - API测试脚本
这个脚本帮助您测试后端API的各种功能
"""

import httpx
import asyncio
import json
import uuid
from datetime import datetime

# 配置API基础地址
BASE_URL = "http://localhost:8000"  # 本地开发服务器地址

class CloudAPITester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.device_id = str(uuid.uuid4())  # 生成测试用的设备ID
        self.user_id = None

    async def test_api_status(self):
        """测试API服务是否启动"""
        print("=== 测试API服务状态 ===")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/docs")
                if response.status_code == 200:
                    print("✅ API服务已启动，可以访问FastAPI文档")
                    print(f"📚 文档地址: {self.base_url}/docs")
                else:
                    print(f"❌ API服务可能有问题，状态码: {response.status_code}")
        except Exception as e:
            print(f"❌ 无法连接到API服务: {e}")
            print("💡 请确保您的后端服务已启动 (python main.py)")
            return False
        return True

    async def test_user_management(self):
        """测试用户管理API"""
        print("\n=== 测试用户管理API ===")
        
        async with httpx.AsyncClient() as client:
            # 1. 创建用户
            print("1. 测试创建用户...")
            user_data = {
                "device_id": self.device_id,
                "display_name": "测试用户"
            }
            
            response = await client.post(
                f"{self.base_url}/api/users", 
                json=user_data
            )
            
            if response.status_code == 200:
                user_info = response.json()
                self.user_id = user_info["id"]
                print(f"✅ 用户创建成功: {user_info['display_name']} (ID: {self.user_id})")
            else:
                print(f"❌ 用户创建失败: {response.status_code} - {response.text}")
                return False

            # 2. 获取用户信息
            print("2. 测试获取用户信息...")
            response = await client.get(f"{self.base_url}/api/users/{self.user_id}")
            
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ 获取用户信息成功: {user_info['display_name']}")
            else:
                print(f"❌ 获取用户信息失败: {response.status_code}")
        
        return True

    async def test_capture_tools(self):
        """测试捕云工具API"""
        print("\n=== 测试捕云工具API ===")
        
        async with httpx.AsyncClient() as client:
            # 获取工具列表
            response = await client.get(f"{self.base_url}/api/capture-tools")
            
            if response.status_code == 200:
                tools = response.json()
                print(f"✅ 获取捕云工具列表成功，共 {len(tools)} 个工具:")
                for tool in tools:
                    print(f"   {tool['emoji']} {tool['name']} ({tool['id']})")
                return tools
            else:
                print(f"❌ 获取捕云工具失败: {response.status_code}")
                return []

    async def test_weather_api(self):
        """测试天气API"""
        print("\n=== 测试天气API ===")
        
        async with httpx.AsyncClient() as client:
            # 测试北京的天气
            latitude, longitude = 39.9042, 116.4074
            
            response = await client.get(
                f"{self.base_url}/api/weather/current",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "units": "metric"
                }
            )
            
            if response.status_code == 200:
                weather_data = response.json()
                weather = weather_data["weather"]
                print(f"✅ 天气API测试成功:")
                print(f"   🌤️  天气: {weather['description']}")
                print(f"   🌡️  温度: {weather['temperature']}°C")
                print(f"   📍 位置ID: {weather_data['location_id']}")
            else:
                print(f"❌ 天气API测试失败: {response.status_code} - {response.text}")

    async def test_cloud_naming_api(self):
        """测试云朵命名API"""
        print("\n=== 测试云朵命名API ===")
        
        async with httpx.AsyncClient() as client:
            # 构造测试数据
            cloud_data = {
                "tool": "broom",  # 使用扫帚工具
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
            }
            
            response = await client.post(
                f"{self.base_url}/api/cloud/name",
                json=cloud_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 云朵命名API测试成功:")
                print(f"   ☁️  名称: {result['name']}")
                print(f"   📝 描述: {result['description']}")
                print(f"   🎨 风格: {result['style']}")
                return result
            else:
                print(f"❌ 云朵命名API测试失败: {response.status_code} - {response.text}")
                return None

    async def test_cloud_description_api(self):
        """测试云朵描述API"""
        print("\n=== 测试云朵描述API ===")
        
        async with httpx.AsyncClient() as client:
            description_data = {
                "cloudName": "魔法棉花糖云",
                "imageFeatures": {
                    "shape": "积云",
                    "color": "白色", 
                    "texture": "蓬松"
                },
                "tool": "broom"
            }
            
            response = await client.post(
                f"{self.base_url}/api/cloud/description",
                json=description_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 云朵描述API测试成功:")
                print(f"   📝 描述: {result['description']}")
                print(f"   🏷️  关键词: {', '.join(result['keywords'])}")
            else:
                print(f"❌ 云朵描述API测试失败: {response.status_code} - {response.text}")

    async def test_all_apis(self):
        """运行所有API测试"""
        print("🚀 开始云彩收集手册API测试")
        print("=" * 50)
        
        # 1. 检查服务状态
        if not await self.test_api_status():
            return
        
        # 2. 测试用户管理
        if not await self.test_user_management():
            return
            
        # 3. 测试捕云工具
        await self.test_capture_tools()
        
        # 4. 测试天气API
        await self.test_weather_api()
        
        # 5. 测试AI相关API
        await self.test_cloud_naming_api()
        await self.test_cloud_description_api()
        
        print("\n" + "=" * 50)
        print("🎉 API测试完成！")
        print(f"💡 您可以在浏览器中访问 {self.base_url}/docs 查看完整API文档")

async def main():
    """主函数"""
    tester = CloudAPITester()
    await tester.test_all_apis()

if __name__ == "__main__":
    print("欢迎使用云彩收集手册API测试工具!")
    print("这个脚本将帮助您测试后端API的各种功能\n")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 测试已停止")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        print("💡 请检查您的后端服务是否正常运行") 