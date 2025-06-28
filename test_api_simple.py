import asyncio
import httpx
import json

async def test_basic_api():
    """测试基本的API连接（纯文本）"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk-VvjuMICkknX8CjFGAfOdK6DnnTTx24O4OUFTgKXSnI5qnpBO'
    }
    
    payload = {
        'model': 'gpt-4o',
        'messages': [
            {
                'role': 'user',
                'content': '请简单回复：你好'
            }
        ],
        'temperature': 1.1,
        'top_p': 0.9,
        'frequency_penalty': 0.8,
        'presence_penalty': 0.6,
        'max_tokens': 50
    }
    
    try:
        # 增加超时时间
        async with httpx.AsyncClient(timeout=300.0) as client:
            print("开始API调用...")
            response = await client.post('https://api.tu-zi.com/v1/chat/completions', headers=headers, json=payload)
            print(f'状态码: {response.status_code}')
            print(f'响应: {response.text}')
            
            if response.status_code == 200:
                data = response.json()
                print(f'AI回复: {data["choices"][0]["message"]["content"]}')
            
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()

async def test_cloud_naming_api():
    """测试云朵命名API（模拟generate_cloud_name_with_ark的调用）"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer sk-VvjuMICkknX8CjFGAfOdK6DnnTTx24O4OUFTgKXSnI5qnpBO'
    }
    
    prompt = """你是云朵命名大师，需要为一朵云起名字。

**工具类型**: broom (儿童脑内剧场童话混乱流)
**风格要求**: 你是一位5岁半的半职业云朵观察员 / 魔法剧作家

**云朵特征**:
- 形状: 积云
- 颜色: 白色  
- 质感: 蓬松

**拍摄环境**:
- 时间: 2024-01-15 14:30
- 天气: 晴朗
- 地点: 北京·天坛公园

请为这朵云生成一个富有创意的名字和简短描述。

要求：
1. 名字要符合工具的风格特色
2. 描述要生动有趣，不超过30字
3. 必须以JSON格式返回

返回格式：
{
    "name": "云朵名称",
    "description": "生动的描述文字",
    "style": "broom"
}"""
    
    payload = {
        'model': 'gpt-4o',
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'temperature': 1.1,
        'top_p': 0.9,
        'frequency_penalty': 0.8,
        'presence_penalty': 0.6,
        'max_tokens': 200
    }
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            print("开始云朵命名API调用...")
            response = await client.post('https://api.tu-zi.com/v1/chat/completions', headers=headers, json=payload)
            print(f'状态码: {response.status_code}')
            print(f'响应: {response.text[:500]}...')  # 只显示前500字符
            
            if response.status_code == 200:
                data = response.json()
                result_text = data["choices"][0]["message"]["content"]
                print(f'云朵命名结果: {result_text}')
                
                try:
                    result = json.loads(result_text)
                    print(f'解析成功: {result}')
                except json.JSONDecodeError:
                    print('JSON解析失败，但API调用成功')
                    
    except Exception as e:
        print(f'错误: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== 测试基本API连接 ===")
    asyncio.run(test_basic_api())
    
    print("\n=== 测试云朵命名API ===")
    asyncio.run(test_cloud_naming_api()) 