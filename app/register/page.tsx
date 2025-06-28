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

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const { signUp } = useAuth()
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    // 基本验证
    if (!email || !password || !confirmPassword) {
      setError('请填写所有字段')
      return
    }

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }

    if (password.length < 6) {
      setError('密码长度至少6位')
      return
    }

    setLoading(true)

    try {
      // 调用Supabase注册
      await signUp(email, password)
      setSuccess('注册成功！请检查您的邮箱并点击验证链接。')
      
      // 3秒后跳转到登录页面
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    } catch (error: any) {
      console.error('注册失败:', error)
      setError(error.message || '注册失败，请重试')
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
                  加入云彩收集手册
                </CardTitle>
                <CardDescription className="text-slate-600">
                  创建账户，开始你的云朵收集之旅
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
                        placeholder="请输入密码（至少6位）"
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

                  {/* 确认密码输入 */}
                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword">确认密码</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
                      <Input
                        id="confirmPassword"
                        type={showConfirmPassword ? 'text' : 'password'}
                        placeholder="请再次输入密码"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="pl-10 pr-10"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400 hover:text-slate-600"
                      >
                        {showConfirmPassword ? <EyeOff /> : <Eye />}
                      </button>
                    </div>
                  </div>

                  {/* 错误信息 */}
                  {error && (
                    <div className="text-red-600 text-sm bg-red-50 p-3 rounded-md border border-red-200">
                      {error}
                    </div>
                  )}

                  {/* 成功信息 */}
                  {success && (
                    <div className="text-green-600 text-sm bg-green-50 p-3 rounded-md border border-green-200">
                      {success}
                    </div>
                  )}

                  {/* 注册按钮 */}
                  <Button
                    type="submit"
                    className="w-full"
                    disabled={loading}
                  >
                    {loading ? '注册中...' : '注册'}
                  </Button>

                  {/* 登录链接 */}
                  <div className="text-center text-sm text-slate-600">
                    已有账户？{' '}
                    <Link href="/login" className="text-blue-600 hover:text-blue-800 underline">
                      立即登录
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