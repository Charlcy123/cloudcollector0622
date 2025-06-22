"use client"

import type React from "react"

import { useState, useRef, Suspense, useEffect } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Camera, Upload, ArrowLeft, Sparkles, Loader2 } from "lucide-react"
import Image from "next/image"

const tools = {
  "magic-broom": {
    name: "扫帚",
    icon: "🧹",
    color: "from-purple-400 to-purple-600",
    bgColor: "bg-purple-50",
    textColor: "text-purple-700",
  },
  "gentle-hand": {
    name: "手",
    icon: "✋",
    color: "from-pink-400 to-pink-600",
    bgColor: "bg-pink-50",
    textColor: "text-pink-700",
  },
  "cat-paw": {
    name: "猫爪",
    icon: "🐾",
    color: "from-orange-400 to-orange-600",
    bgColor: "bg-orange-50",
    textColor: "text-orange-700",
  },
  collector: {
    name: "玻璃罩",
    icon: "🧊",
    color: "from-cyan-400 to-cyan-600",
    bgColor: "bg-cyan-50",
    textColor: "text-cyan-700",
  },
}

function CaptureContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const toolId = searchParams.get("tool") as keyof typeof tools
  const tool = tools[toolId]

  const [selectedImage, setSelectedImage] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedName, setGeneratedName] = useState<string | null>(null)
  const [generatedDescription, setGeneratedDescription] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [isClient, setIsClient] = useState(false)

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
      const reader = new FileReader()
      reader.onload = (e) => {
        setSelectedImage(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const generateCloudName = async () => {
    setIsGenerating(true)

    // 模拟AI生成过程
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // 根据工具类型生成不同风格的名称
    const names = {
      "magic-broom": ["童年夏日午后云", "蜻蜓追逐梦境云", "扫帚飞行记忆云", "怀旧时光漂浮云"],
      "gentle-hand": ["男人云", "手撕鸡云", "烧烤摊薯条团", "下班瘫云"],
      "cat-paw": ["午睡前第二团云", "云形毛球 No.1", "喵星人专属云", "软萌抓抓云"],
      collector: ["无声风暴（局部）", "玻璃下的第三种孤独", "未完成作品·2025春", "静物研究 No.7"],
    }

    const descriptions = {
      "magic-broom": [
        "那些年追过的蜻蜓，都变成了云",
        "童年的扫帚，现在用来捕捉回忆",
        "时光倒流，重回无忧岁月",
        "怀念那个相信魔法的自己",
      ],
      "gentle-hand": ["实实在在的一团云", "手感确实不错", "生活就是这么朴实", "简单粗暴，直接有效"],
      "cat-paw": ["喵～软软的触感", "猫咪视角的天空", "毛茸茸的云朵收藏", "午后慵懒时光的见证"],
      collector: ["当代艺术的静默表达", "玻璃与云的对话", "策展人眼中的天空切片", "艺术化的自然标本"],
    }

    const toolNames = names[toolId]
    const toolDescriptions = descriptions[toolId]

    const randomName = toolNames[Math.floor(Math.random() * toolNames.length)]
    const randomDescription = toolDescriptions[Math.floor(Math.random() * toolDescriptions.length)]

    setGeneratedName(randomName)
    setGeneratedDescription(randomDescription)
    setIsGenerating(false)
  }

  const saveToCollection = () => {
    try {
      if (isClient && selectedImage && generatedName && generatedDescription) {
        // 保存到本地存储
        const existingClouds = JSON.parse(localStorage.getItem("cloudCollection") || "[]")
        const newCloud = {
          id: Date.now(),
          image: selectedImage,
          name: generatedName,
          description: generatedDescription,
          tool: tool.name,
          toolIcon: tool.icon,
          capturedAt: new Date().toISOString(),
          location: "未知位置", // MVP版本暂时使用固定值
        }

        existingClouds.unshift(newCloud)
        localStorage.setItem("cloudCollection", JSON.stringify(existingClouds))

        router.push("/collection")
      }
    } catch (error) {
      console.error("保存云朵时出错:", error)
      // 即使保存失败也跳转到收藏页面
      router.push("/collection")
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
                    onClick={() => fileInputRef.current?.click()}
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
                  <Button variant="outline" size="sm" onClick={() => setSelectedImage(null)}>
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
                        <div className="space-y-2">
                          <h3 className="text-2xl font-bold">{generatedName}</h3>
                          <p className="text-sm opacity-80">{generatedDescription}</p>
                        </div>
                      </div>
                    </Card>

                    <Button
                      onClick={saveToCollection}
                      className="w-full py-6 text-lg bg-gradient-to-r from-green-400 to-green-600 hover:from-green-500 hover:to-green-700"
                    >
                      保存到我的天空
                    </Button>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
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
