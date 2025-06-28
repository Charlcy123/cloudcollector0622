'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Header } from '@/components/Header'
import { AuroraBackground } from '@/components/ui/aurora-background'
import { Mail, Lock, Eye, EyeOff } from 'lucide-react'
import Link from 'next/link'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const { signIn } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    // 基本验证
    if (!email || !password) {
      setError('请填写邮箱和密码')
      return
    }

    setLoading(true)

    try {
      // 调用Supabase登录
      await signIn(email, password)
      // 登录成功后跳转到首页
      router.push('/')
    } catch (error: any) {
      console.error('登录失败:', error)
      setError(error.message || '登录失败，请检查邮箱和密码')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Header />
      <AuroraBackground className="min-h-screen">
        <div className="container mx-auto px-4 pt-20 pb-8">
          <div className="max-w-md mx-auto">
            <Card className="bg-white/80 backdrop-blur-sm border-slate-300">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl font-bold text-slate-800">
                  欢迎回来
                </CardTitle>
                <CardDescription className="text-slate-600">
                  登录您的云彩收集手册账户
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* 邮箱输入 */}
                  <div className="space-y-2">
                    <Label htmlFor="email">邮箱地址</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input
                        id="email"
                        type="email"
                        placeholder="请输入邮箱地址"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  {/* 密码输入 */}
                  <div className="space-y-2">
                    <Label htmlFor="password">密码</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="请输入密码"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="pl-10 pr-10"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400 hover:text-slate-600"
                      >
                        {showPassword ? <EyeOff /> : <Eye />}
                      </button>
                    </div>
                  </div>

                  {/* 错误信息 */}
                  {error && (
                    <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md border border-red-200">
                      {error}
                    </div>
                  )}

                  {/* 登录按钮 */}
                  <Button
                    type="submit"
                    className="w-full"
                    disabled={loading}
                  >
                    {loading ? '登录中...' : '登录'}
                  </Button>

                  {/* 注册链接 */}
                  <div className="text-center text-sm text-slate-600">
                    还没有账户？{' '}
                    <Link href="/register" className="text-blue-600 hover:text-blue-800 underline">
                      立即注册
                    </Link>
                  </div>

                  {/* 忘记密码 */}
                  <div className="text-center">
                    <Link href="#" className="text-xs text-slate-500 hover:text-slate-700 underline">
                      忘记密码？
                    </Link>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </AuroraBackground>
    </>
  )
} 