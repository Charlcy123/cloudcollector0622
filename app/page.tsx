"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Button } from "@/components/ui/button"
import { ButtonColorful } from "@/components/ui/button-colorful"
import { Card } from "@/components/ui/card"
import { SpringElement } from "@/components/ui/spring-element"
import { HandWrittenTitle } from "@/components/ui/hand-writing-text"
import { AuroraBackground } from "@/components/ui/aurora-background"
import { Header } from "@/components/Header"
import { Cloud, Sparkles } from "lucide-react"
import Link from "next/link"

const tools = [
  {
    id: "magic-broom",
    name: "水晶球",
    icon: "🔮",
    description: "摇到它头晕——蹦出的预言全醉啦！",
    color: "from-purple-400 to-purple-600",
    bgColor: "bg-purple-50",
    textColor: "text-purple-700",
  },
  {
    id: "gentle-hand",
    name: "手",
    icon: "✋",
    description: "手感不错，一把捏住",
    color: "from-pink-400 to-pink-600",
    bgColor: "bg-pink-50",
    textColor: "text-pink-700",
  },
  {
    id: "cat-paw",
    name: "猫爪",
    icon: "🐾",
    description: "喵～这团软软的云，我先抓到咯！",
    color: "from-orange-400 to-orange-600",
    bgColor: "bg-orange-50",
    textColor: "text-orange-700",
  },
  {
    id: "glass-cover",
    name: "红笔",
    icon: "✍️",
    description: "点一下，向天空催更",
    color: "from-red-400 to-red-600",
    bgColor: "bg-red-50",
    textColor: "text-red-700",
  },
]

export default function HomePage() {
  const [showTools, setShowTools] = useState(false)

  return (
    <>
      {/* 添加顶栏 */}
      <Header />
      
      <AuroraBackground className="min-h-screen relative overflow-hidden">
        {/* 背景装饰云朵 - 现在可以拖拽！ */}
        <div className="absolute inset-0 pointer-events-none z-10">
          <SpringElement 
            className="absolute top-20 left-10 pointer-events-auto"
            springConfig={{ stiffness: 150, damping: 12 }}
            springPathConfig={{ coilCount: 10, amplitude: 20 }}
            dragElastic={0.3}
          >
            <motion.div
              className="text-slate-600/70 text-6xl drop-shadow-lg select-none"
              animate={{ rotate: [0, 5, -5, 0] }}
              transition={{ duration: 8, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut" }}
            >
              ☁️
            </motion.div>
          </SpringElement>
          
          <SpringElement 
            className="absolute top-40 right-20 pointer-events-auto"
            springConfig={{ stiffness: 180, damping: 14 }}
            springPathConfig={{ coilCount: 8, amplitude: 25 }}
            dragElastic={0.25}
          >
            <motion.div
              className="text-slate-600/60 text-4xl drop-shadow-lg select-none"
              animate={{ rotate: [0, -3, 3, 0] }}
              transition={{ duration: 6, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut", delay: 1 }}
            >
              ☁️
            </motion.div>
          </SpringElement>
          
          <SpringElement 
            className="absolute bottom-40 left-1/4 pointer-events-auto"
            springConfig={{ stiffness: 120, damping: 10 }}
            springPathConfig={{ coilCount: 14, amplitude: 18 }}
            dragElastic={0.4}
          >
            <motion.div
              className="text-slate-600/65 text-5xl drop-shadow-lg select-none"
              animate={{ rotate: [0, 4, -4, 0] }}
              transition={{ duration: 10, repeat: Number.POSITIVE_INFINITY, ease: "easeInOut", delay: 2 }}
            >
              ☁️
            </motion.div>
          </SpringElement>
        </div>

        {/* 添加顶部间距以适应固定顶栏 */}
        <div className="relative z-20 container mx-auto px-4 py-8 pt-20">
          {/* 头部 */}
          <div className="text-center mb-12">
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="flex items-center justify-center gap-3 mb-6"
            >
              <h1 className="text-5xl font-extrabold text-slate-800">云彩收集手册</h1>
            </motion.div>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-gray-600 text-lg leading-relaxed"
            >
              天空太大，云太多
              <br />
              用你的方式，记录它们短暂而浪漫的停留
            </motion.p>
          </div>

          {/* 主要内容区域 */}
          <div className="max-w-md mx-auto">
            {/* 我的天空按钮 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="mb-4"
            >
              <Link href="/collection">
                <div className="transform hover:scale-105 transition-transform duration-300 cursor-pointer">
                  <ButtonColorful 
                    label="我的天空"
                    className="w-full py-6 text-lg"
                  />
                </div>
              </Link>
            </motion.div>

            {/* 开始捕云按钮 - 替换为手写文字效果 */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="mb-10 cursor-pointer"
              onClick={() => setShowTools(!showTools)}
            >
              <div className="transform hover:scale-110 transition-transform duration-300">
                <HandWrittenTitle 
                  title="开始捕云" 
                  subtitle={showTools ? "选择你的工具" : "点击开始你的云彩之旅"}
                />
              </div>
            </motion.div>

            {/* 工具选择 */}
            <AnimatePresence>
              {showTools && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.5 }}
                  className="space-y-5"
                >
                  {tools.map((tool, index) => (
                    <motion.div
                      key={tool.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                    >
                      <Link href={`/capture?tool=${tool.id}`}>
                        <Card
                          className="p-4 cursor-pointer hover:shadow-lg transition-all duration-300 bg-white/60 backdrop-blur-sm border-slate-300 hover:bg-white/80 hover:border-slate-400 text-slate-700"
                        >
                          <div className="flex items-center gap-4">
                            <div className="text-3xl">{tool.icon}</div>
                            <div className="flex-1">
                              <h3 className="font-semibold text-lg">{tool.name}</h3>
                              <p className="text-sm opacity-80">{tool.description}</p>
                            </div>
                          </div>
                        </Card>
                      </Link>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* 底部文字 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.8, delay: 1 }}
            className="text-center mt-20 text-slate-500"
          >
            <p className="text-sm">捕捉自然的温柔一瞬</p>
            
            {/* 开发者测试链接 */}
            <div className="mt-8">
              <Link href="/test-api">
                <Button variant="ghost" size="sm" className="text-xs text-slate-400 hover:text-slate-600">
                  🔧 API 测试面板
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </AuroraBackground>
    </>
  )
}
