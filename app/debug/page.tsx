"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { useAuth } from "@/contexts/AuthContext"
import { authenticatedFetch, API_BASE_URL } from "@/lib/api"

export default function DebugPage() {
  const { user, loading: authLoading } = useAuth()
  const [debugInfo, setDebugInfo] = useState<any>({})
  const [apiResponse, setApiResponse] = useState<any>(null)
  const [error, setError] = useState<string>('')

  const runDebugTests = async () => {
    setError('')
    const debug: any = {
      timestamp: new Date().toISOString(),
      userInfo: {
        isLoggedIn: !!user,
        userId: user?.id,
        userEmail: user?.email,
        authLoading: authLoading
      },
      apiTests: {}
    }

    // 获取当前session和token
    const { supabase } = await import('@/lib/supabase')
    const { data: { session } } = await supabase.auth.getSession()

    try {
      // 测试1: 基础API调用
      console.log('测试基础API...')
      const basicResponse = await fetch(`${API_BASE_URL}/api/capture-tools`)
      debug.apiTests.basicAPI = {
        status: basicResponse.status,
        ok: basicResponse.ok,
        dataLength: basicResponse.ok ? (await basicResponse.json()).length : 0
      }

      // 测试2: 认证API调用
      if (user) {
        console.log('测试认证API...')
        console.log('当前用户ID:', user.id)
        console.log('当前用户邮箱:', user.email)
        console.log('Supabase session:', session?.user?.id)
        console.log('Access token存在:', !!session?.access_token)
        
        const authResponse = await authenticatedFetch('/api/v2/my-collections?page=1&page_size=10')
        debug.apiTests.authAPI = {
          status: authResponse.status,
          ok: authResponse.ok,
          headers: Object.fromEntries(authResponse.headers.entries()),
          userIdFromContext: user.id,
          userIdFromSession: session?.user?.id,
          tokenExists: !!session?.access_token
        }

        if (authResponse.ok) {
          const data = await authResponse.json()
          debug.apiTests.authAPI.data = data
          setApiResponse(data)
        } else {
          const errorText = await authResponse.text()
          debug.apiTests.authAPI.error = errorText
        }
      } else {
        debug.apiTests.authAPI = { error: '用户未登录' }
      }

      // 测试3: 检查localStorage中的token
      if (typeof window !== 'undefined') {
        // 检查多种可能的token存储位置
        const supabaseAuthToken = localStorage.getItem('sb-kntrbjwbrzrwlcspblkw-auth-token')
        const supabaseSession = localStorage.getItem('supabase.auth.token')
        const allKeys = Object.keys(localStorage).filter(key => 
          key.includes('auth') || key.includes('token') || key.includes('supabase')
        )
        
        debug.localStorage = {
          hasSupabaseAuthToken: !!supabaseAuthToken,
          supabaseAuthTokenPreview: supabaseAuthToken ? supabaseAuthToken.substring(0, 50) + '...' : null,
          hasSupabaseSession: !!supabaseSession,
          allAuthKeys: allKeys,
          allKeysCount: Object.keys(localStorage).length
        }
      }

      // 测试4: 直接查询特定用户的数据
      if (user && session) {
        console.log('测试直接数据库查询...')
        try {
          // 使用管理员权限直接查询数据库
          const directResponse = await fetch(`${API_BASE_URL}/api/auth/test`, {
            headers: {
              'Authorization': `Bearer ${session.access_token}`
            }
          })
          debug.apiTests.directDBTest = {
            status: directResponse.status,
            ok: directResponse.ok
          }
          
          if (directResponse.ok) {
            const testData = await directResponse.json()
            debug.apiTests.directDBTest.data = testData
          }
        } catch (err) {
          debug.apiTests.directDBTest = { error: err instanceof Error ? err.message : String(err) }
        }
      }

    } catch (err) {
      debug.error = err instanceof Error ? err.message : String(err)
      setError(debug.error)
    }

    setDebugInfo(debug)
    console.log('调试信息:', debug)
  }

  useEffect(() => {
    if (!authLoading) {
      runDebugTests()
    }
  }, [user, authLoading])

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8">系统调试页面</h1>
      
      <div className="grid gap-6">
        {/* 用户信息卡片 */}
        <Card>
          <CardHeader>
            <CardTitle>用户认证状态</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p><strong>登录状态:</strong> {user ? '已登录' : '未登录'}</p>
              <p><strong>用户ID:</strong> {user?.id || 'N/A'}</p>
              <p><strong>用户邮箱:</strong> {user?.email || 'N/A'}</p>
              <p><strong>认证加载中:</strong> {authLoading ? '是' : '否'}</p>
            </div>
          </CardContent>
        </Card>

        {/* API测试结果 */}
        <Card>
          <CardHeader>
            <CardTitle>API测试结果</CardTitle>
          </CardHeader>
          <CardContent>
            <Button onClick={runDebugTests} className="mb-4">
              重新运行测试
            </Button>
            
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                <strong>错误:</strong> {error}
              </div>
            )}
            
            <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm">
              {JSON.stringify(debugInfo, null, 2)}
            </pre>
          </CardContent>
        </Card>

        {/* API响应数据 */}
        {apiResponse && (
          <Card>
            <CardHeader>
              <CardTitle>我的收藏API响应</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="mb-4">
                <strong>收藏数量:</strong> {apiResponse.collections?.length || 0}
              </p>
              
              {apiResponse.collections && apiResponse.collections.length > 0 && (
                <div className="space-y-4">
                  <h3 className="font-semibold">收藏列表:</h3>
                  {apiResponse.collections.map((collection: any, index: number) => (
                    <div key={index} className="border p-3 rounded">
                      <p><strong>ID:</strong> {collection.id}</p>
                      <p><strong>名称:</strong> {collection.cloud_name}</p>
                      <p><strong>描述:</strong> {collection.cloud_description}</p>
                      <p><strong>用户ID:</strong> {collection.user_id}</p>
                      <p><strong>捕获时间:</strong> {collection.capture_time}</p>
                      <p><strong>工具:</strong> {collection.tool_name} {collection.tool_emoji}</p>
                    </div>
                  ))}
                </div>
              )}
              
              <details className="mt-4">
                <summary className="cursor-pointer font-semibold">查看完整响应</summary>
                <pre className="bg-gray-100 p-4 rounded overflow-auto text-sm mt-2">
                  {JSON.stringify(apiResponse, null, 2)}
                </pre>
              </details>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
} 