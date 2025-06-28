"use client"

import type React from "react"

import { useState, useRef, Suspense, useEffect } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Camera, Upload, ArrowLeft, Sparkles, Loader2, Share2, Download } from "lucide-react"
import Image from "next/image"
// 导入API工具函数
import { aiAPI, shareAPI, storageAPI } from "@/utils/api"
import { cloudCollectionAPI, getCurrentLocation } from "@/utils/api"
// 导入摄像头组件
import CameraCapture from "@/components/CameraCapture"

const tools = {
  "magic-broom": {
    name: "水晶球",
    icon: "🔮",
    color: "from-purple-400 to-purple-600",
    bgColor: "bg-purple-50",
    textColor: "text-purple-700",
    apiTool: "broom", // 对应后端API的工具名称
  },
  "gentle-hand": {
    name: "手",
    icon: "✋",
    color: "from-blue-400 to-blue-600",
    bgColor: "bg-blue-50",
    textColor: "text-blue-700",
    apiTool: "hand",
  },
  "cat-paw": {
    name: "猫爪",
    icon: "🐾",
    color: "from-orange-400 to-orange-600",
    bgColor: "bg-orange-50",
    textColor: "text-orange-700",
    apiTool: "catPaw",
  },
  "glass-cover": {
    name: "红笔",
    icon: "✍️",
    color: "from-red-400 to-red-600",
    bgColor: "bg-red-50",
    textColor: "text-red-700",
    apiTool: "glassCover",
  },
}

function CaptureContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const toolId = searchParams.get("tool") as keyof typeof tools
  const tool = tools[toolId]

  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedName, setGeneratedName] = useState<string | null>(null)
  const [generatedDescription, setGeneratedDescription] = useState<string | null>(null)
  const [isGeneratingShare, setIsGeneratingShare] = useState(false)
  const [isSaving, setIsSaving] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isClient, setIsClient] = useState(false)
  // 添加摄像头相关状态
  const [showCamera, setShowCamera] = useState(false)

  useEffect(() => {
    setIsClient(true)
  }, [])

  if (!tool) {
    router.push("/")
    return null
  }

  const handleImageUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      handleFileSelect(file)
    }
  }

  // 统一的文件处理函数
  const handleFileSelect = (file: File) => {
    setSelectedFile(file)
    const reader = new FileReader()
    reader.onload = (e) => {
      setSelectedImage(e.target?.result as string)
    }
    reader.readAsDataURL(file)
  }

  // 处理摄像头拍照
  const handleCameraCapture = (file: File) => {
    handleFileSelect(file)
    setShowCamera(false)
  }

  // 关闭摄像头
  const handleCameraClose = () => {
    setShowCamera(false)
  }

  // 打开摄像头
  const openCamera = () => {
    setShowCamera(true)
  }

  const generateCloudName = async () => {
    if (!selectedFile) return
    
    setIsGenerating(true)
    
    try {
      // 添加文件信息调试
      console.log('=== 开始生成云朵名称 ===');
      console.log('文件信息:', {
        name: selectedFile.name,
        type: selectedFile.type,
        size: selectedFile.size,
        lastModified: selectedFile.lastModified
      });
      console.log('工具信息:', tool.apiTool);
      
      // 使用封装的API函数
      const response = await aiAPI.generateCloudNameFromUpload(
        selectedFile,
        tool.apiTool,
        {
          time: new Date().toISOString(),
          location: '未知地点'
        }
      )
      
      console.log('API响应:', response)
      
      if (response.success && response.data) {
        console.log('API调用成功，处理结果...');
        const result = response.data
        
        // 解析返回的名称和描述
        const fullName = result.name || '神秘云朵'
        const description = result.description || '这是一朵特别的云'
        
        // 如果名称包含｜分隔符，分离名称和描述
        let cloudName = fullName
        let cloudDescription = description
        
        if (fullName.includes('｜')) {
          const parts = fullName.split('｜')
          cloudName = parts[0].trim()
          cloudDescription = parts[1]?.trim() || description
        }
        
        console.log('最终结果:', { cloudName, cloudDescription });
        setGeneratedName(cloudName)
        setGeneratedDescription(cloudDescription)
      } else {
        console.error('API调用失败:', response.error);
        throw new Error(response.error || 'API调用失败')
      }
      
    } catch (error) {
      console.error('生成云朵名称失败:', error)
      console.log('使用降级方案...');
      // 降级到模拟数据
      const names = {
        "magic-broom": ["童年夏日午后云", "蜻蜓追逐梦境云", "扫帚飞行记忆云", "怀旧时光漂浮云"],
        "gentle-hand": ["男人云", "手撕鸡云", "烧烤摊薯条团", "下班瘫云"],
        "cat-paw": ["午睡前第二团云", "云形毛球 No.1", "喵星人专属云", "软萌抓抓云"],
        "glass-cover": ["无声风暴（局部）", "玻璃下的第三种孤独", "未完成作品·2025春", "静物研究 No.7"],
      }

      const descriptions = {
        "magic-broom": [
          "魔法扫帚轻抚过天空，留下了童真的印记",
          "仿佛能听到远方传来的风铃声",
          "这是属于每个人心中的小小魔法师",
          "怀念那个相信魔法的自己",
        ],
        "gentle-hand": ["实实在在的一团云", "手感确实不错", "生活就是这么朴实", "简单粗暴，直接有效"],
        "cat-paw": ["喵～软软的触感", "猫咪视角的天空", "毛茸茸的云朵收藏", "午后慵懒时光的见证"],
        "glass-cover": ["当代艺术的静默表达", "玻璃与云的对话", "策展人眼中的天空切片", "艺术化的自然标本"],
      }

      const toolNames = names[toolId]
      const toolDescriptions = descriptions[toolId]

      const randomName = toolNames[Math.floor(Math.random() * toolNames.length)]
      const randomDescription = toolDescriptions[Math.floor(Math.random() * toolDescriptions.length)]

      console.log('降级结果:', { randomName, randomDescription });
      setGeneratedName(randomName)
      setGeneratedDescription(randomDescription)
    } finally {
      setIsGenerating(false)
      console.log('=== 云朵名称生成结束 ===');
    }
  }

  const generateShareImage = async () => {
    if (!selectedImage || !generatedName || !generatedDescription) return
    
    setIsGeneratingShare(true)
    
    try {
      // 提取位置信息（与保存功能保持一致）
      console.log('分享图片生成：提取位置信息...');
      let locationText = '未知地点';
      
      try {
        if (selectedFile) {
          const exifResult = await storageAPI.extractExif(selectedFile);
          
          if (exifResult.success && exifResult.data) {
            const exifData = exifResult.data;
            console.log('分享图片：EXIF提取结果:', exifData);
            
            // 优先使用EXIF中的位置信息
            if (exifData.has_gps && exifData.gps_info && exifData.location_info?.address) {
              locationText = exifData.location_info.address;
              console.log(`分享图片：使用EXIF位置信息: ${locationText}`);
            } else if (exifData.has_gps && exifData.gps_info) {
              locationText = `GPS: ${exifData.gps_info.latitude.toFixed(6)}, ${exifData.gps_info.longitude.toFixed(6)}`;
              console.log(`分享图片：使用EXIF GPS坐标: ${locationText}`);
            }
          }
        }
      } catch (exifError) {
        console.log('分享图片：EXIF提取失败，将使用默认位置:', exifError);
      }
      
      // 如果没有提取到真实位置信息，使用工具特定的个性化位置
      if (locationText === '未知地点') {
        const toolSpecificLocations = {
          'glassCover': '意念定位中…',
          'hand': '摸鱼时区深处',
          'catPaw': '躲猫猫冠军认证点🐾',
          'broom': '所有可能性的交汇处',
          // 添加可能的其他工具ID映射，确保与collection页面一致
          'crystal-ball': '意念定位中…',
          'cloud-hand': '摸鱼时区深处',
          'cat-paw': '躲猫猫冠军认证点🐾',
          'red-pen': '所有可能性的交汇处'
        };
        
        const toolId = tool.apiTool;
        locationText = toolSpecificLocations[toolId as keyof typeof toolSpecificLocations] || '神秘维度';
        console.log(`分享图片：使用工具特定位置: 工具ID=${toolId}, 位置=${locationText}`);
      }
      
      // 使用封装的API函数
      const response = await shareAPI.generateShareImage({
        image_url: selectedImage, // base64图片数据
        cloud_name: generatedName,
        description: generatedDescription,
        tool_icon: tool.icon,
        captured_at: new Date().toLocaleString('zh-CN'),
        location: locationText
      })
      
      console.log('分享图片生成成功:', response)
      
      if (response.success && response.data) {
        // 下载分享图片
        const link = document.createElement('a')
        link.href = response.data.share_image_url
        link.download = `${generatedName}_分享图.jpg`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        
        alert('分享图片已生成并下载！')
      } else {
        throw new Error(response.error || '分享图片生成失败')
      }
      
    } catch (error) {
      console.error('生成分享图片失败:', error)
      alert('生成分享图片失败，请稍后重试')
    } finally {
      setIsGeneratingShare(false)
    }
  }

  const saveToCollection = async () => {
    if (isSaving) {
      console.log('正在保存中，忽略重复点击');
      return;
    }

    try {
      if (isClient && selectedFile && generatedName && generatedDescription) {
        setIsSaving(true);
        console.log('开始保存云朵到Storage...');
        
        // 首先尝试从图片EXIF中提取位置信息
        console.log('提取图片EXIF信息...');
        let location = { latitude: 0, longitude: 0, address: '未知位置' };
        let captureTime = new Date().toISOString();
        
        try {
          const exifResult = await storageAPI.extractExif(selectedFile);
          
          if (exifResult.success && exifResult.data) {
            const exifData = exifResult.data;
            console.log('EXIF提取结果:', exifData);
            
            // 使用EXIF中的GPS信息
            if (exifData.has_gps && exifData.gps_info) {
              location.latitude = exifData.gps_info.latitude;
              location.longitude = exifData.gps_info.longitude;
              
              // 使用EXIF中的地址信息
              if (exifData.location_info && exifData.location_info.address) {
                location.address = exifData.location_info.address;
                console.log(`使用EXIF位置信息: ${location.address} (${location.latitude}, ${location.longitude})`);
              } else {
                location.address = `GPS: ${location.latitude.toFixed(6)}, ${location.longitude.toFixed(6)}`;
                console.log(`使用EXIF GPS坐标: ${location.address}`);
              }
            }
            
            // 使用EXIF中的拍摄时间
            if (exifData.has_capture_time && exifData.capture_time) {
              captureTime = exifData.capture_time;
              console.log(`使用EXIF拍摄时间: ${captureTime}`);
            }
          }
        } catch (exifError) {
          console.log('EXIF提取失败，将使用当前位置:', exifError);
        }
        
        // 如果EXIF中没有位置信息，尝试获取当前位置
        if (location.latitude === 0 && location.longitude === 0) {
          try {
            console.log('EXIF中无位置信息，获取当前位置...');
            const position = await getCurrentLocation();
            location.latitude = position.latitude;
            location.longitude = position.longitude;
            location.address = '当前位置';
            console.log(`使用当前位置: ${location.latitude}, ${location.longitude}`);
          } catch (locationError) {
            console.log('获取当前位置失败，使用工具特定的默认位置:', locationError);
            
            // 使用工具特定的个性化位置信息
            const toolSpecificLocations = {
              'glassCover': '意念定位中…',
              'hand': '摸鱼时区深处', 
              'catPaw': '躲猫猫冠军认证点🐾',
              'broom': '所有可能性的交汇处',
              // 添加可能的其他工具ID映射，确保与collection页面一致
              'crystal-ball': '意念定位中…',
              'cloud-hand': '摸鱼时区深处',
              'cat-paw': '躲猫猫冠军认证点🐾',
              'red-pen': '所有可能性的交汇处'
            };
            
            const toolId = tool.apiTool;
            location.address = toolSpecificLocations[toolId as keyof typeof toolSpecificLocations] || '神秘维度';
            console.log(`使用工具特定位置: 工具ID=${toolId}, 位置=${location.address}`);
          }
        }
        
        // 上传图片到Supabase Storage
        console.log('上传图片到Storage...');
        const uploadResult = await storageAPI.uploadImage(selectedFile, 'cloud-images', 'original');
        
        if (!uploadResult.success || !uploadResult.data) {
          throw new Error(uploadResult.error || '图片上传失败');
        }

        console.log('图片上传成功:', uploadResult.data.url);

        // 保存到数据库
        const collectionData = {
          tool_id: tool.apiTool,
          latitude: location.latitude,
          longitude: location.longitude,
          address: location.address,
          city: '未知城市',
          country: '未知国家',
          original_image_url: uploadResult.data.url,
          cloud_name: generatedName,
          cloud_description: generatedDescription,
          keywords: [], // 可以从描述中提取关键词
          capture_time: captureTime,
          weather_data: {} // 可以添加天气数据
        };

        console.log('开始保存到数据库...');
        const saveResult = await cloudCollectionAPI.createCloudCollection(collectionData);
        
        if (!saveResult.success) {
          throw new Error(saveResult.error || '保存到数据库失败');
        }

        console.log('云朵保存成功:', saveResult.data);
        router.push("/collection");
      }
    } catch (error) {
      console.error("保存云朵时出错:", error)
      alert(`保存失败: ${error instanceof Error ? error.message : '未知错误'}`)
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-200 via-sky-100 to-white">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="flex items-center gap-4 mb-8">
          <Button variant="ghost" size="icon" onClick={() => router.back()} className="text-sky-600">
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-3">
            <span className="text-2xl">{tool.icon}</span>
            <h1 className="text-2xl font-bold text-sky-800">{tool.name}</h1>
          </div>
        </div>

        <div className="max-w-md mx-auto space-y-6">
          {/* 图片上传区域 */}
          {!selectedImage ? (
            <Card className="p-8 text-center border-2 border-dashed border-sky-300">
              <div className="space-y-4">
                <div className="text-6xl text-sky-300">☁️</div>
                <p className="text-sky-600 mb-6">选择一张云朵照片开始捕云之旅</p>

                <div className="space-y-3">
                  <Button onClick={() => fileInputRef.current?.click()} className="w-full" variant="outline">
                    <Upload className="w-4 h-4 mr-2" />
                    上传图片
                  </Button>

                  <Button
                    onClick={openCamera}
                    className={`w-full bg-gradient-to-r ${tool.color} text-white`}
                  >
                    <Camera className="w-4 h-4 mr-2" />
                    拍摄云朵
                  </Button>
                </div>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageUpload}
                  className="hidden"
                />
              </div>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* 图片预览 */}
              <Card className="p-4">
                <div className="relative aspect-video rounded-lg overflow-hidden">
                  <Image src={selectedImage || "/placeholder.svg"} alt="Selected cloud" fill className="object-cover" />
                </div>
                <div className="mt-4 flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => {
                    setSelectedImage(null)
                    setSelectedFile(null)
                    setGeneratedName(null)
                    setGeneratedDescription(null)
                  }}>
                    重新选择
                  </Button>
                  {!generatedName && (
                    <Button
                      onClick={generateCloudName}
                      disabled={isGenerating}
                      className={`flex-1 bg-gradient-to-r ${tool.color} text-white`}
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          AI正在识别...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4 mr-2" />
                          开始识别
                        </>
                      )}
                    </Button>
                  )}
                </div>
              </Card>

              {/* 生成结果 */}
              <AnimatePresence>
                {generatedName && (
                  <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">
                    <Card className={`p-6 ${tool.bgColor} border-2 ${tool.textColor}`}>
                      <div className="text-center space-y-3">
                        <div className="text-4xl">{tool.icon}</div>
                        <h2 className="text-xl font-bold">捕获了一朵云！</h2>
                        <div className="space-y-3">
                          <h3 className="text-2xl font-bold">{generatedName}</h3>
                          <div className="bg-white/20 rounded-lg p-4">
                            <p className="text-base leading-relaxed opacity-90 whitespace-pre-wrap break-words">
                              {generatedDescription}
                            </p>
                          </div>
                        </div>
                      </div>
                    </Card>

                    <div className="space-y-3">
                      <Button
                        onClick={saveToCollection}
                        disabled={isSaving}
                        className="w-full py-6 text-lg bg-gradient-to-r from-green-400 to-green-600 hover:from-green-500 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isSaving ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            正在保存到我的天空...
                          </>
                        ) : (
                          '保存到我的天空'
                        )}
                      </Button>
                      
                      <Button
                        onClick={generateShareImage}
                        disabled={isGeneratingShare}
                        variant="outline"
                        className="w-full py-4 text-base border-2"
                      >
                        {isGeneratingShare ? (
                          <>
                            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                            正在生成分享图片...
                          </>
                        ) : (
                          <>
                            <Share2 className="w-4 h-4 mr-2" />
                            生成分享图片
                          </>
                        )}
                      </Button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>

      {/* 摄像头组件 */}
      {showCamera && (
        <CameraCapture
          onCapture={handleCameraCapture}
          onClose={handleCameraClose}
        />
      )}
    </div>
  )
}

export default function CapturePage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-b from-sky-200 via-sky-100 to-white flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-sky-600" />
        </div>
      }
    >
      <CaptureContent />
    </Suspense>
  )
}
