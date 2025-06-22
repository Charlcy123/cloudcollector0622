"use client"

import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import Particles from "@/components/ui/particles"
import ProfileCard from "@/components/ui/profile-card"
import SimpleCard from "@/components/ui/simple-card"
import { ArrowLeft, Cloud, Trash2, Calendar, MapPin } from "lucide-react"
import { useRouter } from "next/navigation"
import Image from "next/image"

interface CloudItem {
  id: number
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
  const [clouds, setClouds] = useState<CloudItem[]>([])
  const [selectedCloud, setSelectedCloud] = useState<CloudItem | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const savedClouds = JSON.parse(localStorage.getItem("cloudCollection") || "[]")
    setClouds(savedClouds)
  }, [])

  const deleteCloud = (id: number) => {
    const updatedClouds = clouds.filter((cloud) => cloud.id !== id)
    setClouds(updatedClouds)
    localStorage.setItem("cloudCollection", JSON.stringify(updatedClouds))
    setSelectedCloud(null)
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
        <div className="flex items-center gap-4 mb-8">
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

        {clouds.length === 0 ? (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center py-16">
            <div className="text-8xl text-white/70 mb-6 drop-shadow-lg">☁️</div>
            <h2 className="text-xl font-semibold text-white mb-4 drop-shadow-sm">天空还很空旷</h2>
            <p className="text-white/90 mb-8 drop-shadow-sm">快去捕捉你的第一朵云吧！</p>
            <Button
              onClick={() => router.push("/")}
              className="bg-white/30 backdrop-blur-sm hover:bg-white/40 text-white border border-white/30"
            >
              开始捕云
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
