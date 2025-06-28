from fastapi import FastAPI, HTTPException, Depends, Header, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timezone
import random
from volcenginesdkarkruntime import Ark
from supabase import create_client, Client
import httpx
import base64
import requests
import re
# from PIL import Image, ImageDraw, ImageFont  # 临时注释掉PIL导入
import urllib3
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from PIL import Image, ImageDraw, ImageFont
import io
import uuid
import asyncio

# 导入JWT认证模块
from auth import get_current_user, get_current_user_id, get_optional_user

# 加载环境变量
load_dotenv()

# 添加EXIF数据处理导入
try:
    from PIL.ExifTags import TAGS, GPSTAGS
    from PIL import Image as PILImage
    EXIF_AVAILABLE = True
    print("✅ EXIF处理库加载成功")
except ImportError:
    EXIF_AVAILABLE = False
    print("⚠️ EXIF处理库未安装，将跳过位置信息提取")

# API基础URL配置 - 支持环境变量切换
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

# 创建 FastAPI 应用
app = FastAPI(title="云彩收集手册 API", version="1.0.0")

# 添加静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============== CORS 配置 ==============
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js 开发服务器
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # 备用端口
        "https://www.cloudcollector.xyz",
        "https://cloudcollector.xyz"  # 生产环境域名（请替换为实际域名）
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============== SSL兼容性修复 ==============
# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 强制跳过SSL验证的猴子补丁
original_request = requests.Session.request
def patched_request(self, method, url, **kwargs):
    kwargs['verify'] = False
    return original_request(self, method, url, **kwargs)
requests.Session.request = patched_request

# 设置环境变量强制跳过SSL验证
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["CURL_CA_BUNDLE"] = ""
os.environ["REQUESTS_CA_BUNDLE"] = ""

# ============== 全局工具风格配置 ==============

# 云朵工具统一风格配置（包含命名和描述）
TOOL_STYLES = {
    "broom": {
        "style": "儿童脑内剧场童话混乱流",
        "naming_description": "你是一位5岁半的云端小巫师，负责给天上的每一朵云取奇怪又可爱的名字。你不会说'放屁的螺旋桨云'、'摔肿屁股的兔云'这样好玩又有画面感的名字。请根据云的颜色、形状、动作（比如在哭、在跑、在放屁、在跳舞、卡住了等）取一个像小孩取的名字，既荒诞又有童趣，最多8个字，听起来就像天上正在发生一场童话事故。",
        "description_prompt": """你是一位5岁半的小魔法师，住在云朵上，每天骑着扫帚巡视天空。你能通过观察云的形状、颜色、移动速度，判断天气是不是要变化（比如要下雨、打雷、起风，或者会有早霞）。但你说话的方式和大人不一样：你不会说'这是积雨云'，你会说'它在天上哭鼻子'或者'它是爆米花云正在放屁'！现在请用你自己的语言，说出这朵云正在干嘛（用孩子的幻想逻辑表达天气变化），再给出一个100%吉利的预言，哄大人开心。还可以附送一个荒诞但简单的互动动作指令，比如'原地跳三下好运就会落在头发上'、'举起钥匙圈对着天空转圈'，让他们感觉真的能召唤好运！请用短短两三句话完成：一句是云在干嘛，一句是它的幸运预言，最后可以加一句搞笑的动作指令。要真诚、童稚、荒诞，好笑但不油腻，温柔但不无聊！""",
        "examples": [
            "漏水的胖河马云｜它用哭哭攒洗脚水泡泡呢！（预言：等会淋到你脖子的那颗，会帮你冲走黏在后背的坏心情！）",
            "狂奔的碎棉花云｜它赶着去给晚霞送请柬！（预言：今天你会被风轻轻推一下，刚好赶上那班有猫咪司机的神奇巴士！）",
            "摔肿屁股的兔云｜看！它哭出的雹子还在呢！（预言：你踩到第3个水坑时，会捡到它落的'哭鼻子冠军'勋章——送你啦！）",
            "膨胀的勇气棉花云｜它吸饱了北风准备发射自己！剧透：你'请假'时吹过的牛，会变成真的气球带你溜达五分钟~",
            "炸毛的乌云爆米花机｜它正把雨滴崩成跳跳糖！预言：没带伞的人会获得瞬移小马达（有效期：跑到屋檐下）！",
            "放屁的螺旋桨云｜它喝风太多在帮天空转电风扇！（预言：你刘海被吹乱的那秒，能闻到它偷藏的西瓜籽味道！）",
            "迷路的螺丝帽云｜它说缺个扳手拧紧彩虹！（急令：快把钥匙圈举高！咧开嘴对着云朵转三圈！转完能换一声'叮当'好运！）"
        ]
    },
    "hand": {
        "style": "生活实诚风格",
        "naming_description": "你是一个特别会碎碎念的生活观察员，说话像朋友聚餐吐槽，带着丧、懒、一点点好笑的自嘲。把云朵比作生活瞬间和情绪。你专门捕捉生活中那些让人秒懂、会心一笑的瞬间，说出大家心声但没说出口的话。说出来的是'社畜共鸣'、'情绪戳中'、'生活真实'、'自嘲金句'、'代表发声'。",
        "description_prompt": "用'躺平哲学'解构成人困境（如拖延/内卷/社交恐惧），引发当代打工人的苦笑共鸣",
        "examples": [
            "泡面等水开的五分钟｜五分钟内干不了任何事，但就是要坐着等",
            "昨天没洗的衣服在天上飘着｜它好像比我还自由",
            "这团云是'不想社交'本人｜已读不回气质MAX",
            "风很努力，云看起来也很卷，我不行｜它们都在拼，我只是活着",
            "'行吧'气质的云｜没意见，但也没兴趣",
            "差点迟到云（已经绝望）｜今天的希望只维持到地铁口",
            "这是我想请假的理由之一｜图里那团发白的就是我的意志力",
            "明明晴天，我却只想请病假｜看天也没动力",
            "我刚刚盯着它发呆三分钟｜比会议有内容",
            "你说它像啥它就像啥｜配合型人格云"
        ]
    },
    "catPaw": {
        "style": "猫主子视角 · 情绪化 + 占有欲 + 内心戏 + 戏精微幻想",
        "naming_description": "你是一只在天台看天的猫主子，只根据云的样子来命名它，但你说话方式很情绪化。你看到的不只是云，而是猫视角里的一个移动的物体\"它像我没睡饱的脸\"、\"没尾巴还学我躺\"。请根据云图特征，为它起个猫主子视角的情绪化名字。不能是正常云名，要像吐槽、占有、控诉或炫耀。",
        "description_prompt": "你是猫主子，刚刚给一朵云命了个名，现在要写一句你内心的评价/命令/幻想。它可以是因为它太像你、惹到你、太软不可信……你看到的是情绪，不是天气。比如\"我要罚它淋自己一小时\"\"我肚子也这样的时候不准惹我\"\"这云不听话，但归我\"",
        "examples": [
            "刚舔完又飞走的云（不许抢）｜这是我的。没签名但你懂的",
            "软得不合理，必须霸占的云｜它今天必须给我躺",
            "我昨天梦到的鱼干其实飞上来了｜味道不错，但你不配知道",
            "没尾巴却想模仿我躺姿的云｜嘲讽 100 分",
            "今天最像我肚皮的那团，喵住｜别动，它是我心情监护人",
            "它没叫我起床，我现在生气｜后果很严重，我要罚它飘两个小时",
            "本喵批准入睡用·云 No.2｜请勿打扰，梦里在铲屎",
            "我舔了一下，它不见了｜这很不负责任，我报警了",
            "太软不可信·不准舔系列｜软得像人类说的话，我信不过",
            "空白（说明：睡着了）｜别打扰我，我脑子在命名另一个宇宙",
            "昨晚梦里它咬我尾巴｜所以今天它必须原地打转直到我开心为止"
        ]
    },
    "glassCover": {
        "style": "文学结构 名作篡改 + 轻学术腔 + 社交病毒基因",
        "naming_description": "你是一位天象文学策展人，专为天上的云命名。你擅长把经典中外文学作品（书名、角色名、金句）进行荒诞篡改，制造出像\"文学平行宇宙天气播报\"一样的标题。请参考以下方式改写：名著结构替换（例：《老人与海》→《社畜与云》），角色错置+情境（例：云娜·卡列尼娜出轨事件），古典混搭（例：李白的酒砸在天上），金句篡改（例：鲁迅：我家门前两朵云），社交传播语感（例：转发此云可获包法利夫人同款幻觉）要求：命名要有文学钩子、荒诞错位感，听起来像某种天气社交预言，不超过15字。",
        "description_prompt": """你是'云文学展'的策展人，为一朵具体的云写展签说明。这句话要结合云的外观特征（如厚重、飘忽、将雨、如羽毛、灰蓝色等），但不能使用科学术语，而要用文学意象、名句错改、角色投射说出这朵云的'情绪+命运+幻想'。请参考以下写法：篡改文学名句（金句变天象：如'天上有诗，但酒味先落地'）、用角色/作者视角解读云（如'本云无法判断是否拥有自由意志'）、文艺腔伪气象报告（如'今日无雨，马孔多仅飘轻微怅惘'）、社交文本型提示（如'仅供转发，不供解释'），要求：内容短句化、有传播钩子、不说教，像高冷文艺号在朋友圈发图配字。""",
        "examples": [
            "《社畜与云》｜离职意向浓度达73%，预计晚高峰将有轻微压抑感",
            "李白的酒砸在天上：盛唐积雨云警报：天上有诗，但酒味先落地了",
            "卡夫卡式焦虑（已扩散至平流层）｜本云无法判断是否拥有自由意志",
            "黛玉葬花未遂｜情绪外包，眼泪云处理中",
            "《百年孤独》降雨预言｜马孔多今日无雨",
            "鲁迅：我家门前两朵云｜一朵是乌云，另一朵也是乌云",
            "云娜·卡列尼娜出轨事件｜本次列车已离轨，预计再婚不顺",
            "转发此云可获包法利夫人同款幻觉｜不负责解释，只供转发",
            "但丁密码：地狱层级试用版｜请按云层厚度解锁适配的沉沦程度",
            "《瓦尔登湖》中的归隐者云｜隐匿在山水之间，风吹草动皆成诗",
            "《等待戈多》的气象版｜什么也没发生，可能明天也不会"
        ]
    }
}

# 为了向后兼容，保留旧的命名配置引用
TOOL_PROMPTS = TOOL_STYLES

# 云朵描述工具风格配置（更新为与命名风格一致）
TOOL_DESCRIPTION_STYLES = {
    "broom": {
        "style": "儿童脑内剧场童话混乱流",
        "description": TOOL_STYLES["broom"]["description_prompt"]
    },
    "hand": {
        "style": "生活实诚风格", 
        "description": TOOL_STYLES["hand"]["description_prompt"]
    },
    "catPaw": {
        "style": "猫主子视角",
        "description": TOOL_STYLES["catPaw"]["description_prompt"]
    },
    "glassCover": {
        "style": "文学结构风格",
        "description": TOOL_STYLES["glassCover"]["description_prompt"]
    }
}

# 初始化火山方舟客户端
client = Ark(api_key=os.environ.get("ARK_API_KEY"))

# 初始化 Supabase 客户端
supabase_url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
supabase_anon_key = os.environ.get("NEXT_PUBLIC_SUPABASE_ANON_KEY")
supabase_service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# 创建Supabase客户端，使用简化配置解决SSL问题
print("正在初始化Supabase客户端...")

# 设置环境变量跳过SSL验证（开发环境）
os.environ["PYTHONHTTPSVERIFY"] = "0"

try:
    # 创建Supabase客户端
    supabase: Client = create_client(supabase_url, supabase_anon_key)
    supabase_admin: Client = create_client(supabase_url, supabase_service_key)
    
    # 测试连接
    print("测试Supabase连接...")
    test_result = supabase_admin.table("capture_tools").select("id").limit(1).execute()
    print(f"✅ Supabase客户端初始化成功，连接正常")
    
except Exception as e:
    print(f"❌ Supabase客户端初始化失败: {str(e)}")
    print("⚠️ 使用Mock数据模式，某些功能可能受限")
    
    # 创建Mock客户端（简单的替代方案）
    class MockSupabaseClient:
        def table(self, table_name):
            return MockTable(table_name)
    
    class MockTable:
        def __init__(self, table_name):
            self.table_name = table_name
            
        def select(self, *args):
            return self
            
        def insert(self, data):
            return self
            
        def update(self, data):
            return self
            
        def delete(self):
            return self
            
        def eq(self, column, value):
            return self
            
        def limit(self, count):
            return self
            
        def order(self, column, **kwargs):
            return self
            
        def range(self, start, end):
            return self
            
        def execute(self):
            # 返回Mock数据
            if self.table_name == "capture_tools":
                return type('MockResult', (), {
                    'data': [
                        {"id": "1", "name": "水晶球", "emoji": "🔮", "description": "儿童魔法风格", "sort_order": 1},
                        {"id": "2", "name": "云朵之手", "emoji": "✋", "description": "生活实诚风格", "sort_order": 2},
                        {"id": "3", "name": "猫咪爪爪", "emoji": "🐾", "description": "猫主子视角", "sort_order": 3},
                        {"id": "4", "name": "红笔", "emoji": "✍️", "description": "文学结构风格", "sort_order": 4}
                    ],
                    'count': 4
                })()
            else:
                return type('MockResult', (), {'data': [], 'count': 0})()
    
    supabase = MockSupabaseClient()
    supabase_admin = MockSupabaseClient()

# ============== 数据库操作辅助函数 ==============

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

class LocationInfo(BaseModel):
    address: str
    city: str
    country: str

class WeatherResponse(BaseModel):
    weather: WeatherData
    location_id: str
    location_info: LocationInfo  # 新增地点信息字段

# ============== Mock 数据生成函数 ==============

async def generate_cloud_name_with_ark(tool: str, features: ImageFeatures, context: CloudContext) -> Dict[str, Any]:
    """使用自定义 OpenAI 风格 API 生成云朵名称"""
    try:
        tool_prompts = TOOL_PROMPTS.get(tool, TOOL_PROMPTS["hand"])

        # 构建示例说明
        examples_text = '\n'.join([f"- {example}" for example in tool_prompts['examples'][:5]])

        prompt = f"""你是云朵命名大师，需要为一朵云起名字并写描述。

**工具类型**: {tool} ({tool_prompts['style']})
**风格要求**: {tool_prompts['naming_description']}

**参考示例**（重要：格式为"名字｜描述"）:
{examples_text}

**关键格式说明**: 
- 上面每个示例都是"名字｜描述"的格式
- ｜是分隔符，左边是云朵名字，右边是对应的描述
- 例如："忧郁棉花糖云｜它说下午三点果酱会偷袭你的袖子！"
  - 名字：忧郁棉花糖云
  - 描述：它说下午三点果酱会偷袭你的袖子！
- 你需要创造一个新的"名字｜描述"组合，风格要与示例保持一致

**云朵特征参考**:
- 形状: {features.shape}
- 颜色: {features.color}  
- 质感: {features.texture}

**拍摄环境**:
- 时间: {context.time}
- 天气: {context.weather if context.weather else '自然天气'}
- 地点: {context.location}

{f"注意：天气信息供参考，若天气信息不可用，请自由发挥创意，重点体现{tool_prompts['style']}的风格特色。" if not context.weather else ""}

请以{tool_prompts['style']}为这朵云生成：
1. 一个富有创意的**名字**（参考示例中｜左边的风格）
2. 一句生动的**描述**（参考示例中｜右边的风格，不超过30字）

**创作要求**：
- 名字和描述要像示例一样配套，形成完整的创意组合
- 名字体现云朵的特色和工具风格特色
- 描述要呼应名字，符合工具的语言风格
- 发挥自己的天才创意来命名，适当结合云朵特征，让图片和生成的文字有关联性
- 必须严格按照{tool_prompts['style']}的风格特色


**输出格式**：
{{
    "name": "云朵名称",
    "description": "生动的描述文字",
    "style": "{tool}"
}}

请务必按照JSON格式返回，不要包含其他文字。"""

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
            "max_tokens": 500  # 增加到500，允许更长的描述
        }

        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                result_text = response_data["choices"][0]["message"]["content"].strip()

                try:
                    result = json.loads(result_text)
                    description = result.get("description", f"一朵{features.shape}的{features.color}云")
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
                            description = line.split(":")[-1].strip().strip('"').strip("'")

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
        "description": description,  # 移除[:30]限制
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
- 生动有趣，充满创意
- 符合{tool_description_styles['style']}风格
- 自由发挥创意，适当结合云朵特征
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
            "max_tokens": 500  # 增加到500，允许更长的描述
        }

        # 调用自定义 OpenAI 风格 API
        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                result_text = response_data["choices"][0]["message"]["content"].strip()
                
                try:
                    result = json.loads(result_text)
                    description = result.get("description", "")
                    # 移除30字符限制，让AI生成的完整描述显示
                    
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
        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
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
        
        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
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
        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
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
    """返回模拟天气数据"""
    return {
        "weather": {
            "main": "Clouds",
            "description": "多云",
            "icon": "02d",
            "temperature": 22.5
        },
        "location_id": "mock_location_123",
        "location_info": {
            "address": "云朵收集地",
            "city": "天空之城",
            "country": "云之国"
        }
    }

# ============== 用户管理 API ==============
# 注意：遗留的设备ID用户管理API已移除，现在使用JWT认证
# 用户管理通过Supabase Auth处理，不需要自定义用户创建端点

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
        
        # 处理位置信息 - 如果是"当前位置"则根据工具显示个性化文案
        location_data = collection["location"]
        if location_data and isinstance(location_data, dict) and "address" in location_data:
            original_location = location_data["address"]
            personalized_location = get_personalized_location_text(collection["tool_id"], original_location)
            # 创建新的位置数据副本，更新地址
            location_data = location_data.copy()
            location_data["address"] = personalized_location
        
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
            "location": location_data,
            "weather": collection["weather"],
            "created_at": collection["created_at"]
        }
        
        return CloudCollectionResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取云朵收藏失败: {str(e)}")

# ============== AI 相关 API ==============

@app.post("/api/cloud/name-from-image", response_model=CloudNameResponse)
async def generate_cloud_name_from_image_api(request: CloudNameImageRequest):
    """从图像生成云朵名称"""
    try:
        result = await generate_cloud_name_from_image(request.tool, request.image, request.context)
        return CloudNameResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成云朵名称失败: {str(e)}")

@app.post("/api/cloud/description-from-image", response_model=CloudDescriptionResponse)
async def generate_cloud_description_from_image_api(request: CloudDescriptionImageRequest):
    """从图像生成云朵描述"""
    try:
        result = await generate_cloud_description_from_image(
            request.tool, 
            request.image, 
            request.context,
            request.cloudName
        )
        return CloudDescriptionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成云朵描述失败: {str(e)}")

@app.post("/api/cloud/name", response_model=CloudNameResponse)
async def generate_cloud_name(request: CloudNameRequest):
    """根据图像特征生成云朵名称"""
    try:
        result = await generate_cloud_name_with_ark(request.tool, request.imageFeatures, request.context)
        return CloudNameResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成云朵名称失败: {str(e)}")

@app.post("/api/cloud/description", response_model=CloudDescriptionResponse)
async def generate_cloud_description(request: CloudDescriptionRequest):
    """根据云朵名称生成描述"""
    try:
        result = await generate_cloud_description_with_ark(request.cloudName, request.imageFeatures, request.tool)
        return CloudDescriptionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成云朵描述失败: {str(e)}")

@app.post("/api/cloud/analyze", response_model=CloudAnalysisResponse)
async def analyze_cloud_image(request: CloudAnalysisRequest):
    """分析云朵图像特征"""
    try:
        result = await analyze_cloud_with_deepseek(request.image, request.options)
        return CloudAnalysisResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析云朵图像失败: {str(e)}")

@app.get("/api/weather/current", response_model=WeatherResponse)
async def get_weather_data(latitude: float, longitude: float, units: str = "metric"):
    """获取当前天气数据"""
    try:
        # 获取天气数据
        weather_data = await get_real_weather_data(latitude, longitude, units)
        
        # 获取位置信息
        location_info = await get_location_info(latitude, longitude)
        
        # 保存位置记录
        location_id = await save_location(
            latitude=latitude,
            longitude=longitude,
            address=location_info.get("address", ""),
            city=location_info.get("city", ""),
            country=location_info.get("country", "")
        )
        
        return WeatherResponse(
            weather=WeatherData(**weather_data["weather"]),
            location_id=location_id,
            location_info=LocationInfo(**location_info)
        )
    except Exception as e:
        print(f"获取天气数据失败: {str(e)}")
        # 返回模拟数据
        mock_data = mock_weather_response()
        return WeatherResponse(**mock_data)

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
            "max_tokens": 500  # 增加到500，允许更长的描述
        }
        
        # 发送POST请求
        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
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

        # 构建示例说明
        examples_text = '\n'.join([f"- {example}" for example in tool_prompts['examples'][:5]])

        prompt = f"""你是云朵命名大师，现在要为一朵云起名字。请仔细观察这张云朵图片，然后以{tool_prompts['style']}为这朵云生成一个富有创意的名字和简短描述。

**工具类型**: {tool} ({tool_prompts['style']})
**风格要求**: {tool_prompts['naming_description']}

**参考示例**（重要：格式为"名字｜描述"）:
{examples_text}

**关键格式说明**: 
- 上面每个示例都是"名字｜描述"的格式
- ｜是分隔符，左边是云朵名字，右边是对应的描述
- 例如："忧郁棉花糖云｜它说下午三点果酱会偷袭你的袖子！"
  - 名字：忧郁棉花糖云
  - 描述：它说下午三点果酱会偷袭你的袖子！
- 你需要创造一个新的"名字｜描述"组合，风格要与示例保持一致

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


**创作要求**：
- 仔细观察图片中云朵的具体形状、颜色、质感和背景
- 结合拍摄环境创造有趣的故事和角色
- 发挥天才想象力，但要基于观察到的视觉特征
- 让风格特色与实际特征相结合，创造有关联性的命名
- 创造有情感、有故事的云朵名称
- 名字和描述要像示例一样配套，形成完整的创意组合
- 名字必须严格符合{tool_prompts['style']}的风格特色，体现创意和个性
- 描述要生动有趣，要呼应名字

**输出格式**：
{{
    "name": "云朵名称",
    "description": "生动的描述文字",
    "style": "{tool}",
    "features": {{
        "shape": "识别到的云朵形状",
        "color": "识别到的云朵颜色",
        "texture": "识别到的云朵质感"
    }}
}}

请务必按照JSON格式返回，不要包含其他文字。"""

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
            "max_tokens": 500  # 增加到500，允许更长的描述
        }

        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
            response = await client.post(CUSTOM_API_BASE, headers=headers, json=payload)
            
            if response.status_code == 200:
                response_data = response.json()
                result_text = response_data["choices"][0]["message"]["content"].strip()
                print(f"API响应内容: {result_text}")

                try:
                    result = json.loads(result_text)
                    description = result.get("description", f"一朵神秘的云")
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
                            description = result.get("description", f"一朵神秘的云")
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
                            description = line.split(":")[-1].strip().strip('"').strip("'")

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
- 生动有趣，充满创意
- 符合{tool_description_styles['style']}风格
- 自由发挥你的天才创意，适当结合云朵特征
- JSON格式返回
- 重点展现云朵名称背后的情感和故事
- 让风格特色成为描述的灵魂


返回格式：
{{
    "description": "针对名称的创意描述",
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
- 生动有趣，充满创意
- 符合{tool_description_styles['style']}风格
- 自由发挥创意，适当结合云朵特征
- JSON格式返回

**创作建议**：
- 把图像当作灵感来源，适当结合实际特征
- 重点展现风格特色和创意表达
- 创造有情感、有故事的描述


返回格式：
{{
    "description": "对云朵的创意描述",
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
            "max_tokens": 500  # 增加到500，允许更长的描述
        }

        print(f"开始调用API...")
        async with httpx.AsyncClient(verify=False, timeout=300.0) as client:
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
                    # 移除30字符限制，让AI生成的完整描述显示
                    
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
                            # 移除30字符限制，让AI生成的完整描述显示
                            
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
    time: Optional[str] = Form(None, description="拍摄时间（可选）"),
    location: Optional[str] = Form(None, description="拍摄地点（可选）"),
    weather: Optional[str] = Form(None, description="天气情况（可选）")
):
    """从上传的图片文件生成云朵名称（仅生成名称，不保存到数据库）"""
    print(f"=== 开始处理图片上传命名请求 ===")
    print(f"文件名: {file.filename}")
    print(f"文件类型: {file.content_type}")
    print(f"文件大小: {file.size if hasattr(file, 'size') else '未知'}")
    print(f"工具: {tool}")
    print(f"时间: {time}")
    print(f"地点: {location}")
    print(f"天气: {weather}")
    
    try:
        # 验证必需参数
        if not file:
            raise HTTPException(status_code=400, detail="缺少图片文件")
        if not tool:
            raise HTTPException(status_code=400, detail="缺少工具参数")
        
        # 验证工具类型
        valid_tools = ["broom", "hand", "catPaw", "glassCover"]
        if tool not in valid_tools:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的工具类型: {tool}，支持的类型: {valid_tools}"
            )
        
        # 验证文件类型
        if file.content_type and not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型: {file.content_type}，请上传图片文件"
            )
        
        print("开始读取文件内容...")
        # 读取文件内容
        file_content = await file.read()
        print(f"文件大小: {len(file_content)} bytes")
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="上传的文件为空")
        
        if len(file_content) > 10 * 1024 * 1024:  # 10MB 限制
            raise HTTPException(status_code=400, detail="文件过大，请上传小于10MB的图片")
        
        print("转换为base64...")
        # 转换为base64
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        print(f"Base64长度: {len(image_base64)}")
        
        print("构建上下文...")
        # 构建context，使用默认值处理可选参数
        context = CloudContext(
            time=time or "未知时间",
            weather=weather,
            location=location or "未知地点"
        )
        print(f"构建的上下文: {context}")
        
        print("调用云朵命名函数...")
        # 调用现有的函数
        response = await generate_cloud_name_from_image(tool, image_base64, context)
        print(f"云朵命名完成:")
        print(f"  名称: {response['name']}")
        print(f"  描述: {response['description']}")
        print(f"  风格: {response['style']}")
        print(f"  完整响应: {response}")
        
        return CloudNameResponse(
            name=response["name"],
            description=response["description"],
            style=response["style"]
        )
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        print(f"=== 文件上传处理异常 ===")
        print(f"异常信息: {str(e)}")
        print(f"异常类型: {type(e)}")
        import traceback
        print(f"完整错误信息: {traceback.format_exc()}")
        print(f"=== 文件上传异常结束 ===")
        
        raise HTTPException(
            status_code=500,
            detail=f"这朵云正在躲猫猫，AI一时没追上它的脑洞！错误详情: {str(e)}"
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
        print(f"描述生成完成:")
        print(f"  描述: {response['description']}")
        print(f"  关键词: {response['keywords']}")
        print(f"  完整响应: {response}")
        
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
    """生成分享图片"""
    try:
        print(f"=== 开始生成分享图片 ===")
        print(f"原图URL: {image_url[:100]}...")  # 只显示前100个字符
        print(f"云朵名称: {cloud_name}")
        print(f"描述: {description}")
        print(f"工具图标: {tool_icon}")
        print(f"拍摄时间: {captured_at}")
        print(f"地点: {location}")
        
        # 下载或处理原图
        original_image = None
        if image_url.startswith('http'):
            print("从HTTP URL加载图片...")
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            original_image = Image.open(io.BytesIO(response.content))
        elif image_url.startswith('data:image'):
            print("从base64数据加载图片...")
            # base64格式: data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD...
            try:
                header, data = image_url.split(',', 1)
                print(f"Base64 header: {header}")
                print(f"Base64 data length: {len(data)}")
                image_data = base64.b64decode(data)
                print(f"Decoded image data length: {len(image_data)}")
                original_image = Image.open(io.BytesIO(image_data))
                print(f"图片加载成功，格式: {original_image.format}, 模式: {original_image.mode}")
            except Exception as e:
                print(f"Base64图片解析失败: {str(e)}")
                # 如果base64解析失败，创建一个默认的占位图片
                original_image = Image.new('RGB', (400, 300), color='lightblue')
                draw_placeholder = ImageDraw.Draw(original_image)
                draw_placeholder.text((150, 140), "云朵图片", fill='white')
        else:
            print("从本地文件路径加载图片...")
            # 本地文件路径
            original_image = Image.open(image_url)
        
        print(f"原图尺寸: {original_image.size}")
        
        # 创建分享图片画布 (正方形，适合社交媒体分享)
        canvas_size = (800, 800)
        canvas = Image.new('RGB', canvas_size, color='white')
        print(f"创建画布: {canvas_size}")
        
        # 调整原图尺寸，保持比例
        original_ratio = original_image.width / original_image.height
        if original_ratio > 1:  # 横图
            new_width = 700
            new_height = int(700 / original_ratio)
        else:  # 竖图或正方形
            new_height = 500
            new_width = int(500 * original_ratio)
        
        # 确保图片不超出画布
        if new_width > 700:
            new_width = 700
            new_height = int(700 / original_ratio)
        if new_height > 500:
            new_height = 500
            new_width = int(500 * original_ratio)
            
        resized_image = original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"调整后图片尺寸: {resized_image.size}")
        
        # 将调整后的图片居中粘贴到画布上
        paste_x = (canvas_size[0] - new_width) // 2
        paste_y = 50  # 从顶部留出空间放标题
        canvas.paste(resized_image, (paste_x, paste_y))
        print(f"图片粘贴位置: ({paste_x}, {paste_y})")
        
        # 创建绘图对象
        draw = ImageDraw.Draw(canvas)
        print("创建绘图对象成功")
        
        # 简化字体加载 - 优先使用支持中文的字体
        print("=== 开始字体加载 ===")
        
        # 首先尝试加载支持中文的系统字体
        title_font = None
        desc_font = None
        info_font = None
        
        # 网站字体配置 - 与前端保持一致
        print("=== 开始字体加载（使用网站字体配置）===")
        
        # 首先尝试加载支持中文的系统字体
        title_font = None
        desc_font = None
        info_font = None
        
        # 字体优先级配置（与网站CSS保持一致）
        website_font_paths = [
            # 1. 项目字体目录中的PF频凡胡涂体
            "fonts/PFanHuTuTi.ttf",
            "fonts/PF频凡胡涂体.ttf", 
            # 2. macOS系统字体（与网站CSS一致）
            "/System/Library/Fonts/PingFang.ttc",  # PingFang SC
            "/System/Library/Fonts/Hiragino Sans GB.ttc",  # Hiragino Sans GB
            "/System/Library/Fonts/STHeiti Medium.ttc",  # Microsoft YaHei 替代
            "/System/Library/Fonts/STHeiti Light.ttc",  # 微软雅黑 替代
            # 3. 系统备用字体
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",  # Arial Unicode
            "/System/Library/Fonts/Helvetica.ttc",  # Helvetica Neue 替代
            "/System/Library/Fonts/Supplemental/Arial.ttf",  # Arial
        ]
        
        font_loaded = False
        loaded_font_name = "未知"
        
        for font_path in website_font_paths:
            try:
                if os.path.exists(font_path):
                    title_font = ImageFont.truetype(font_path, 28)
                    desc_font = ImageFont.truetype(font_path, 18)
                    info_font = ImageFont.truetype(font_path, 14)
                    loaded_font_name = os.path.basename(font_path)
                    print(f"✅ 使用网站字体: {font_path}")
                    print(f"   字体名称: {loaded_font_name}")
                    font_loaded = True
                    break
            except Exception as e:
                print(f"⚠️ 字体 {font_path} 加载失败: {str(e)}")
                continue
        
        # 如果所有字体都加载失败，使用默认字体
        if not font_loaded:
            print("⚠️ 所有网站字体加载失败，使用默认字体")
            try:
                # 最后尝试使用默认字体，但增大字号
                title_font = ImageFont.load_default()
                desc_font = ImageFont.load_default() 
                info_font = ImageFont.load_default()
                loaded_font_name = "系统默认字体"
                print("✅ 使用默认字体")
            except Exception as e:
                print(f"❌ 默认字体也加载失败: {str(e)}")
                # 如果连默认字体都失败，创建None值，后面会处理
                title_font = None
                desc_font = None
                info_font = None
                loaded_font_name = "无字体"
        
        # 绘制标题区域背景
        title_bg_height = 40
        draw.rectangle([0, 0, canvas_size[0], title_bg_height], fill='#f8f9fa')
        print("✅ 标题背景绘制完成")
        
        # 绘制云朵名称（标题）- 使用最简单的方法
        tool_name = get_tool_name(tool_icon)
        title_text = f"{tool_icon} {cloud_name}"
        print(f"准备绘制标题: '{title_text}'")
        
        # 简化标题绘制 - 不计算居中，直接左对齐
        try:
            if title_font:
                draw.text((20, 8), title_text, fill='#2d3748', font=title_font)
            else:
                draw.text((20, 8), title_text, fill='#2d3748')
            print(f"✅ 标题绘制完成")
        except Exception as e:
            print(f"❌ 标题绘制失败: {str(e)}")
            # 最简单的绘制方法
            draw.text((20, 8), title_text, fill='black')
            print("✅ 使用最简单方法重新绘制标题")
        
        # 绘制描述文字（在图片下方）- 简化处理
        desc_y = paste_y + new_height + 20
        print(f"准备绘制描述，起始位置: y={desc_y}")
        
        # 简化描述处理 - 不换行，直接截断
        max_desc_length = 50
        if len(description) > max_desc_length:
            short_description = description[:max_desc_length] + "..."
        else:
            short_description = description
        
        print(f"描述文字: '{short_description}'")
        
        try:
            if desc_font:
                draw.text((20, desc_y), short_description, fill='#4a5568', font=desc_font)
            else:
                draw.text((20, desc_y), short_description, fill='#4a5568')
            print(f"✅ 描述绘制完成")
        except Exception as e:
            print(f"❌ 描述绘制失败: {str(e)}")
            # 最简单的绘制方法
            draw.text((20, desc_y), short_description, fill='black')
            print("✅ 使用最简单方法重新绘制描述")
        
        # 绘制底部信息
        bottom_y = canvas_size[1] - 60
        
        # 绘制底部背景
        draw.rectangle([0, bottom_y, canvas_size[0], canvas_size[1]], fill='#f7fafc')
        print("✅ 底部背景绘制完成")
        
        # 时间和地点信息 - 简化处理
        time_text = f"时间: {captured_at}"
        location_text = f"地点: {location}"
        brand_text = "云彩收集手册"
        
        print(f"准备绘制底部信息:")
        print(f"  时间: '{time_text}'")
        print(f"  地点: '{location_text}'")
        print(f"  品牌: '{brand_text}'")
        
        # 绘制时间
        try:
            if info_font:
                draw.text((20, bottom_y + 10), time_text, fill='#718096', font=info_font)
            else:
                draw.text((20, bottom_y + 10), time_text, fill='#718096')
            print(f"✅ 时间信息绘制完成")
        except Exception as e:
            print(f"❌ 时间信息绘制失败: {str(e)}")
            draw.text((20, bottom_y + 10), time_text, fill='black')
            print("✅ 使用最简单方法重新绘制时间")
        
        # 绘制地点
        try:
            if info_font:
                draw.text((20, bottom_y + 30), location_text, fill='#718096', font=info_font)
            else:
                draw.text((20, bottom_y + 30), location_text, fill='#718096')
            print(f"✅ 地点信息绘制完成")
        except Exception as e:
            print(f"❌ 地点信息绘制失败: {str(e)}")
            draw.text((20, bottom_y + 30), location_text, fill='black')
            print("✅ 使用最简单方法重新绘制地点")
        
        # 绘制品牌标识 - 简化右对齐
        try:
            if info_font:
                draw.text((canvas_size[0] - 120, bottom_y + 20), brand_text, fill='#a0aec0', font=info_font)
            else:
                draw.text((canvas_size[0] - 120, bottom_y + 20), brand_text, fill='#a0aec0')
            print(f"✅ 品牌标识绘制完成")
        except Exception as e:
            print(f"❌ 品牌标识绘制失败: {str(e)}")
            draw.text((canvas_size[0] - 120, bottom_y + 20), brand_text, fill='gray')
            print("✅ 使用最简单方法重新绘制品牌")
        
        # 添加字体信息显示（用于调试）
        font_debug_text = f"字体: {loaded_font_name}"
        try:
            if info_font:
                # 计算文字宽度以右对齐
                bbox = draw.textbbox((0, 0), font_debug_text, font=info_font)
                text_width = bbox[2] - bbox[0]
                draw.text((canvas_size[0] - text_width - 10, bottom_y + 40), 
                         font_debug_text, fill='#e2e8f0', font=info_font)
            else:
                draw.text((canvas_size[0] - 150, bottom_y + 40), 
                         font_debug_text, fill='#e2e8f0')
            print(f"✅ 字体信息显示完成: '{font_debug_text}'")
        except Exception as e:
            print(f"⚠️ 字体信息显示失败: {str(e)}")
            # 不影响主要功能，忽略错误
        
        # 保存图片
        output_filename = f"share_{uuid.uuid4().hex[:8]}.jpg"
        output_path = f"static/shares/{output_filename}"
        
        # 确保目录存在
        os.makedirs("static/shares", exist_ok=True)
        
        # 保存图片
        canvas.save(output_path, 'JPEG', quality=90)
        
        print(f"✅ 分享图片已保存: {output_path}")
        
        # 返回可访问的URL
        share_url = f"{API_BASE_URL}/{output_path}"
        print(f"✅ 分享图片URL: {share_url}")
        return share_url
        
    except Exception as e:
        print(f"❌ 生成分享图片失败: {str(e)}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"生成分享图片失败: {str(e)}")

def get_tool_name(tool_icon: str) -> str:
    """根据工具图标获取工具名称"""
    tool_names = {
        "🔮": "水晶球",
        "✋": "手", 
        "🐾": "猫爪",
        "✍️": "红笔",
        "✏️": "红笔",  # 保持兼容性
        "🫙": "红笔",  # 保持兼容性
        "🧊": "红笔"  # 备用图标
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

# ============== Storage 相关 API ==============

@app.post("/api/v2/storage/extract-exif", response_model=dict)
async def extract_image_exif_v2(
    file: UploadFile = File(..., description="要分析的图片文件"),
    current_user: dict = Depends(get_current_user)
):
    """提取图片的EXIF信息，包括GPS坐标和拍摄时间"""
    try:
        # 验证文件类型
        if file.content_type and not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型: {file.content_type}，请上传图片文件"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="上传的文件为空")
        
        print(f"开始提取EXIF信息，文件大小: {len(file_content)} bytes")
        
        # 提取GPS信息
        gps_info = extract_gps_from_exif(file_content)
        
        # 提取拍摄时间
        capture_time = extract_exif_datetime(file_content)
        
        # 如果有GPS信息，获取地址信息
        location_info = {}
        if gps_info and 'latitude' in gps_info and 'longitude' in gps_info:
            try:
                location_data = await get_location_info(gps_info['latitude'], gps_info['longitude'])
                location_info = {
                    'address': location_data.get('address', ''),
                    'city': location_data.get('city', ''),
                    'country': location_data.get('country', ''),
                    'source': 'exif'
                }
                print(f"从GPS坐标获取到地址: {location_info['address']}")
            except Exception as e:
                print(f"获取地址信息失败: {str(e)}")
                location_info = {
                    'address': f"GPS: {gps_info['latitude']:.6f}, {gps_info['longitude']:.6f}",
                    'city': '',
                    'country': '',
                    'source': 'exif'
                }
        
        result = {
            'has_gps': bool(gps_info),
            'gps_info': gps_info,
            'location_info': location_info,
            'capture_time': capture_time,
            'has_capture_time': bool(capture_time)
        }
        
        print(f"EXIF提取结果: {result}")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"提取EXIF信息异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"提取EXIF信息失败: {str(e)}"
        )

@app.post("/api/v2/storage/upload-image", response_model=dict)
async def upload_image_to_storage_v2(
    file: UploadFile = File(..., description="要上传的图片文件"),
    bucket: str = Form("cloud-images", description="存储桶名称"),
    folder: str = Form("original", description="文件夹名称"),
    current_user: dict = Depends(get_current_user)
):
    """上传图片到Supabase Storage"""
    try:
        # 验证文件类型
        if file.content_type and not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型: {file.content_type}，请上传图片文件"
            )
        
        # 读取文件内容
        file_content = await file.read()
        
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="上传的文件为空")
        
        if len(file_content) > 10 * 1024 * 1024:  # 10MB 限制
            raise HTTPException(status_code=400, detail="文件过大，请上传小于10MB的图片")
        
        # 提取EXIF信息（在上传的同时）
        gps_info = extract_gps_from_exif(file_content)
        capture_time = extract_exif_datetime(file_content)
        
        # 生成唯一文件名
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        # 使用 timezone.utc 替代 datetime.UTC 以兼容更多Python版本
        file_name = f"{int(datetime.now(timezone.utc).timestamp() * 1000)}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        # 构建文件路径：folder/year/month/filename
        now = datetime.now(timezone.utc)
        year = now.year
        month = f"{now.month:02d}"
        file_path = f"{folder}/{year}/{month}/{file_name}"
        
        print(f"开始上传文件到 {bucket}/{file_path}")
        
        # 上传到Supabase Storage
        try:
            result = supabase_admin.storage.from_(bucket).upload(
                file_path, 
                file_content,
                {
                    "content-type": file.content_type or "image/jpeg",
                    "cache-control": "3600"
                }
            )
            
            if hasattr(result, 'error') and result.error:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Storage上传失败: {result.error.message}"
                )
            
        except Exception as storage_error:
            print(f"Storage上传错误: {str(storage_error)}")
            raise HTTPException(
                status_code=500, 
                detail=f"图片上传失败: {str(storage_error)}"
            )
        
        # 获取公共URL
        try:
            public_url = supabase_admin.storage.from_(bucket).get_public_url(file_path)
            
            # 如果返回的不是字符串或为空，使用备用方案
            if not isinstance(public_url, str) or not public_url:
                # 备用方案：手动构建URL
                public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{file_path}"
            
        except Exception as url_error:
            print(f"获取公共URL错误: {str(url_error)}")
            # 备用方案：手动构建URL
            public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{file_path}"
        
        print(f"图片上传成功: {public_url}")
        
        # 返回上传结果和EXIF信息
        return {
            "url": public_url,
            "path": file_path,
            "bucket": bucket,
            "size": len(file_content),
            "content_type": file.content_type,
            "exif_info": {
                "has_gps": bool(gps_info),
                "gps_info": gps_info,
                "capture_time": capture_time,
                "has_capture_time": bool(capture_time)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"上传图片异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"图片上传失败: {str(e)}"
        )

@app.delete("/api/v2/storage/delete-image")
async def delete_image_from_storage_v2(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """从Supabase Storage删除图片"""
    try:
        file_path = request.get("filePath")
        bucket = request.get("bucket", "cloud-images")
        
        if not file_path:
            raise HTTPException(status_code=400, detail="缺少文件路径参数")
        
        # 从Storage删除文件
        try:
            result = supabase_admin.storage.from_(bucket).remove([file_path])
            
            if hasattr(result, 'error') and result.error:
                raise HTTPException(
                    status_code=500, 
                    detail=f"删除失败: {result.error.message}"
                )
            
        except Exception as storage_error:
            print(f"Storage删除错误: {str(storage_error)}")
            raise HTTPException(
                status_code=500, 
                detail=f"图片删除失败: {str(storage_error)}"
            )
        
        return {"message": "图片删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"删除图片异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"图片删除失败: {str(e)}"
        )

@app.post("/api/v2/storage/public-url")
async def get_public_url_v2(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """获取图片的公共URL"""
    try:
        file_path = request.get("filePath")
        bucket = request.get("bucket", "cloud-images")
        
        if not file_path:
            raise HTTPException(status_code=400, detail="缺少文件路径参数")
        
        # 获取公共URL
        try:
            public_url = supabase_admin.storage.from_(bucket).get_public_url(file_path)
            
            # 如果返回的不是字符串或为空，使用备用方案
            if not isinstance(public_url, str) or not public_url:
                # 备用方案：手动构建URL
                public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{file_path}"
            
        except Exception as url_error:
            print(f"获取公共URL错误: {str(url_error)}")
            # 备用方案：手动构建URL
            public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{file_path}"
        
        return {"url": public_url}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"获取公共URL异常: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取公共URL失败: {str(e)}"
        )

# ============== 工具函数 ==============

def extract_gps_from_exif(image_bytes: bytes) -> dict:
    """从图片EXIF数据中提取GPS信息"""
    if not EXIF_AVAILABLE:
        return {}
    
    try:
        # 从字节数据创建PIL图像
        image = PILImage.open(io.BytesIO(image_bytes))
        
        # 获取EXIF数据
        exif_data = image._getexif()
        if not exif_data:
            print("图片没有EXIF数据")
            return {}
        
        # 查找GPS信息
        gps_info = {}
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name == 'GPSInfo':
                for gps_tag, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag, gps_tag)
                    gps_info[gps_tag_name] = gps_value
                break
        
        if not gps_info:
            print("图片EXIF中没有GPS信息")
            return {}
        
        # 转换GPS坐标
        latitude = convert_gps_coordinate(gps_info.get('GPSLatitude'), gps_info.get('GPSLatitudeRef'))
        longitude = convert_gps_coordinate(gps_info.get('GPSLongitude'), gps_info.get('GPSLongitudeRef'))
        
        if latitude is not None and longitude is not None:
            print(f"从EXIF提取到GPS坐标: {latitude}, {longitude}")
            return {
                'latitude': latitude,
                'longitude': longitude,
                'source': 'exif'
            }
        else:
            print("GPS坐标转换失败")
            return {}
            
    except Exception as e:
        print(f"提取EXIF GPS信息失败: {str(e)}")
        return {}

def convert_gps_coordinate(coord, ref):
    """将GPS坐标从度分秒格式转换为十进制度"""
    if not coord or not ref:
        return None
    
    try:
        # coord格式通常是 [(度, 分母), (分, 分母), (秒, 分母)]
        degrees = float(coord[0][0]) / float(coord[0][1])
        minutes = float(coord[1][0]) / float(coord[1][1]) / 60.0
        seconds = float(coord[2][0]) / float(coord[2][1]) / 3600.0
        
        decimal_coord = degrees + minutes + seconds
        
        # 根据参考方向调整正负号
        if ref in ['S', 'W']:
            decimal_coord = -decimal_coord
            
        return decimal_coord
    except (IndexError, ValueError, ZeroDivisionError) as e:
        print(f"GPS坐标转换错误: {str(e)}")
        return None

def extract_exif_datetime(image_bytes: bytes) -> str:
    """从图片EXIF数据中提取拍摄时间"""
    if not EXIF_AVAILABLE:
        return ""
    
    try:
        image = PILImage.open(io.BytesIO(image_bytes))
        exif_data = image._getexif()
        
        if not exif_data:
            return ""
        
        # 查找拍摄时间
        for tag, value in exif_data.items():
            tag_name = TAGS.get(tag, tag)
            if tag_name in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                try:
                    # EXIF时间格式: "YYYY:MM:DD HH:MM:SS"
                    datetime_str = str(value)
                    # 转换为ISO格式
                    dt = datetime.strptime(datetime_str, "%Y:%m:%d %H:%M:%S")
                    return dt.isoformat() + "Z"
                except ValueError:
                    continue
        
        return ""
    except Exception as e:
        print(f"提取EXIF时间失败: {str(e)}")
        return ""

# ============== JWT认证测试路由 ==============

@app.get("/api/auth/test")
async def test_auth_endpoint(current_user: dict = Depends(get_current_user)):
    """
    JWT认证测试端点
    
    这个端点用于测试JWT认证是否正常工作
    需要在请求头中包含有效的Bearer Token
    
    Returns:
        dict: 包含当前用户信息的响应
    """
    return {
        "message": "认证成功！",
        "user_id": current_user["sub"],
        "email": current_user.get("email"),
        "token_info": {
            "issued_at": current_user.get("iat"),
            "expires_at": current_user.get("exp"),
        }
    }

@app.get("/api/auth/profile")
async def get_user_profile(current_user: dict = Depends(get_current_user)):
    """
    获取当前用户档案信息
    
    需要JWT认证
    """
    return {
        "user_id": current_user["sub"],
        "email": current_user.get("email"),
        "user_metadata": current_user.get("user_metadata", {}),
        "app_metadata": current_user.get("app_metadata", {}),
        "created_at": current_user.get("iat"),
    }

# ============== JWT认证版本的云朵收藏API ==============

@app.post("/api/v2/cloud-collections", response_model=CloudCollectionResponse)
async def create_cloud_collection(
    request: CloudCollectionCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    创建云朵收藏 (JWT认证版本)
    
    使用JWT Token认证的新版本API
    用户ID直接从JWT Token中获取，更安全可靠
    """
    try:
        # 从JWT Token中获取用户ID
        user_id = current_user["sub"]
        
        # 保存地点信息
        location_id = await save_location(
            latitude=request.latitude,
            longitude=request.longitude,
            address=request.address,
            city=request.city,
            country=request.country
        )
        
        # 保存天气信息
        weather_id = None
        if request.weather_data:
            weather_id = await save_weather_record(location_id, request.weather_data)
        
        # 创建云朵收藏记录
        collection_data = {
            "user_id": current_user["sub"],  # 使用JWT中的用户ID
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

@app.get("/api/v2/my-collections", response_model=CloudCollectionListResponse)
async def get_my_cloud_collections(
    current_user: dict = Depends(get_current_user),
    page: int = 1,
    page_size: int = 20,
    tool_id: Optional[str] = None,
    is_favorite: Optional[bool] = None
):
    """
    获取当前用户的云朵收藏列表 (JWT认证版本)
    
    自动从JWT Token中获取用户ID，无需在URL中传递
    """
    try:
        user_id = current_user["sub"]
        print(current_user)

        print(f'user_id: {user_id}')
        
        # 构建查询条件
        query = supabase_admin.table("cloud_collections").select("""
            *,
            tool:capture_tools(name, emoji),
            location:locations(*),
            weather:weather_records(*)
        """, count="exact").eq("user_id", current_user["sub"])
        
        # 添加筛选条件
        if tool_id:
            query = query.eq("tool_id", tool_id)
        if is_favorite is not None:
            query = query.eq("is_favorite", is_favorite)
        
        # 分页和排序
        offset = (page - 1) * page_size
        result = query.order("capture_time", desc=True).range(offset, offset + page_size - 1).execute()
        
        print(result)

        # 构建响应数据
        collections = []
        for collection in result.data:
            # 处理位置信息 - 如果是"当前位置"则根据工具显示个性化文案
            location_data = collection["location"]
            if location_data and isinstance(location_data, dict) and "address" in location_data:
                original_location = location_data["address"]
                personalized_location = get_personalized_location_text(collection["tool_id"], original_location)
                # 创建新的位置数据副本，更新地址
                location_data = location_data.copy()
                location_data["address"] = personalized_location
            
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
                "location": location_data,
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

@app.patch("/api/v2/cloud-collections/{collection_id}/favorite")
async def toggle_cloud_collection_favorite(
    collection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    切换云朵收藏的收藏状态 (JWT认证版本)
    """
    try:
        user_id = current_user["sub"]
        
        # 检查收藏记录是否属于当前用户
        result = supabase_admin.table("cloud_collections").select("is_favorite").eq(
            "id", collection_id
        ).eq("user_id", current_user["sub"]).execute()
        
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

@app.delete("/api/v2/cloud-collections/{collection_id}")
async def delete_cloud_collection(
    collection_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    删除云朵收藏 (JWT认证版本)
    """
    try:
        user_id = current_user["sub"]
        
        # 检查收藏记录是否属于当前用户
        result = supabase_admin.table("cloud_collections").select("id").eq(
            "id", collection_id
        ).eq("user_id", current_user["sub"]).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="云朵收藏不存在或无权限")
        
        # 删除收藏记录
        supabase_admin.table("cloud_collections").delete().eq("id", collection_id).execute()
        
        return {"message": "删除成功"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除云朵收藏失败: {str(e)}")

# ============== 原有的云朵收藏API（保持向后兼容）==============

@app.post("/api/v2/cloud/create-from-image-upload", response_model=CloudCollectionResponse)
async def create_cloud_collection_from_image_upload(
    file: UploadFile = File(..., description="云朵图片文件"),
    tool: str = Form(..., description="捕云工具类型：broom, hand, catPaw, glassCover"),
    time: Optional[str] = Form(None, description="拍摄时间（可选）"),
    location: Optional[str] = Form(None, description="拍摄地点（可选）"),
    weather: Optional[str] = Form(None, description="天气情况（可选）"),
    latitude: Optional[float] = Form(None, description="纬度（可选）"),
    longitude: Optional[float] = Form(None, description="经度（可选）"),
    current_user: dict = Depends(get_current_user)
):
    """从上传的图片文件创建完整的云朵收藏记录"""
    print(f"=== 开始处理图片上传并创建云朵收藏 ===")
    print(f"文件名: {file.filename}")
    print(f"文件类型: {file.content_type}")
    print(f"工具: {tool}")
    print(f"坐标: {latitude}, {longitude}")
    
    try:
        # 验证必需参数
        if not file:
            raise HTTPException(status_code=400, detail="缺少图片文件")
        if not tool:
            raise HTTPException(status_code=400, detail="缺少工具参数")
        
        # 验证工具类型
        valid_tools = ["broom", "hand", "catPaw", "glassCover"]
        if tool not in valid_tools:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的工具类型: {tool}，支持的类型: {valid_tools}"
            )
        
        # 验证文件类型
        if file.content_type and not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型: {file.content_type}，请上传图片文件"
            )
        
        # 读取文件内容
        file_content = await file.read()
        if len(file_content) == 0:
            raise HTTPException(status_code=400, detail="上传的文件为空")
        if len(file_content) > 10 * 1024 * 1024:  # 10MB 限制
            raise HTTPException(status_code=400, detail="文件过大，请上传小于10MB的图片")
        
        # 第一步：上传图片到存储
        print("上传图片到存储...")
        file_ext = file.filename.split('.')[-1] if '.' in file.filename else 'jpg'
        file_name = f"{int(datetime.now(timezone.utc).timestamp() * 1000)}_{uuid.uuid4().hex[:8]}.{file_ext}"
        
        now = datetime.now(timezone.utc)
        year = now.year
        month = f"{now.month:02d}"
        file_path = f"original/{year}/{month}/{file_name}"
        
        # 上传到Supabase Storage
        try:
            result = supabase_admin.storage.from_("cloud-images").upload(
                file_path, 
                file_content,
                {
                    "content-type": file.content_type or "image/jpeg",
                    "cache-control": "3600"
                }
            )
            
            if hasattr(result, 'error') and result.error:
                raise HTTPException(
                    status_code=500, 
                    detail=f"Storage上传失败: {result.error.message}"
                )
            
        except Exception as storage_error:
            print(f"Storage上传错误: {str(storage_error)}")
            raise HTTPException(
                status_code=500, 
                detail=f"图片上传失败: {str(storage_error)}"
            )
        
        # 获取公共URL
            public_url = supabase_admin.storage.from_("cloud-images").get_public_url(file_path)
            
            # 如果返回的不是字符串或为空，使用备用方案
            if not isinstance(public_url, str) or not public_url:            public_url = public_url_result.get('publicURL') or public_url_result.get('publicUrl')
            
            if not public_url:
                # 备用方案：手动构建URL
                public_url = f"{supabase_url}/storage/v1/object/public/cloud-images/{file_path}"
            
        except Exception as url_error:
            print(f"获取公共URL错误: {str(url_error)}")
            # 备用方案：手动构建URL
            public_url = f"{supabase_url}/storage/v1/object/public/cloud-images/{file_path}"
        
        print(f"图片上传成功: {public_url}")
        
        # 第二步：提取EXIF信息
        print("提取EXIF信息...")
        gps_info = extract_gps_from_exif(file_content)
        capture_time_from_exif = extract_exif_datetime(file_content)
        
        # 优先使用EXIF中的GPS信息，其次使用传入的坐标
        final_latitude = latitude
        final_longitude = longitude
        
        if gps_info and gps_info.get('latitude') and gps_info.get('longitude'):
            final_latitude = gps_info['latitude']
            final_longitude = gps_info['longitude']
            print(f"使用EXIF GPS信息: {final_latitude}, {final_longitude}")
        elif latitude and longitude:
            print(f"使用传入的GPS信息: {final_latitude}, {final_longitude}")
        else:
            # 默认坐标（如果都没有）
            final_latitude = 39.9042  # 北京天安门
            final_longitude = 116.4074
            print(f"使用默认GPS信息: {final_latitude}, {final_longitude}")
        
        # 优先使用EXIF中的时间，其次使用传入的时间
        final_capture_time = time
        if capture_time_from_exif:
            final_capture_time = capture_time_from_exif
            print(f"使用EXIF时间信息: {final_capture_time}")
        elif time:
            print(f"使用传入的时间信息: {final_capture_time}")
        else:
            # 使用当前时间
            final_capture_time = datetime.now(timezone.utc).isoformat()
            print(f"使用当前时间: {final_capture_time}")
        
        # 第三步：生成云朵名称和描述
        print("转换为base64...")
        image_base64 = base64.b64encode(file_content).decode('utf-8')
        print(f"Base64长度: {len(image_base64)}")
        
        print("构建上下文...")
        context = CloudContext(
            time=final_capture_time or "未知时间",
            weather=weather,
            location=location or "未知地点"
        )
        print(f"构建的上下文: {context}")
        
        print("调用云朵命名函数...")
        name_response = await generate_cloud_name_from_image(tool, image_base64, context)
        print(f"云朵命名完成: {name_response['name']}")
        
        # 第四步：生成更详细的描述和关键词
        print("生成详细描述...")
        description_response = await generate_cloud_description_from_image(
            tool, 
            image_base64, 
            context, 
            name_response['name']
        )
        print(f"详细描述生成完成: {description_response['description']}")
        
        # 第五步：获取位置和天气信息
        print("获取位置和天气信息...")
        
        # 获取位置信息
        location_info = None
        if final_latitude and final_longitude:
            try:
                location_info = await get_location_info(final_latitude, final_longitude)
                print(f"位置信息: {location_info}")
            except Exception as e:
                print(f"获取位置信息失败: {str(e)}")
        
        # 获取天气信息
        weather_info = None
        if final_latitude and final_longitude:
            try:
                weather_response = await get_real_weather_data(final_latitude, final_longitude)
                weather_info = weather_response
                print(f"天气信息: {weather_info}")
            except Exception as e:
                print(f"获取天气信息失败: {str(e)}")
        
        # 第六步：获取或创建用户
        print("获取或创建用户...")
        user = await get_or_create_user(device_id=device_id, user_id=user_id)
        print(f"用户信息: {user['id']}")
        
        # 第七步：保存位置信息
        print("保存位置信息...")
        location_id = await save_location(
            latitude=final_latitude,
            longitude=final_longitude,
            address=location_info.get('address') if location_info else location,
            city=location_info.get('city') if location_info else None,
            country=location_info.get('country') if location_info else None
        )
        print(f"位置ID: {location_id}")
        
        # 第八步：保存天气记录
        weather_id = None
        if weather_info:
            print("保存天气记录...")
            weather_id = await save_weather_record(location_id, weather_info)
            print(f"天气ID: {weather_id}")
        
        # 第九步：获取工具ID
        print("获取工具信息...")
        tools_result = supabase_admin.table("capture_tools").select("id").eq("name", tool).execute()
        tool_id = None
        if tools_result.data:
            tool_id = tools_result.data[0]["id"]
        else:
            # 如果工具不存在，创建一个默认的
            tool_mapping = {
                "broom": "扫把",
                "hand": "手掌", 
                "catPaw": "猫爪",
                "glassCover": "玻璃罩"
            }
            tool_name = tool_mapping.get(tool, tool)
            create_result = supabase_admin.table("capture_tools").insert({
                "name": tool,
                "display_name": tool_name,
                "emoji": "☁️",
                "description": f"{tool_name}捕云工具",
                "sort_order": 1
            }).execute()
            tool_id = create_result.data[0]["id"]
        
        print(f"工具ID: {tool_id}")
        
        # 第十步：创建云朵收藏记录
        print("创建云朵收藏记录...")
        collection_data = {
            "user_id": user["id"],
            "tool_id": tool_id,
            "location_id": location_id,
            "weather_id": weather_id,
            "original_image_url": public_url,
            "cropped_image_url": None,
            "thumbnail_url": None,
            "cloud_name": name_response['name'],
            "cloud_description": description_response['description'],
            "keywords": description_response['keywords'] or [],
            "image_features": name_response.get('features', {}),
            "capture_time": final_capture_time,
            "view_count": 0
        }
        
        result = supabase_admin.table("cloud_collections").insert(collection_data).execute()
        collection_id = result.data[0]["id"]
        print(f"云朵收藏记录创建成功，ID: {collection_id}")
        
        # 第十一步：获取完整的收藏记录并返回
        print("获取完整收藏记录...")
        return await get_cloud_collection_detail(collection_id)
        
    except HTTPException:
        # 重新抛出 HTTP 异常
        raise
    except Exception as e:
        print(f"=== 创建云朵收藏异常 ===")
        print(f"异常信息: {str(e)}")
        print(f"异常类型: {type(e)}")
        import traceback
        print(f"完整错误信息: {traceback.format_exc()}")
        print(f"=== 创建云朵收藏异常结束 ===")
        
        raise HTTPException(
            status_code=500,
            detail=f"创建云朵收藏失败: {str(e)}"
        )

@app.get("/api/v2/users/my-collections", response_model=CloudCollectionListResponse)
async def get_user_cloud_collections(
    current_user: dict = Depends(get_current_user),
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
        """, count="exact").eq("user_id", current_user["sub"])
        
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
            # 处理位置信息 - 如果是"当前位置"则根据工具显示个性化文案
            location_data = collection["location"]
            if location_data and isinstance(location_data, dict) and "address" in location_data:
                original_location = location_data["address"]
                personalized_location = get_personalized_location_text(collection["tool_id"], original_location)
                # 创建新的位置数据副本，更新地址
                location_data = location_data.copy()
                location_data["address"] = personalized_location
            
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
                "location": location_data,
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

# ============== 工具相关辅助函数 ==============

def get_personalized_location_text(tool_id: str, location_text: str) -> str:
    """
    根据工具类型和位置文本返回个性化的位置描述
    
    Args:
        tool_id: 工具ID (glassCover, hand, catPaw, broom)
        location_text: 原始位置文本
    
    Returns:
        个性化的位置描述文本
    """
    # 如果位置不是"当前位置"，直接返回原文本
    if location_text != "当前位置":
        return location_text
    
    # 根据不同工具返回个性化文案
    tool_location_map = {
        "glassCover": "意念定位中…",          # 水晶球工具
        "hand": "摸鱼时区深处",               # 手工具
        "catPaw": "躲猫猫冠军认证点🐾",        # 猫爪工具
        "broom": "所有可能性的交汇处"          # 红笔工具
    }
    
    return tool_location_map.get(tool_id, location_text)

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