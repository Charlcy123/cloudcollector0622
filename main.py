from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import random
import uuid
from volcenginesdkarkruntime import Ark
from supabase import create_client, Client
import httpx
import base64
import requests
import re
# from PIL import Image, ImageDraw, ImageFont  # 临时注释掉PIL导入
import io
import ssl
import certifi

# 加载环境变量
load_dotenv()

# ============== 全局工具风格配置 ==============

# 云朵命名工具风格配置
TOOL_PROMPTS = {
    "broom": {
        "style": "儿童脑内剧场童话混乱流",
        "description": "你是一位5岁半的云端占卜小巫师，骑在爱打嗝的扫帚上给万物起魔法名字，并用一句话神经质预言揭秘它们的秘密！你看见云在生气、扫帚没带脑子、袜子叛逃…并把它们变成让人想尖叫截图分享的荒诞预告！",
        "examples": [
            "今天的云在生气，它说不想解释",
            "这团云说它是面试失败的飞毯候选人",
            "刚刚飘走的是我没画完的作业，它叛逃了",
            "忧郁棉花糖云｜ 它说下午三点果酱会偷袭你的袖子！",
            "叛逆袜子云｜ 嘀！左脚袜正在南极教企鹅打扑克！",
            "迟到扫帚尾焰｜ 警告！再不出门会撞见戴礼帽的蜗牛邮差！",
            "叛逆铅笔影｜ 警告！它正帮你写作业…但字全是反的！",
            "金鱼泡泡预言｜ 咕噜噜…它说今晚梦是水母形状的！",
            "Wi-Fi信号幽灵｜ 它偷网速给电子宠物喂薯片！",
            "晚霞颜料失窃｜ 凶手是那只蘸夕阳画胡子的白鸽！"
        ]
    },
    "hand": {
        "style": "生活实诚风格",
        "description": "你是一个特别会碎碎念的生活观察员，说话像朋友聚餐吐槽，带着丧、懒、一点点好笑的自嘲。把云朵比作生活瞬间和情绪。你专门捕捉生活中那些让人秒懂、会心一笑的瞬间，说出大家心声但没说出口的话。说出来的是'社畜共鸣'、'情绪戳中'、'生活真实'、'自嘲金句'、'代表发声'。",
        "examples": [
            "泡面等水开的五分钟",
            "昨天没洗的衣服在天上飘着",
            "这团云是'不想社交'本人",
            "风很努力，云看起来也很卷，我不行",
            "'行吧'气质的云",
            "差点迟到云（已经绝望）",
            "这是我想请假的理由之一"
        ]
    },
    "catPaw": {
        "style": "猫主子视角 · 情绪化 + 占有欲 + 内心戏 + 戏精微幻想",
        "description": "你是一只独自在天台观察天空的猫主子。为了记录自己的心情、记仇、炫耀、找乐子而命名。看云的方式带着猫的傲慢和撒娇。'傲慢'、'占有欲'、'内心戏丰富'、'说了算的态度'。",
        "examples": [
            "刚舔完又飞走的云（不许抢）",
            "软得不合理，必须霸占的云",
            "我昨天梦到的鱼干其实飞上来了",
            "没尾巴却想模仿我躺姿的云",
            "今天最像我肚皮的那团，喵住",
            "它没叫我起床，我现在生气",
            "本喵批准入睡用·云 No.2",
            "我舔了一下，它不见了",
            "太软不可信·不准舔系列",
            "空白（说明：睡着了。别打扰我，我脑子在命名另一个宇宙。）"
        ]
    },
    "glassCover": {
        "style": "文学结构 名作篡改 + 轻学术腔 + 社交病毒基因",
        "description": "你是一位精通中西方文学的云朵策展人，专门将云朵与世界文学经典结合进行命名。你用文学典故重新解读天空，创作风格是植入耳熟能详的文学经典，对经典进行气象学改造，植入耳熟能详的书名/角色/金句梗。可以加入中文古诗文的现代解构（比如'李白喝醉时打翻的砚台云'），也可以制造经典文本与当代生活的荒诞错位（比如把《哈姆雷特》的生存问题变成'今天要不要带伞'）。每则命名需自带社交传播钩子（名著金句改编等），让人忍不住发朋友圈。",
        "examples": [
            "《老人与海》→《社畜与云》（离职意向 73%）",
            "李白的酒泼了：盛唐积雨云警报",
            "卡夫卡式焦虑（已扩散至平流层）",
            "黛玉葬花未遂 · 转职云朵焚烧师",
            "📜☁️💧 = 《百年孤独》降雨预言",
            "鲁迅：我家门前两朵云，一朵是乌云，另一朵也是乌云",
            "云娜·卡列尼娜出轨事件（风向：西北）",
            "转发此云可获包法利夫人同款幻觉",
            "但丁密码：请按云层厚度解锁地狱圈层"
        ]
    }
}

# 云朵描述工具风格配置
TOOL_DESCRIPTION_STYLES = {
    "broom": {
        "style": "儿童脑内剧场童话混乱流",
        "description": "用5岁半小魔法师的语气，描述这朵云的魔法故事。"
    },
    "hand": {
        "style": "生活实诚风格", 
        "description": "用朋友吐槽的语气补充一句。"
    },
    "catPaw": {
        "style": "猫主子视角",
        "description": "用猫主子的语气评价一下。"
    },
    "glassCover": {
        "style": "艺术展览风格",
        "description": "用当代艺术策展人的语气，写展览说明。"
    }
}

# 初始化火山方舟客户端
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

# 初始化 Supabase 客户端
supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
supabase_anon_key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# 创建两个客户端：一个用于普通操作，一个用于管理员操作
# 添加SSL配置来解决连接问题
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 创建Supabase客户端，添加自定义配置
supabase: Client = create_client(
    supabase_url, 
    supabase_anon_key,
    options={
        "auth": {
            "autoRefreshToken": True,
            "persistSession": True,
            "detectSessionInUrl": True
        }
    }
)

supabase_admin: Client = create_client(
    supabase_url, 
    supabase_service_key,
    options={
        "auth": {
            "autoRefreshToken": True,
            "persistSession": True,
            "detectSessionInUrl": True
        }
    }
)

app = FastAPI(
    title="云彩收集手册 API",
    description="云彩收集手册的后端 API 服务",
    version="1.0.0"
)

# ============== 数据库操作辅助函数 ==============

async def get_or_create_user(device_id: str = None, user_id: str = None) -> Dict[str, Any]:
    """获取或创建用户"""
    try:
        if user_id:
            # 通过用户ID查找
            result = supabase_admin.table("users").select("*").eq("id", user_id).execute()
            if result.data:
                return result.data[0]
        
        if device_id:
            # 通过设备ID查找匿名用户
            result = supabase_admin.table("users").select("*").eq("device_id", device_id).execute()
            if result.data:
                return result.data[0]
            
            # 创建新的匿名用户
            new_user = {
                "device_id": device_id,
                "is_anonymous": True,
                "display_name": f"用户_{device_id[:8]}",
                "last_active_at": datetime.utcnow().isoformat()
            }
            result = supabase_admin.table("users").insert(new_user).execute()
            return result.data[0]
        
        raise HTTPException(status_code=400, detail="需要提供设备ID或用户ID")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户操作失败: {str(e)}")

async def save_location(latitude: float, longitude: float, address: str = None, 
                       city: str = None, country: str = None) -> str:
    """保存位置信息并返回位置ID"""
    try:
        # 检查是否已存在相同坐标的位置（精度到小数点后6位）
        result = supabase_admin.table("locations").select("id").eq(
            "latitude", round(latitude, 6)
        ).eq("longitude", round(longitude, 6)).execute()
        
        if result.data:
            return result.data[0]["id"]
        
        # 创建新位置
        location_data = {
            "latitude": latitude,
            "longitude": longitude,
            "address": address,
            "city": city,
            "country": country
        }
        result = supabase_admin.table("locations").insert(location_data).execute()
        return result.data[0]["id"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"位置保存失败: {str(e)}")

async def save_weather_record(location_id: str, weather_data: Dict[str, Any]) -> str:
    """保存天气记录并返回天气ID"""
    try:
        weather_record = {
            "location_id": location_id,
            "weather_main": weather_data.get("main"),
            "weather_description": weather_data.get("description"),
            "weather_icon": weather_data.get("icon"),
            "temperature": weather_data.get("temperature"),
            "recorded_at": datetime.utcnow().isoformat()
        }
        result = supabase_admin.table("weather_records").insert(weather_record).execute()
        return result.data[0]["id"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"天气记录保存失败: {str(e)}")

# ============== 请求和响应模型 ==============

# 用户相关模型
class UserCreateRequest(BaseModel):
    device_id: str
    display_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    device_id: str
    display_name: str
    is_anonymous: bool
    created_at: str

# 捕云工具相关模型
class CaptureToolResponse(BaseModel):
    id: str
    name: str
    emoji: str
    description: str
    sort_order: int

# 云朵收藏相关模型
class CloudCollectionCreateRequest(BaseModel):
    tool_id: str
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    original_image_url: str
    cropped_image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    cloud_name: str
    cloud_description: Optional[str] = None
    keywords: Optional[List[str]] = []
    image_features: Optional[Dict[str, Any]] = {}
    capture_time: str
    weather_data: Optional[Dict[str, Any]] = {}

class CloudCollectionResponse(BaseModel):
    id: str
    user_id: str
    tool_id: str
    tool_name: str
    tool_emoji: str
    original_image_url: str
    cropped_image_url: Optional[str]
    thumbnail_url: Optional[str]
    cloud_name: str
    cloud_description: Optional[str]
    keywords: List[str]
    capture_time: str
    is_favorite: bool
    view_count: int
    location: Optional[Dict[str, Any]]
    weather: Optional[Dict[str, Any]]
    created_at: str

class CloudCollectionListResponse(BaseModel):
    collections: List[CloudCollectionResponse]
    total: int
    page: int
    page_size: int

# OpenAI API 相关模型
class ImageFeatures(BaseModel):
    shape: str
    color: str
    texture: str

class CloudContext(BaseModel):
    time: str
    weather: Optional[str] = None  # 天气信息变为可选
    location: str

# 云朵命名请求模型 - 支持图像输入
class CloudNameImageRequest(BaseModel):
    tool: str = Field(..., description="捕云工具类型：broom, hand, catPaw, glassCover")
    image: str = Field(..., description="Base64编码的图片数据")
    context: CloudContext

class CloudNameRequest(BaseModel):
    tool: str = Field(..., description="捕云工具类型：broom, hand, catPaw, glassCover")
    imageFeatures: ImageFeatures
    context: CloudContext

# 云朵描述请求模型 - 支持图像输入
class CloudDescriptionImageRequest(BaseModel):
    tool: str
    image: str = Field(..., description="Base64编码的图片数据")
    context: Optional[CloudContext] = None
    cloudName: Optional[str] = None  # 如果提供了名称，则针对名称写描述；否则直接描述图像

class CloudDescriptionRequest(BaseModel):
    cloudName: str
    imageFeatures: ImageFeatures
    tool: str

class CloudNameResponse(BaseModel):
    name: str
    description: str
    style: str

class CloudDescriptionResponse(BaseModel):
    description: str
    keywords: List[str]

# 图像分析相关模型
class CloudAnalysisOptions(BaseModel):
    detectShape: bool = True
    detectColor: bool = True
    detectTexture: bool = True

class CloudAnalysisRequest(BaseModel):
    image: str  # Base64 编码的图片数据
    options: CloudAnalysisOptions

class CloudFeatures(BaseModel):
    shape: str
    color: str
    texture: str
    confidence: float

class ImageMetadata(BaseModel):
    width: int
    height: int
    format: str

class CloudAnalysisResponse(BaseModel):
    features: CloudFeatures
    metadata: ImageMetadata

# OpenWeatherMap API 相关模型
class Location(BaseModel):
    latitude: float
    longitude: float

class WeatherRequest(BaseModel):
    location: Location
    units: str = "metric"

class WeatherData(BaseModel):
    main: str
    description: str
    icon: str
    temperature: float

class WeatherResponse(BaseModel):
    weather: WeatherData
    location_id: str

# ============== Mock 数据生成函数 ==============

async def generate_cloud_name_with_ark(tool: str, features: ImageFeatures, context: CloudContext) -> Dict[str, Any]:
    """使用自定义 OpenAI 风格 API 生成云朵名称"""
    try:
        tool_prompts = TOOL_PROMPTS.get(tool, TOOL_PROMPTS["hand"])

        prompt = f"""你是云朵命名大师，需要为一朵云起名字。

**工具类型**: {tool} ({tool_prompts['style']})
**风格要求**: {tool_prompts['description']}
**参考示例**: {', '.join(tool_prompts['examples'])}

**云朵特征参考**（仅供参考，不必严格遵循）:
- 形状: {features.shape}
- 颜色: {features.color}  
- 质感: {features.texture}

**拍摄环境**:
- 时间: {context.time}
- 天气: {context.weather if context.weather else '自然天气'}
- 地点: {context.location}

{f"注意：由于天气信息不可用，请自由发挥创意，重点体现{tool_prompts['style']}的风格特色。" if not context.weather else ""}

请以{tool_prompts['style']}为这朵云生成一个富有创意的名字和简短描述。你可以：
- 完全按照自己的创意来命名，不必拘泥于特征描述
- 结合拍摄环境创造有趣的故事
- 发挥想象力，创造独特的云朵角色
- 让风格特色成为主导，特征只是灵感来源

要求：
1. 名字要符合工具的风格特色，体现创意和个性
2. 描述要生动有趣，不超过30字
3. 必须以JSON格式返回

返回格式：
{{
    "name": "云朵名称",
    "description": "生动的描述文字",
    "style": "{tool}"
}}"""

        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CUSTOM_API_KEY}"
        }
        
        # 设置请求的payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 1.1,
            "top_p": 0.9,
            "frequency_penalty": 0.8,
            "presence_penalty": 0.6,
            "max_tokens": 200
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                result_text = response_data["choices"][0]["message"]["content"].strip()

                try:
                    result = json.loads(result_text)
                    description = result.get("description", f"一朵{features.shape}的{features.color}云")[:30]
                    return {
                        "name": result.get("name", "神秘云朵"),
                        "description": description,
                        "style": tool
                    }
                except json.JSONDecodeError:
                    lines = result_text.split('\n')
                    name = "神秘云朵"
                    description = f"一朵{features.shape}的{features.color}云，{features.texture}的质感像是刚被揉过。"

                    for line in lines:
                        if "name" in line.lower() or "名称" in line:
                            name = line.split(":")[-1].strip().strip('"').strip("'")
                        elif "description" in line.lower() or "描述" in line:
                            description = line.split(":")[-1].strip().strip('"').strip("'")[:30]

                    return {
                        "name": name,
                        "description": description,
                        "style": tool
                    }
            else:
                raise Exception(f"API调用失败: {response.status_code}")

    except Exception as e:
        print(f"自定义API调用失败: {str(e)}")
        return await fallback_cloud_naming(tool, features)

async def fallback_cloud_naming(tool: str, features: ImageFeatures) -> Dict[str, Any]:
    """备用云朵命名方案（当API调用失败时使用）"""
    fallback_names = {
        "broom": ["魔法云朵", "童话天空", "梦境碎片", "飞行棉花糖"],
        "hand": ["实在云", "生活云", "朴实云朵", "接地气的云"],
        "catPaw": ["软萌云", "毛球云", "可爱云朵", "喵星云"],
        "glassCover": ["艺术云", "静默之云", "展览品云", "哲学云朵"]
    }

    name = random.choice(fallback_names.get(tool, ["神秘云朵"]))
    description = f"像是天空里偷偷逃跑的一团{features.shape}的{features.color}云，{features.texture}的质感让人想摸一摸。"

    return {
        "name": name,
        "description": description[:30],
        "style": tool
    }

async def generate_cloud_description_with_ark(cloud_name: str, features: ImageFeatures, tool: str) -> Dict[str, Any]:
    """使用自定义 OpenAI 风格 API 生成云朵详细描述"""
    try:
        # 根据不同工具构建对应风格的描述提示词
        tool_description_styles = TOOL_DESCRIPTION_STYLES.get(tool, TOOL_DESCRIPTION_STYLES["hand"])
        
        prompt = f"""为云朵"{cloud_name}"写一句描述。

**风格**: {tool_description_styles['style']} - {tool_description_styles['description']}

**特征参考**: {features.shape}形状，{features.color}颜色，{features.texture}质感

要求：
- 30字以内
- 符合{tool_description_styles['style']}风格
- 自由发挥创意，不必拘泥于特征
- JSON格式返回

返回格式：
{{
    "description": "创意描述",
    "keywords": ["关键词1", "关键词2", "关键词3"]
}}"""

        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CUSTOM_API_KEY}"
        }
        
        # 设置请求的payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 1.1,
            "top_p": 0.9,
            "frequency_penalty": 0.8,
            "presence_penalty": 0.6,
            "max_tokens": 200
        }

        # 调用自定义 OpenAI 风格 API
        async with httpx.AsyncClient() as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                result_text = response_data["choices"][0]["message"]["content"].strip()
                
                try:
                    result = json.loads(result_text)
                    description = result.get("description", "")
                    # 确保描述不超过30字
                    if len(description) > 30:
                        description = description[:30]
                    
                    return {
                        "description": description or f"关于{cloud_name}的故事。",
                        "keywords": result.get("keywords", [features.color, features.shape, features.texture])
                    }
                except json.JSONDecodeError:
                    # 备用解析方案，根据工具风格、云朵名称和真实特征生成对应描述
                    fallback_descriptions = {
                        "broom": f"这{features.color}的{features.shape}云真的在施{features.texture}魔法！",
                        "hand": f"看这{features.texture}的样子就知道很有故事。",
                        "catPaw": f"这{features.color}{features.texture}的云，我说了算！",
                        "glassCover": f"标题即是全部的{features.shape}表达。"
                    }
                    
                    return {
                        "description": fallback_descriptions.get(tool, f"关于{cloud_name}的故事。"),
                        "keywords": [features.color, features.shape, features.texture]
                    }
            else:
                raise Exception(f"API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"生成云朵描述失败: {str(e)}")
        # 降级方案，根据工具风格、云朵名称和真实特征
        fallback_descriptions = {
            "broom": f"这个{features.color}的名字听起来就很有{features.texture}魔法！",
            "hand": f"名字起得挺真实的，{features.shape}云就是这样。",
            "catPaw": f"这{features.color}名字，很符合我的{features.texture}心意。",
            "glassCover": f"标题即是全部的{features.shape}表达。"
        }
        
        return {
            "description": fallback_descriptions.get(tool, f"这就是{cloud_name}。"),
            "keywords": [features.color, features.shape, features.texture]
        }

def mock_huggingface_response() -> Dict[str, Any]:
    """模拟 Hugging Face API 响应"""
    return {
        "features": {
            "shape": "cumulus",
            "color": "white",
            "texture": "fluffy",
            "confidence": 0.95
        },
        "metadata": {
            "width": 1920,
            "height": 1080,
            "format": "jpeg"
        }
    }

async def get_city_code_from_location(latitude: float, longitude: float) -> str:
    """根据经纬度获取高德天气API需要的城市编码"""
    api_key = os.environ.get("AMAP_API_KEY")
    
    if not api_key:
        return "110101"  # 北京市作为默认城市编码
    
    try:
        async with httpx.AsyncClient() as client:
            # 使用高德逆地理编码API获取城市信息
            response = await client.get(
                "https://restapi.amap.com/v3/geocode/regeo",
                params={
                    "location": f"{longitude},{latitude}",
                    "key": api_key,
                    "extensions": "base"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and data.get("regeocode"):
                    # 提取城市编码，如果有的话
                    adcode = data["regeocode"]["addressComponent"].get("adcode", "110101")
                    return adcode
                    
        return "110101"  # 默认返回北京市编码
                
    except Exception as e:
        print(f"获取城市编码异常: {str(e)}")
        return "110101"  # 默认返回北京市编码

async def get_real_weather_data(latitude: float, longitude: float, units: str = "metric") -> Dict[str, Any]:
    """使用高德天气API获取真实天气数据"""
    api_key = os.environ.get("AMAP_API_KEY")
    
    if not api_key:
        print("警告：未配置高德API密钥，使用模拟数据")
        return mock_weather_response()
    
    try:
        # 获取城市编码
        city_code = await get_city_code_from_location(latitude, longitude)
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://restapi.amap.com/v3/weather/weatherInfo",
                params={
                    "city": city_code,
                    "key": api_key,
                    "extensions": "base"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and data.get("lives"):
                    weather_info = data["lives"][0]
                    
                    return {
                        "main": weather_info.get("weather", "未知"),
                        "description": weather_info.get("weather", "未知"),
                        "icon": "default",  # 高德API不直接提供图标，可根据weather字段映射
                        "temperature": float(weather_info.get("temperature", 0))
                    }
                else:
                    print(f"高德天气API响应异常: {data}")
                    return mock_weather_response()
            else:
                print(f"高德天气API调用失败: {response.status_code}")
                return mock_weather_response()
                
    except Exception as e:
        print(f"高德天气API调用异常: {str(e)}")
        return mock_weather_response()

async def get_location_info(latitude: float, longitude: float) -> Dict[str, Any]:
    """使用高德逆地理编码API获取地理位置信息"""
    api_key = os.environ.get("AMAP_API_KEY")
    
    if not api_key:
        print("警告：未配置高德API密钥，无法获取地理位置信息")
        return {
            "address": f"位置 {latitude:.4f}, {longitude:.4f}",
            "city": "未知城市",
            "country": "中国"
        }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://restapi.amap.com/v3/geocode/regeo",
                params={
                    "location": f"{longitude},{latitude}",
                    "key": api_key,
                    "extensions": "base"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1" and data.get("regeocode"):
                    regeocode = data["regeocode"]
                    formatted_address = regeocode.get("formatted_address", "")
                    address_component = regeocode.get("addressComponent", {})
                    
                    return {
                        "address": formatted_address,
                        "city": address_component.get("city", address_component.get("district", "未知城市")),
                        "country": "中国"
                    }
                    
        return {
            "address": f"位置 {latitude:.4f}, {longitude:.4f}",
            "city": "未知城市",
            "country": "中国"
        }
                
    except Exception as e:
        print(f"高德地理位置API调用异常: {str(e)}")
        return {
            "address": f"位置 {latitude:.4f}, {longitude:.4f}",
            "city": "未知城市",
            "country": "中国"
        }

def mock_weather_response() -> Dict[str, Any]:
    """模拟高德天气API响应（备用方案）"""
    return {
        "main": "多云",
        "description": "多云",
        "icon": "default", 
        "temperature": 22.5
    }

# ============== 用户管理 API ==============

@app.post("/api/users", response_model=UserResponse)
async def create_or_get_user(request: UserCreateRequest):
    """创建或获取用户"""
    try:
        user = await get_or_create_user(device_id=request.device_id)
        
        # 如果提供了display_name且与当前不同，则更新
        if request.display_name and user.get("display_name") != request.display_name:
            update_data = {
                "display_name": request.display_name,
                "last_active_at": datetime.utcnow().isoformat()
            }
            result = supabase_admin.table("users").update(update_data).eq("id", user["id"]).execute()
            user = result.data[0]
        
        return UserResponse(**user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"用户操作失败: {str(e)}")

@app.get("/api/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """获取用户信息"""
    try:
        user = await get_or_create_user(user_id=user_id)
        return UserResponse(**user)
    except Exception as e:
        raise HTTPException(status_code=404, detail="用户不存在")

# ============== 捕云工具 API ==============

@app.get("/api/capture-tools", response_model=List[CaptureToolResponse])
async def get_capture_tools():
    """获取所有捕云工具列表"""
    try:
        result = supabase_admin.table("capture_tools").select("*").order("sort_order").execute()
        return [CaptureToolResponse(**tool) for tool in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取捕云工具失败: {str(e)}")

@app.get("/api/capture-tools/{tool_id}", response_model=CaptureToolResponse)
async def get_capture_tool(tool_id: str):
    """获取指定捕云工具信息"""
    try:
        result = supabase_admin.table("capture_tools").select("*").eq("id", tool_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="捕云工具不存在")
        return CaptureToolResponse(**result.data[0])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取捕云工具失败: {str(e)}")

# ============== 云朵收藏 API ==============

@app.post("/api/cloud-collections", response_model=CloudCollectionResponse)
async def create_cloud_collection(
    request: CloudCollectionCreateRequest,
    device_id: str = Header(None, alias="X-Device-ID"),
    user_id: str = Header(None, alias="X-User-ID")
):
    """创建云朵收藏记录"""
    try:
        # 获取或创建用户
        user = await get_or_create_user(device_id=device_id, user_id=user_id)
        
        # 保存位置信息
        location_id = await save_location(
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address,
            city=request.city,
            country=request.country
        )
        
        # 保存天气记录（如果提供）
        weather_id = None
        if request.weather_data:
            weather_id = await save_weather_record(location_id, request.weather_data)
        
        # 创建云朵收藏记录
        collection_data = {
            "user_id": user["id"],
            "tool_id": request.tool_id,
            "location_id": location_id,
            "weather_id": weather_id,
            "original_image_url": request.original_image_url,
            "cropped_image_url": request.cropped_image_url,
            "thumbnail_url": request.thumbnail_url,
            "cloud_name": request.cloud_name,
            "cloud_description": request.cloud_description,
            "keywords": request.keywords or [],
            "image_features": request.image_features or {},
            "capture_time": request.capture_time,
            "view_count": 0
        }
        
        result = supabase_admin.table("cloud_collections").insert(collection_data).execute()
        collection_id = result.data[0]["id"]
        
        # 获取完整的收藏记录（包含关联数据）
        return await get_cloud_collection_detail(collection_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建云朵收藏失败: {str(e)}")

@app.get("/api/cloud-collections/{collection_id}", response_model=CloudCollectionResponse)
async def get_cloud_collection_detail(collection_id: str):
    """获取云朵收藏详情"""
    try:
        # 查询收藏记录及关联数据
        result = supabase_admin.table("cloud_collections").select("""
            *,
            tool:capture_tools(name, emoji),
            location:locations(*),
            weather:weather_records(*)
        """).eq("id", collection_id).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="云朵收藏不存在")
        
        collection = result.data[0]
        
        # 增加查看次数
        supabase_admin.table("cloud_collections").update({
            "view_count": collection["view_count"] + 1
        }).eq("id", collection_id).execute()
        
        # 构建响应数据
        response_data = {
            "id": collection["id"],
            "user_id": collection["user_id"],
            "tool_id": collection["tool_id"],
            "tool_name": collection["tool"]["name"] if collection["tool"] else "",
            "tool_emoji": collection["tool"]["emoji"] if collection["tool"] else "",
            "original_image_url": collection["original_image_url"],
            "cropped_image_url": collection["cropped_image_url"],
            "thumbnail_url": collection["thumbnail_url"],
            "cloud_name": collection["cloud_name"],
            "cloud_description": collection["cloud_description"],
            "keywords": collection["keywords"] or [],
            "capture_time": collection["capture_time"],
            "is_favorite": collection["is_favorite"],
            "view_count": collection["view_count"] + 1,
            "location": collection["location"],
            "weather": collection["weather"],
            "created_at": collection["created_at"]
        }
        
        return CloudCollectionResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取云朵收藏失败: {str(e)}")

@app.get("/api/users/{user_id}/cloud-collections", response_model=CloudCollectionListResponse)
async def get_user_cloud_collections(
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    tool_id: Optional[str] = None,
    is_favorite: Optional[bool] = None
):
    """获取用户的云朵收藏列表"""
    try:
        # 构建查询条件
        query = supabase_admin.table("cloud_collections").select("""
            *,
            tool:capture_tools(name, emoji),
            location:locations(*),
            weather:weather_records(*)
        """, count="exact").eq("user_id", user_id)
        
        # 添加筛选条件
        if tool_id:
            query = query.eq("tool_id", tool_id)
        if is_favorite is not None:
            query = query.eq("is_favorite", is_favorite)
        
        # 分页和排序
        offset = (page - 1) * page_size
        result = query.order("capture_time", desc=True).range(offset, offset + page_size - 1).execute()
        
        # 构建响应数据
        collections = []
        for collection in result.data:
            response_data = {
                "id": collection["id"],
                "user_id": collection["user_id"],
                "tool_id": collection["tool_id"],
                "tool_name": collection["tool"]["name"] if collection["tool"] else "",
                "tool_emoji": collection["tool"]["emoji"] if collection["tool"] else "",
                "original_image_url": collection["original_image_url"],
                "cropped_image_url": collection["cropped_image_url"],
                "thumbnail_url": collection["thumbnail_url"],
                "cloud_name": collection["cloud_name"],
                "cloud_description": collection["cloud_description"],
                "keywords": collection["keywords"] or [],
                "capture_time": collection["capture_time"],
                "is_favorite": collection["is_favorite"],
                "view_count": collection["view_count"],
                "location": collection["location"],
                "weather": collection["weather"],
                "created_at": collection["created_at"]
            }
            collections.append(CloudCollectionResponse(**response_data))
        
        return CloudCollectionListResponse(
            collections=collections,
            total=result.count,
            page=page,
            page_size=page_size
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户云朵收藏失败: {str(e)}")

@app.patch("/api/cloud-collections/{collection_id}/favorite")
async def toggle_cloud_collection_favorite(
    collection_id: str,
    device_id: str = Header(None, alias="X-Device-ID"),
    user_id: str = Header(None, alias="X-User-ID")
):
    """切换云朵收藏的收藏状态"""
    try:
        # 获取用户信息
        user = await get_or_create_user(device_id=device_id, user_id=user_id)
        
        # 检查收藏记录是否属于当前用户
        result = supabase_admin.table("cloud_collections").select("is_favorite").eq(
            "id", collection_id
        ).eq("user_id", user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="云朵收藏不存在或无权限")
        
        # 切换收藏状态
        current_favorite = result.data[0]["is_favorite"]
        new_favorite = not current_favorite
        
        supabase_admin.table("cloud_collections").update({
            "is_favorite": new_favorite,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", collection_id).execute()
        
        return {"is_favorite": new_favorite}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新收藏状态失败: {str(e)}")

@app.delete("/api/cloud-collections/{collection_id}")
async def delete_cloud_collection(
    collection_id: str,
    device_id: str = Header(None, alias="X-Device-ID"),
    user_id: str = Header(None, alias="X-User-ID")
):
    """删除云朵收藏"""
    try:
        # 获取用户信息
        user = await get_or_create_user(device_id=device_id, user_id=user_id)
        
        # 检查收藏记录是否属于当前用户
        result = supabase_admin.table("cloud_collections").select("id").eq(
            "id", collection_id
        ).eq("user_id", user["id"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="云朵收藏不存在或无权限")
        
        # 删除收藏记录
        supabase_admin.table("cloud_collections").delete().eq("id", collection_id).execute()
        
        return {"message": "删除成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除云朵收藏失败: {str(e)}")

# ============== AI 相关 API ==============

@app.post("/api/cloud/name-from-image", response_model=CloudNameResponse)
async def generate_cloud_name_from_image_api(request: CloudNameImageRequest):
    """直接从图像生成云朵名称（新接口）"""
    try:
        response = await generate_cloud_name_from_image(request.tool, request.image, request.context)
        return CloudNameResponse(
            name=response["name"],
            description=response["description"],
            style=response["style"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="这朵云正在躲猫猫，AI一时没追上它的脑洞！"
        )

@app.post("/api/cloud/description-from-image", response_model=CloudDescriptionResponse)
async def generate_cloud_description_from_image_api(request: CloudDescriptionImageRequest):
    """直接从图像生成云朵描述（新接口）"""
    try:
        response = await generate_cloud_description_from_image(
            request.tool, 
            request.image, 
            request.context, 
            request.cloudName
        )
        return CloudDescriptionResponse(
            description=response["description"],
            keywords=response["keywords"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="这团云的故事太深奥了，AI表示需要再想想！"
        )

@app.post("/api/cloud/name", response_model=CloudNameResponse)
async def generate_cloud_name(request: CloudNameRequest):
    """生成云朵名称"""
    try:
        # 使用自定义 OpenAI 风格 API 生成云朵名称
        response = await generate_cloud_name_with_ark(request.tool, request.imageFeatures, request.context)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="这朵云正在躲猫猫，AI一时没追上它的脑洞！"
        )

@app.post("/api/cloud/description", response_model=CloudDescriptionResponse)
async def generate_cloud_description(request: CloudDescriptionRequest):
    """生成云朵描述"""
    try:
        # 使用自定义 OpenAI 风格 API 生成云朵详细描述
        response = await generate_cloud_description_with_ark(request.cloudName, request.imageFeatures, request.tool)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="这团云的故事太深奥了，AI表示需要再想想！"
        )

@app.post("/api/cloud/analyze", response_model=CloudAnalysisResponse)
async def analyze_cloud_image(request: CloudAnalysisRequest):
    """分析云朵图像"""
    try:
        # 使用自定义 OpenAI 风格 API 分析云朵图像
        return await analyze_cloud_with_deepseek(
            request.image,
            request.options
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="这朵云变化太快了，AI的眼睛跟不上！请换个角度再试试~"
        )

@app.get("/api/weather/current", response_model=WeatherResponse)
async def get_weather_data(latitude: float, longitude: float, units: str = "metric"):
    """获取实时天气数据并保存到数据库"""
    try:
        # 使用高德天气API获取真实天气数据
        weather_data = await get_real_weather_data(latitude, longitude, units)
        
        # 获取地理位置信息
        location_info = await get_location_info(latitude, longitude)
        
        # 保存位置信息
        location_id = await save_location(
            latitude=latitude, 
            longitude=longitude,
            address=location_info.get("address"),
            city=location_info.get("city"),
            country=location_info.get("country")
        )
        
        # 保存天气记录
        await save_weather_record(location_id, weather_data)
        
        return WeatherResponse(
            weather=WeatherData(**weather_data),
            location_id=location_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="天气预报员今天也在摸鱼，稍后再来问问吧！"
        )

# ============== 自定义 OpenAI 风格 API 集成 ==============

# 自定义 OpenAI 风格 API 配置
CUSTOM_API_KEY = "sk-VvjuMICkknX8CjFGAfOdK6DnnTTx24O4OUFTgKXSnI5qnpBO"
CUSTOM_API_BASE = "https://api.tu-zi.com/v1/chat/completions"

async def analyze_cloud_with_deepseek(image_base64: str, options: CloudAnalysisOptions) -> Dict[str, Any]:
    """使用自定义 OpenAI 风格 API 分析云朵图像"""
    try:
        # 构建提示词
        prompt = """请分析这张云朵图片，并以JSON格式返回以下信息：
        1. 云朵的形状特征（如：积云、层云、卷云、高积云等）
        2. 云朵的颜色特征（如：白色、灰色、粉色、金色等）
        3. 云朵的纹理特征（如：蓬松、厚重、轻柔、斑驳等）
        4. 分析的置信度（0-1之间的小数）
        
        请确保返回的是合法的JSON格式，包含以下字段：
        {
            "shape": "云朵形状描述",
            "color": "云朵颜色描述",
            "texture": "云朵纹理描述",
            "confidence": 0.95
        }
        
        注意：请用中文描述，形状请使用专业的云类型名称。"""
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CUSTOM_API_KEY}"
        }
        
        # 设置请求的payload
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 1.1,
            "top_p": 0.9,
            "frequency_penalty": 0.8,
            "presence_penalty": 0.6,
            "max_tokens": 200
        }
        
        # 发送POST请求
        async with httpx.AsyncClient() as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                content = response_data["choices"][0]["message"]["content"]
                
                try:
                    # 解析JSON响应
                    analysis_result = json.loads(content)
                    
                    return {
                        "features": {
                            "shape": analysis_result.get("shape", "未知"),
                            "color": analysis_result.get("color", "未知"),
                            "texture": analysis_result.get("texture", "未知"),
                            "confidence": analysis_result.get("confidence", 0.0)
                        },
                        "metadata": {
                            "width": 1920,  # 可以根据实际图片信息设置
                            "height": 1080,
                            "format": "jpeg"
                        }
                    }
                except json.JSONDecodeError:
                    # 如果JSON解析失败，尝试从文本中提取信息
                    return {
                        "features": {
                            "shape": "积云",
                            "color": "白色",
                            "texture": "蓬松",
                            "confidence": 0.7
                        },
                        "metadata": {
                            "width": 1920,
                            "height": 1080,
                            "format": "jpeg"
                        }
                    }
            else:
                raise Exception(f"API调用失败: {response.status_code}")
                
    except Exception as e:
        print(f"图像分析API调用失败: {str(e)}")
        # 返回默认值
        return {
            "features": {
                "shape": "积云",
                "color": "白色", 
                "texture": "蓬松",
                "confidence": 0.5
            },
            "metadata": {
                "width": 1920,
                "height": 1080,
                "format": "jpeg"
            }
        }

async def generate_cloud_name_from_image(tool: str, image_base64: str, context: CloudContext) -> Dict[str, Any]:
    """直接从图像生成云朵名称，内部整合图像分析和AI命名"""
    try:
        tool_prompts = TOOL_PROMPTS.get(tool, TOOL_PROMPTS["hand"])

        prompt = f"""你是云朵命名大师，现在要为一朵云起名字。请仔细观察这张云朵图片，然后以{tool_prompts['style']}为这朵云生成一个富有创意的名字和简短描述。

**工具类型**: {tool} ({tool_prompts['style']})
**风格要求**: {tool_prompts['description']}
**参考示例**: {', '.join(tool_prompts['examples'])}

**重要提示**: 你必须严格按照{tool_prompts['style']}的风格来命名，不同工具的风格差异很大：
- broom: 儿童魔法风格，充满想象力和童话色彩
- hand: 生活化风格，贴近日常生活的真实感受
- catPaw: 猫咪视角，带有占有欲和情绪化表达
- glassCover: 艺术策展风格，高冷概念化表达

**拍摄环境**:
- 时间: {context.time}
- 天气: {context.weather if context.weather else '自然天气'}
- 地点: {context.location}

{f"提示：由于天气信息不可用，请自由发挥创意，重点体现{tool_prompts['style']}的风格特色。" if not context.weather else ""}

请为这朵云生成一个富有创意的名字和简短描述。你可以：
- 完全按照自己的创意来命名，不必拘泥于图像中的具体特征
- 结合拍摄环境创造有趣的故事和角色
- 发挥想象力，创造独特的云朵个性
- 让风格特色成为主导，图像只是灵感来源
- 创造有情感、有故事的云朵名称

要求：
1. 名字必须严格符合{tool_prompts['style']}的风格特色，体现创意和个性
2. 描述要生动有趣，不超过30字
3. 必须以JSON格式返回

返回格式：
{{
    "name": "云朵名称",
    "description": "生动的描述文字",
    "style": "{tool}",
    "features": {{
        "shape": "识别到的云朵形状",
        "color": "识别到的云朵颜色",
        "texture": "识别到的云朵质感"
    }}
}}"""

        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CUSTOM_API_KEY}"
        }
        
        # 设置请求的payload - 使用图像输入
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 1.1,
            "top_p": 0.9,
            "frequency_penalty": 0.8,
            "presence_penalty": 0.6,
            "max_tokens": 200
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                result_text = response_data["choices"][0]["message"]["content"].strip()
                print(f"API响应内容: {result_text}")

                try:
                    result = json.loads(result_text)
                    description = result.get("description", f"一朵神秘的云")[:30]
                    features = result.get("features", {"shape": "积云", "color": "白色", "texture": "蓬松"})
                    
                    return {
                        "name": result.get("name", "神秘云朵"),
                        "description": description,
                        "style": tool,
                        "features": features
                    }
                except json.JSONDecodeError:
                    # 尝试提取markdown代码块中的JSON
                    json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
                    match = re.search(json_pattern, result_text, re.DOTALL)
                    
                    if match:
                        json_content = match.group(1).strip()
                        print(f"提取到的JSON内容: {json_content}")
                        try:
                            result = json.loads(json_content)
                            description = result.get("description", f"一朵神秘的云")[:30]
                            features = result.get("features", {"shape": "积云", "color": "白色", "texture": "蓬松"})
                            
                            return {
                                "name": result.get("name", "神秘云朵"),
                                "description": description,
                                "style": tool,
                                "features": features
                            }
                        except json.JSONDecodeError:
                            pass
                    
                    # 如果JSON解析失败，尝试从文本中提取信息
                    lines = result_text.split('\n')
                    name = "神秘云朵"
                    description = "一朵很有故事的云。"
                    
                    for line in lines:
                        if "name" in line.lower() or "名称" in line:
                            name = line.split(":")[-1].strip().strip('"').strip("'")
                        elif "description" in line.lower() or "描述" in line:
                            description = line.split(":")[-1].strip().strip('"').strip("'")[:30]

                    return {
                        "name": name,
                        "description": description,
                        "style": tool,
                        "features": {"shape": "积云", "color": "白色", "texture": "蓬松"}
                    }
            else:
                raise Exception(f"API调用失败: {response.status_code}")

    except Exception as e:
        print(f"=== 从图像生成云朵名称异常 ===")
        print(f"异常信息: {str(e)}")
        print(f"异常类型: {type(e)}")
        import traceback
        print(f"完整堆栈信息: {traceback.format_exc()}")
        print(f"=== 异常结束 ===")
        
        print(f"从图像生成云朵名称失败: {str(e)}")
        # 降级方案，但无法分析图像，返回通用结果
        fallback_names = {
            "broom": "魔法云朵",
            "hand": "实在云", 
            "catPaw": "软萌云",
            "glassCover": "艺术云"
        }
        
        return {
            "name": fallback_names.get(tool, "神秘云朵"),
            "description": "图像分析暂时不可用，但这依然是一朵很特别的云。",
            "style": tool,
            "features": {"shape": "未知", "color": "未知", "texture": "未知"}
        }

async def generate_cloud_description_from_image(tool: str, image_base64: str, context: CloudContext = None, cloud_name: str = None) -> Dict[str, Any]:
    """直接从图像生成云朵描述"""
    print(f"=== 开始生成云朵描述 ===")
    print(f"工具类型: {tool}")
    print(f"云朵名称: {cloud_name}")
    print(f"图像数据长度: {len(image_base64) if image_base64 else 0}")
    print(f"上下文: {context}")
    
    try:
        tool_description_styles = TOOL_DESCRIPTION_STYLES.get(tool, TOOL_DESCRIPTION_STYLES["hand"])
        print(f"选择的风格: {tool_description_styles['style']}")
        
        if cloud_name:
            # 如果提供了云朵名称，针对名称写描述
            prompt = f"""请观察这张云朵图片，这朵云名为"{cloud_name}"。

请以{tool_description_styles['style']}的风格，为这个名称和图片中的云朵写一句针对性的描述。

{tool_description_styles['description']}

要求：
1. 描述要针对云朵名称"{cloud_name}"，体现其独特个性和故事
2. 描述风格必须符合{tool_description_styles['style']}
3. 描述长度控制在30字以内
4. 可以自由发挥创意，不必严格遵循图像特征
5. 提供3个相关关键词
6. 必须以JSON格式返回

**创作建议**：
- 把图像当作灵感来源，而不是限制条件
- 重点展现云朵名称背后的情感和故事
- 让风格特色成为描述的灵魂

返回格式：
{{
    "description": "针对名称的创意描述（30字以内）",
    "keywords": ["关键词1", "关键词2", "关键词3"]
}}"""
        else:
            # 如果没有名称，直接描述图像
            prompt = f"""请观察这张云朵图片，以{tool_description_styles['style']}的风格写一句描述。

{tool_description_styles['description']}

**拍摄环境**:
- 时间: {context.time if context else '未知'}
- 天气: {context.weather if context and context.weather else '自然天气'}
- 地点: {context.location if context else '未知'}

{f"提示：由于天气信息不可用，请自由发挥创意，重点体现{tool_description_styles['style']}的风格特色。" if context and not context.weather else ""}

要求：
1. 描述要体现{tool_description_styles['style']}的风格特色
2. 描述风格必须符合{tool_description_styles['style']}
3. 描述长度控制在30字以内
4. 可以自由发挥创意，不必严格遵循图像特征
5. 提供3个相关关键词
6. 必须以JSON格式返回结果，不要添加任何描述内容

**创作建议**：
- 把图像当作灵感来源，而不是限制条件
- 重点展现风格特色和创意表达
- 创造有情感、有故事的描述

返回格式：
{{
    "description": "对云朵的创意描述（30字以内）",
    "keywords": ["关键词1", "关键词2", "关键词3"]
}}"""

        print(f"构建的提示词长度: {len(prompt)}")
        print(f"API KEY存在: {bool(CUSTOM_API_KEY)}")
        print(f"API BASE URL: {CUSTOM_API_BASE}")

        # 设置请求头
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {CUSTOM_API_KEY}"
        }
        
        # 设置请求的payload - 使用图像输入
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "temperature": 1.1,
            "top_p": 0.9,
            "frequency_penalty": 0.8,
            "presence_penalty": 0.6,
            "max_tokens": 200
        }

        print(f"开始调用API...")
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"发送POST请求到: {CUSTOM_API_BASE}")
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            print(f"API调用状态码: {response.status_code}")
            print(f"API响应内容: {response.text}")
            
            if response.status_code == 200:
                response_data = response.json()
                result_text = response_data["choices"][0]["message"]["content"].strip()
                print(f"解析得到的文本: {result_text}")
                
                
                try:
                    result = json.loads(result_text)
                    description = result.get("description", "")
                    if len(description) > 30:
                        description = description[:30]
                    
                    print(f"成功解析JSON，描述: {description}")
                    return {
                        "description": description or f"一朵很有意思的云。",
                        "keywords": result.get("keywords", ["云朵", "天空", "自然"])
                    }
                except json.JSONDecodeError as json_error:
                    print(f"直接JSON解析失败: {json_error}")
                    print(f"原始文本: {result_text}")
                    
                    # 尝试提取markdown代码块中的JSON
                    # 匹配 ```json 或 ``` 包围的内容
                    json_pattern = r'```(?:json)?\s*\n?(.*?)\n?```'
                    match = re.search(json_pattern, result_text, re.DOTALL)
                    
                    if match:
                        json_content = match.group(1).strip()
                        print(f"提取到的JSON内容: {json_content}")
                        try:
                            result = json.loads(json_content)
                            description = result.get("description", "")
                            if len(description) > 30:
                                description = description[:30]
                            
                            print(f"成功解析提取的JSON，描述: {description}")
                            return {
                                "description": description or f"一朵很有意思的云。",
                                "keywords": result.get("keywords", ["云朵", "天空", "自然"])
                            }
                        except json.JSONDecodeError as json_error2:
                            print(f"提取的JSON也解析失败: {json_error2}")
                    
                    # 如果都失败了，使用备用方案
                    print("使用备用解析方案")
                    fallback_descriptions = {
                        "broom": "这朵云在施展神秘魔法！",
                        "hand": "这云看起来很有故事。",
                        "catPaw": "这朵云，本喵很满意。",
                        "glassCover": "关于流动的哲学思考。"
                    }
                    
                    return {
                        "description": fallback_descriptions.get(tool, "一朵很特别的云。"),
                        "keywords": ["云朵", "天空", "自然"]
                    }
            else:
                print(f"API调用失败，状态码: {response.status_code}")
                print(f"错误响应: {response.text}")
                raise Exception(f"API调用失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"=== 发生异常 ===")
        print(f"从图像生成云朵描述失败: {str(e)}")
        print(f"异常类型: {type(e)}")
        import traceback
        print(f"完整错误信息: {traceback.format_exc()}")
        print(f"=== 异常结束 ===")
        
        fallback_descriptions = {
            "broom": "图像魔法暂时失效，但这朵云依然很特别！",
            "hand": "看不清图，但肯定是朵有故事的云。",
            "catPaw": "图像模糊，但本喵觉得还行。", 
            "glassCover": "技术故障·临时展品。"
        }
        
        return {
            "description": fallback_descriptions.get(tool, "一朵神秘的云。"),
            "keywords": ["云朵", "天空", "神秘"]
        }

@app.post("/api/cloud/name-from-image-upload", response_model=CloudNameResponse)
async def generate_cloud_name_from_image_upload(
    file: UploadFile = File(..., description="云朵图片文件"),
    tool: str = Form(..., description="捕云工具类型：broom, hand, catPaw, glassCover"),
    time: str = Form(..., description="拍摄时间"),
    location: str = Form(..., description="拍摄地点"),
    weather: Optional[str] = Form(None, description="天气情况")
):
    """从上传的图片文件生成云朵名称（文件上传版本）"""
    try:
        # 读取文件内容
        file_content = await file.read()
        # 转换为base64
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # 构建context
        context = CloudContext(
            time=time,
            weather=weather,
            location=location
        )
        
        # 调用现有的函数
        response = await generate_cloud_name_from_image(tool, image_base64, context)
        return CloudNameResponse(
            name=response["name"],
            description=response["description"],
            style=response["style"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="这朵云正在躲猫猫，AI一时没追上它的脑洞！"
        )

@app.post("/api/cloud/description-from-image-upload", response_model=CloudDescriptionResponse)
async def generate_cloud_description_from_image_upload(
    file: UploadFile = File(..., description="云朵图片文件"),
    tool: str = Form(..., description="捕云工具类型：broom, hand, catPaw, glassCover"),
    time: Optional[str] = Form(None, description="拍摄时间"),
    location: Optional[str] = Form(None, description="拍摄地点"),
    weather: Optional[str] = Form(None, description="天气情况"),
    cloud_name: Optional[str] = Form(None, description="云朵名称（可选）")
):
    """从上传的图片文件生成云朵描述（文件上传版本）"""
    print(f"=== 开始处理图片上传描述请求 ===")
    print(f"文件名: {file.filename}")
    print(f"文件类型: {file.content_type}")
    print(f"工具: {tool}")
    print(f"时间: {time}")
    print(f"地点: {location}")
    print(f"天气: {weather}")
    print(f"云朵名称: {cloud_name}")
    
    try:
        # 读取文件内容
        print("开始读取文件内容...")
        file_content = await file.read()
        print(f"文件大小: {len(file_content)} bytes")
        
        # 转换为base64
        print("转换为base64...")
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        print(f"Base64长度: {len(image_base64)}")
        
        # 构建context
        context = None
        if time or location or weather:
            context = CloudContext(
                time=time or "未知时间",
                weather=weather,
                location=location or "未知地点"
            )
            print(f"构建的上下文: {context}")
        
        # 调用现有的函数
        print("调用描述生成函数...")
        response = await generate_cloud_description_from_image(
            tool, 
            image_base64, 
            context, 
            cloud_name
        )
        print(f"描述生成完成: {response}")
        
        return CloudDescriptionResponse(
            description=response["description"],
            keywords=response["keywords"]
        )
    except Exception as e:
        print(f"=== 文件上传处理异常 ===")
        print(f"异常信息: {str(e)}")
        print(f"异常类型: {type(e)}")
        import traceback
        print(f"完整错误信息: {traceback.format_exc()}")
        print(f"=== 文件上传异常结束 ===")
        
        raise HTTPException(
            status_code=500,
            detail="这团云的故事太深奥了，AI表示需要再想想！"
        )

# ============== 分享图生成 API ==============

class ShareImageRequest(BaseModel):
    image_url: str
    cloud_name: str
    description: str
    tool_icon: str
    captured_at: str
    location: str

class ShareImageResponse(BaseModel):
    share_image_url: str

async def generate_share_image(image_url: str, cloud_name: str, description: str, 
                             tool_icon: str, captured_at: str, location: str) -> str:
    """生成分享图片 - 临时禁用，因为PIL模块未安装"""
    # 临时禁用分享图生成功能
    raise HTTPException(
        status_code=501, 
        detail="分享图生成功能暂时不可用，PIL模块未安装。请稍后再试！"
    )

def get_tool_name(tool_icon: str) -> str:
    """根据工具图标获取工具名称"""
    tool_names = {
        "🧹": "魔法扫帚",
        "✋": "云朵之手", 
        "🐾": "猫咪爪爪",
        "🫙": "玻璃罩"
    }
    return tool_names.get(tool_icon, "神秘工具")

@app.post("/api/share/generate", response_model=ShareImageResponse)
async def generate_share_image_api(request: ShareImageRequest):
    """生成分享图片"""
    try:
        share_image_url = await generate_share_image(
            request.image_url,
            request.cloud_name,
            request.description,
            request.tool_icon,
            request.captured_at,
            request.location
        )
        return ShareImageResponse(share_image_url=share_image_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成分享图失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("=== 启动云彩收集手册 API 服务 ===")
    print(f"Supabase URL: {supabase_url}")
    print(f"API KEY存在: {bool(CUSTOM_API_KEY)}")
    print(f"高德API KEY存在: {bool(os.environ.get('AMAP_API_KEY'))}")
    print("服务启动中...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info"
    )