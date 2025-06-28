'use client'

import { useAuth } from '@/contexts/AuthContext'
import Link from 'next/link'

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
            fontSize: '18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            backdropFilter: 'blur(10px)'
          }}
          title="登出"
        >
          🚪
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
              fontSize: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              backdropFilter: 'blur(10px)'
            }}
            title="登录"
          >
            🔑
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
              fontSize: '18px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              backdropFilter: 'blur(10px)'
            }}
            title="注册"
          >
            ➕
          </button>
        </Link>
      </div>
    </div>
  )
} 