'use client'

import { createContext, useContext, useEffect, useState } from 'react'
import { User, Session } from '@supabase/supabase-js'
import { supabase } from '@/lib/supabase'

// 定义认证上下文的类型
interface AuthContextType {
  user: User | null           // 当前登录用户信息
  session: Session | null     // 当前会话信息（包含JWT token）
  loading: boolean           // 是否正在加载认证状态
  signUp: (email: string, password: string) => Promise<any>    // 注册函数
  signIn: (email: string, password: string) => Promise<any>    // 登录函数
  signOut: () => Promise<any>                                  // 登出函数
  getToken: () => string | null                               // 获取JWT token
}

// 创建认证上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined)

// 认证提供者组件
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // 获取当前会话
    const getSession = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      setSession(session)
      
      // 确保用户ID与JWT token中的sub字段一致
      if (session?.user && session?.access_token) {
        try {
          // 解码JWT token获取真实的用户ID
          const tokenParts = session.access_token.split('.');
          if (tokenParts.length === 3) {
            const payload = JSON.parse(atob(tokenParts[1]));
            
            // 使用JWT token中的sub作为用户ID，确保一致性
            const userWithCorrectId = {
              ...session.user,
              id: payload.sub  // 强制使用JWT中的sub作为用户ID
            };
            
            console.log('修正用户ID:', {
              originalUserId: session.user.id,
              jwtTokenSub: payload.sub,
              finalUserId: userWithCorrectId.id
            });
            
            setUser(userWithCorrectId);
          } else {
            setUser(session?.user ?? null);
          }
        } catch (error) {
          console.error('解析JWT token失败:', error);
          setUser(session?.user ?? null);
        }
      } else {
        setUser(session?.user ?? null);
      }
      
      setLoading(false)
    }

    getSession()

    // 监听认证状态变化
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      async (event, session) => {
        console.log('Auth state changed:', event, session?.user?.email)
        setSession(session)
        
        // 同样的逻辑应用到状态变化时
        if (session?.user && session?.access_token) {
          try {
            const tokenParts = session.access_token.split('.');
            if (tokenParts.length === 3) {
              const payload = JSON.parse(atob(tokenParts[1]));
              const userWithCorrectId = {
                ...session.user,
                id: payload.sub
              };
              setUser(userWithCorrectId);
            } else {
              setUser(session?.user ?? null);
            }
          } catch (error) {
            console.error('解析JWT token失败:', error);
            setUser(session?.user ?? null);
          }
        } else {
          setUser(session?.user ?? null);
        }
        
        setLoading(false)
      }
    )

    // 清理订阅
    return () => subscription.unsubscribe()
  }, [])

  // 注册函数
  const signUp = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signUp({
      email,
      password,
    })
    if (error) throw error
    return data
  }

  // 登录函数
  const signIn = async (email: string, password: string) => {
    const { data, error } = await supabase.auth.signInWithPassword({
      email,
      password,
    })
    if (error) throw error
    return data
  }

  // 登出函数
  const signOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) throw error
  }

  // 获取当前JWT token
  const getToken = () => {
    return session?.access_token ?? null
  }

  const value = {
    user,
    session,
    loading,
    signUp,
    signIn,
    signOut,
    getToken,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// 使用认证上下文的Hook
export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 