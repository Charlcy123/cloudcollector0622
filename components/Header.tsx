'use client'

import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'
import { LogIn, LogOut, UserPlus } from 'lucide-react'

// 简化的顶栏组件 - 只显示登录和注册图标
export function Header() {
  const { user, signOut } = useAuth()

  // 如果用户已登录，显示登出按钮；否则显示登录和注册图标
  if (user) {
    return (
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 1000 }}>
        <button
          onClick={signOut}
          style={{
            background: 'rgba(255, 255, 255, 0.9)',
            border: 'none',
            borderRadius: '50%',
            width: '40px',
            height: '40px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            backdropFilter: 'blur(10px)',
            color: '#64748b',
            transition: 'all 0.2s ease'
          }}
          title="登出"
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.1)'
            e.currentTarget.style.color = '#dc2626'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.9)'
            e.currentTarget.style.color = '#64748b'
          }}
        >
          <LogOut size={18} />
        </button>
      </div>
    )
  }

  return (
    <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 1000 }}>
      <div style={{ display: 'flex', gap: '10px' }}>
        {/* 登录图标 */}
        <Link href="/login">
          <button
            style={{
              background: 'rgba(255, 255, 255, 0.9)',
              border: 'none',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              backdropFilter: 'blur(10px)',
              color: '#64748b',
              transition: 'all 0.2s ease'
            }}
            title="登录"
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(59, 130, 246, 0.1)'
              e.currentTarget.style.color = '#2563eb'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.9)'
              e.currentTarget.style.color = '#64748b'
            }}
          >
            <LogIn size={18} />
          </button>
        </Link>
        
        {/* 注册图标 */}
        <Link href="/register">
          <button
            style={{
              background: 'rgba(255, 255, 255, 0.9)',
              border: 'none',
              borderRadius: '50%',
              width: '40px',
              height: '40px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              backdropFilter: 'blur(10px)',
              color: '#64748b',
              transition: 'all 0.2s ease'
            }}
            title="注册"
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'rgba(34, 197, 94, 0.1)'
              e.currentTarget.style.color = '#16a34a'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.9)'
              e.currentTarget.style.color = '#64748b'
            }}
          >
            <UserPlus size={18} />
          </button>
        </Link>
      </div>
    </div>
  )
} 