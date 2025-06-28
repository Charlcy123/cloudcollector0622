import { createClient } from '@supabase/supabase-js'

// 从环境变量获取Supabase配置
// 这些配置需要在.env.local文件中设置
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

// 创建Supabase客户端实例
// 这个客户端用于前端与Supabase进行认证和数据交互
export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    // 设置认证配置
    autoRefreshToken: true, // 自动刷新token
    persistSession: true,   // 持久化会话到localStorage
    detectSessionInUrl: true // 检测URL中的会话信息（用于邮箱验证等）
  }
})

// 导出类型定义，方便TypeScript类型检查
export type Database = any // 这里可以根据你的数据库结构定义具体类型 