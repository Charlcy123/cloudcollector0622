import { supabase } from './supabase'

// API基础URL
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// 获取当前用户的JWT Token
const getAuthToken = async (): Promise<string | null> => {
  const { data: { session } } = await supabase.auth.getSession()
  return session?.access_token ?? null
}

// 创建带认证的fetch请求
export const authenticatedFetch = async (
  url: string, 
  options: RequestInit = {}
): Promise<Response> => {
  // 获取JWT Token
  const token = await getAuthToken()
  
  // 构建请求头 - 使用正确的类型定义
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers as Record<string, string>,
  }
  
  // 如果有token，添加到Authorization头
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  // 发送请求
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers,
  })
  
  return response
}

// 便捷的API调用方法
export const api = {
  // GET请求
  get: async (url: string) => {
    return authenticatedFetch(url, { method: 'GET' })
  },
  
  // POST请求
  post: async (url: string, data: any) => {
    return authenticatedFetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
    })
  },
  
  // PUT请求
  put: async (url: string, data: any) => {
    return authenticatedFetch(url, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  },
  
  // DELETE请求
  delete: async (url: string) => {
    return authenticatedFetch(url, { method: 'DELETE' })
  },
  
  // PATCH请求
  patch: async (url: string, data?: any) => {
    return authenticatedFetch(url, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    })
  },
}

// 使用示例：
// const response = await api.get('/api/users/me')
// const userData = await response.json()

// 文件上传（带认证）
export const uploadWithAuth = async (
  url: string,
  formData: FormData
): Promise<Response> => {
  const token = await getAuthToken()
  
  const headers: Record<string, string> = {}
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return fetch(`${API_BASE_URL}${url}`, {
    method: 'POST',
    headers,
    body: formData,
  })
} 