"use client"

import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import Particles from "@/components/ui/particles"
import ProfileCard from "@/components/ui/profile-card"
import SimpleCard from "@/components/ui/simple-card"
import { ArrowLeft, Cloud, Trash2, Calendar, MapPin, Loader2, RefreshCw } from "lucide-react"
import { useRouter } from "next/navigation"
import Image from "next/image"
import { useAuth } from "@/contexts/AuthContext"
import { authenticatedFetch, API_BASE_URL } from "@/lib/api"

interface CloudItem {
  id: string
  image: string
  name: string
  description: string
  tool: string
  toolIcon: string
  capturedAt: string
  location: string
}

export default function CollectionPage() {
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const [clouds, setClouds] = useState<CloudItem[]>([])
  const [selectedCloud, setSelectedCloud] = useState<CloudItem | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [error, setError] = useState<string>('')
  const containerRef = useRef<HTMLDivElement>(null)

  // 加载用户的云朵收藏
  const loadUserCollections = async (showRefreshingState = false) => {
    // 如果认证还在加载中，等待
    if (authLoading) return
    
    // 如果用户未登录，重定向到登录页
    if (!user) {
      console.log('用户未登录，重定向到登录页')
      router.push('/login')
      return
    }

    try {
      if (showRefreshingState) {
        setIsRefreshing(true)
      } else {
        setIsLoading(true)
      }
      setError('')

      console.log('开始加载用户云朵收藏...')
      console.log('当前用户:', user)

      // 使用JWT认证的API获取用户收藏
      const response = await authenticatedFetch('/api/v2/my-collections?page=1&page_size=100')
      
      console.log('API响应状态:', response.status)
      console.log('API响应headers:', Object.fromEntries(response.headers.entries()))
      
      if (!response.ok) {
        console.error('API请求失败，状态码:', response.status)
        if (response.status === 401) {
          console.log('Token过期或无效，重定向到登录页')
          router.push('/login')
          return
        }
        const errorText = await response.text()
        console.error('错误响应内容:', errorText)
        throw new Error(`API请求失败: ${response.status} - ${errorText}`)
      }

      const data = await response.json()
      console.log('获取到的原始数据:', data)
      console.log('收藏数量:', data.collections?.length || 0)
      console.log('完整的collections数组:', JSON.stringify(data.collections, null, 2))
      
      // 检查数据结构
      if (!data.collections || !Array.isArray(data.collections)) {
        console.error('数据格式错误: collections不是数组', data)
        throw new Error('数据格式错误')
      }
      
      // 转换数据格式以匹配现有UI
      const cloudItems: CloudItem[] = data.collections.map((collection: any, index: number) => {
        console.log(`处理第${index + 1}个收藏项:`, {
          id: collection.id,
          cloud_name: collection.cloud_name,
          tool_id: collection.tool_id,
          original_image_url: collection.original_image_url
        })
        
        // 处理位置信息 - 修复版本
        let locationText = '未知位置';
        
        // 尝试从不同的数据结构中获取位置信息
        if (collection.location) {
          if (typeof collection.location === 'string') {
            // 如果location是字符串
            locationText = collection.location;
          } else if (collection.location.address) {
            // 如果location是对象且有address字段
            locationText = collection.location.address;
          } else if (Array.isArray(collection.location) && collection.location.length > 0) {
            // 如果location是数组（关联查询结果）
            locationText = collection.location[0]?.address || '未知位置';
          }
        }
        
        console.log(`收藏项 ${index + 1} 的位置信息:`, {
          原始location: collection.location,
          解析后的locationText: locationText,
          工具ID: collection.tool_id
        });
        
        // 如果位置是默认值或空值，使用工具特定的个性化位置
        if (locationText === '未知位置' || locationText === '位置未知' || !locationText || locationText.trim() === '') {
          const toolSpecificLocations = {
            'glassCover': '意念定位中…',
            'hand': '摸鱼时区深处',
            'catPaw': '躲猫猫冠军认证点🐾',
            'broom': '所有可能性的交汇处',
            // 添加可能的其他工具ID映射
            'crystal-ball': '意念定位中…',
            'cloud-hand': '摸鱼时区深处',
            'cat-paw': '躲猫猫冠军认证点🐾',
            'red-pen': '所有可能性的交汇处'
          };
          
          const toolId = collection.tool_id;
          locationText = toolSpecificLocations[toolId as keyof typeof toolSpecificLocations] || '神秘维度';
          
          console.log(`使用工具特定位置: 工具ID=${toolId}, 位置=${locationText}`);
        }
        
        const cloudItem = {
          id: collection.id,
          image: collection.original_image_url,
          name: collection.cloud_name,
          description: collection.cloud_description || '',
          tool: collection.tool_name,
          toolIcon: collection.tool_emoji,
          capturedAt: collection.capture_time,
          location: locationText
        }
        
        console.log(`转换后的云朵项:`, cloudItem)
        return cloudItem
      })

      console.log('=== 最终转换结果 ===')
      console.log('转换后的云朵数据数量:', cloudItems.length)
      console.log('转换后的云朵数据:', JSON.stringify(cloudItems, null, 2))
      console.log('即将设置到state的数据:', cloudItems)
      
      // 添加位置信息的详细调试
      cloudItems.forEach((item, index) => {
        console.log(`云朵 ${index + 1} 的位置信息:`, {
          id: item.id,
          name: item.name,
          location: item.location,
          tool: item.tool,
          toolIcon: item.toolIcon
        });
      });
      
      setClouds(cloudItems)
      console.log('setClouds 调用完成')

    } catch (error) {
      console.error('加载数据失败:', error)
      setError(error instanceof Error ? error.message : '加载失败')
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  useEffect(() => {
    loadUserCollections()
  }, [user, authLoading, router])

  // 手动刷新
  const handleRefresh = () => {
    loadUserCollections(true)
  }

  const deleteCloud = async (id: string) => {
    try {
      const response = await authenticatedFetch(`/api/v2/cloud-collections/${id}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) {
        throw new Error('删除失败')
      }

      // 从本地状态中移除
      const updatedClouds = clouds.filter((cloud) => cloud.id !== id)
      setClouds(updatedClouds)
      setSelectedCloud(null)
      
    } catch (error) {
      console.error('删除云朵失败:', error)
      alert(`删除失败: ${error instanceof Error ? error.message : '未知错误'}`)
    }
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("zh-CN", {
      year: "numeric",
      month: "long",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  // 认证加载状态
  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-sky-200 via-sky-100 to-white">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-sky-600 mx-auto" />
          <p className="text-sky-600">正在验证身份...</p>
        </div>
      </div>
    )
  }

  // 数据加载状态
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-sky-200 via-sky-100 to-white">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-sky-600 mx-auto" />
          <p className="text-sky-600">正在加载你的天空...</p>
        </div>
      </div>
    )
  }

  // 错误状态
  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-sky-200 via-sky-100 to-white">
        <div className="text-center space-y-4">
          <div className="text-6xl text-red-400 mb-4">😢</div>
          <h2 className="text-xl font-semibold text-red-600">加载失败</h2>
          <p className="text-red-500">{error}</p>
          <Button onClick={() => window.location.reload()} className="mt-4">
            重新加载
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div 
      ref={containerRef}
      className="min-h-screen relative overflow-hidden"
      style={{
        background: 'linear-gradient(to bottom right, #0f172a, #020617, #0c0a09)',
        minHeight: '100vh',
      }}
    >
      {/* 粒子背景 */}
      <Particles
        className="absolute inset-0"
        particleCount={400}
        particleSpread={20}
        speed={0.08}
        particleColors={["#ffffff", "#f0f9ff", "#dbeafe", "#bfdbfe", "#93c5fd", "#60a5fa", "#3b82f6"]}
        moveParticlesOnHover={true}
        particleHoverFactor={0.8}
        alphaParticles={true}
        particleBaseSize={120}
        sizeRandomness={1.2}
        cameraDistance={20}
        disableRotation={false}
      />
      
      {/* 半透明遮罩层，让内容更易读 */}
      <div 
        className="absolute inset-0 backdrop-blur-[0.5px] z-10"
        style={{
          backgroundColor: 'rgba(0, 0, 0, 0.4)',
        }}
      />

      {/* 背景装饰云朵 */}
      <div className="absolute inset-0 pointer-events-none z-20">
        <motion.div
          className="absolute top-10 right-10 text-white/40 text-4xl drop-shadow-lg"
          animate={{ x: [0, -20, 0], y: [0, 10, 0] }}
          transition={{ duration: 12, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
        >
          ☁️
        </motion.div>
        <motion.div
          className="absolute bottom-20 left-10 text-white/35 text-5xl drop-shadow-lg"
          animate={{ x: [0, 30, 0], y: [0, -15, 0] }}
          transition={{ duration: 15, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut", delay: 3 }}
        >
          ☁️
        </motion.div>
      </div>

      <div className="relative z-30 container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <Button 
              variant="ghost" 
              size="icon" 
              onClick={() => router.back()} 
              className="text-white hover:bg-white/20 backdrop-blur-sm"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex items-center gap-3">
              <Cloud className="w-6 h-6 text-white drop-shadow-md" />
              <h1 className="text-2xl font-bold text-white drop-shadow-md">我的天空</h1>
            </div>
          </div>
          
          {/* 刷新按钮 */}
          <Button
            variant="ghost"
            size="icon"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="text-white hover:bg-white/20 backdrop-blur-sm"
          >
            <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
          </Button>
          
          {/* 临时调试按钮 */}
          <Button
            variant="ghost"
            size="sm"
            onClick={async () => {
              console.log('=== API调试测试 ===')
              console.log('当前用户:', user)
              console.log('认证状态:', { user: !!user, loading: authLoading })
              
              try {
                // 测试简单的API调用
                const testResponse = await fetch(`${API_BASE_URL}/api/capture-tools`)
                console.log('测试API响应状态:', testResponse.status)
                const testData = await testResponse.json()
                console.log('测试API数据:', testData)
                
                // 测试认证API调用
                const authResponse = await authenticatedFetch('/api/v2/my-collections?page=1&page_size=5')
                console.log('认证API响应状态:', authResponse.status)
                const authData = await authResponse.json()
                console.log('认证API数据:', authData)
              } catch (error) {
                console.error('API测试失败:', error)
              }
            }}
            className="text-white hover:bg-white/20 backdrop-blur-sm text-xs"
          >
            调试API
          </Button>
        </div>

        {clouds.length === 0 ? (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center py-16">
            <div className="text-8xl text-white/70 mb-6 drop-shadow-lg">☁️</div>
            <h2 className="text-xl font-semibold text-white mb-4 drop-shadow-sm">天空还很空旷</h2>
            <Button
              onClick={() => router.push("/")}
              className="bg-white/30 backdrop-blur-sm hover:bg-white/40 text-white border border-white/30"
            >
              回到首页捕云
            </Button>
          </motion.div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {clouds.map((cloud, index) => (
              <motion.div
                key={cloud.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="aspect-video"
              >
                <SimpleCard
                  className="h-full"
                  onClick={() => setSelectedCloud(cloud)}
                >
                  <div className="relative w-full h-full">
                    <Image
                      src={cloud.image || "/placeholder.svg"}
                      alt={cloud.name}
                      fill
                      className="object-cover"
                    />
                    <div className="absolute top-2 right-2 text-2xl bg-white/80 rounded-full p-1 z-10">
                      {cloud.toolIcon}
                    </div>
                    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4 z-10">
                      <h3 className="font-semibold text-lg text-white mb-1 drop-shadow-sm">{cloud.name}</h3>
                      <p className="text-sm text-white/90 mb-2 drop-shadow-sm line-clamp-2">{cloud.description}</p>
                      <div className="flex items-center gap-2 text-xs text-white/80">
                        <Calendar className="w-3 h-3" />
                        {formatDate(cloud.capturedAt)}
                      </div>
                    </div>
                  </div>
                </SimpleCard>
              </motion.div>
            ))}
          </div>
        )}

        {/* 云朵详情弹窗 */}
        <AnimatePresence>
          {selectedCloud && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50"
              onClick={() => setSelectedCloud(null)}
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.9, opacity: 0 }}
                className="bg-white rounded-2xl max-w-md w-full max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="relative aspect-video">
                  <Image
                    src={selectedCloud.image || "/placeholder.svg"}
                    alt={selectedCloud.name}
                    fill
                    className="object-cover rounded-t-2xl"
                  />
                  <div className="absolute top-4 right-4 text-3xl bg-white/90 rounded-full p-2">
                    {selectedCloud.toolIcon}
                  </div>
                </div>

                <div className="p-6 space-y-4">
                  <div>
                    <h2 className="text-2xl font-bold text-sky-800 mb-2">{selectedCloud.name}</h2>
                    <p className="text-sky-600">{selectedCloud.description}</p>
                  </div>

                  <div className="space-y-2 text-sm text-sky-500">
                    <div className="flex items-center gap-2">
                      <span className="text-lg">{selectedCloud.toolIcon}</span>
                      <span>使用 {selectedCloud.tool} 捕获</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      <span>{formatDate(selectedCloud.capturedAt)}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      <span>{selectedCloud.location}</span>
                    </div>
                  </div>

                  <div className="flex gap-3 pt-4">
                    <Button
                      variant="outline"
                      onClick={() => setSelectedCloud(null)}
                      className="flex-1"
                    >
                      关闭
                    </Button>
                    <Button
                      variant="destructive"
                      onClick={() => deleteCloud(selectedCloud.id)}
                      className="flex-1"
                    >
                      <Trash2 className="w-4 h-4 mr-2" />
                      删除
                    </Button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
