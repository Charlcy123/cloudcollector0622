/**
 * 云彩收集手册 API 封装
 * Cloud Collector API utilities
 */

import { createClient } from '@supabase/supabase-js';

// ============== 基础配置 ==============
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.cloudcollector.xyz';

// API 请求配置
const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
};

// ============== 类型定义 ==============
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

// 用户相关类型
export interface User {
  id: string;
  device_id: string;
  display_name: string;
  is_anonymous: boolean;
  created_at: string;
}

export interface UserCreateRequest {
  device_id: string;
  display_name?: string;
}

// 捕云工具类型
export interface CaptureTool {
  id: string;
  name: string;
  emoji: string;
  description: string;
  sort_order: number;
}

// 云朵收藏类型
export interface CloudCollection {
  id: string;
  user_id: string;
  tool_id: string;
  tool_name: string;
  tool_emoji: string;
  original_image_url: string;
  cropped_image_url?: string;
  thumbnail_url?: string;
  cloud_name: string;
  cloud_description?: string;
  keywords: string[];
  capture_time: string;
  is_favorite: boolean;
  view_count: number;
  location?: any;
  weather?: any;
  created_at: string;
}

export interface CloudCollectionCreateRequest {
  tool_id: string;
  latitude: number;
  longitude: number;
  address?: string;
  city?: string;
  country?: string;
  original_image_url: string;
  cropped_image_url?: string;
  thumbnail_url?: string;
  cloud_name: string;
  cloud_description?: string;
  keywords?: string[];
  image_features?: any;
  capture_time: string;
  weather_data?: any;
}

export interface CloudCollectionListResponse {
  collections: CloudCollection[];
  total: number;
  page: number;
  page_size: number;
}

// AI 相关类型
export interface ImageFeatures {
  shape: string;
  color: string;
  texture: string;
}

export interface CloudContext {
  time: string;
  weather?: string;
  location: string;
}

export interface CloudNameRequest {
  tool: string;
  imageFeatures: ImageFeatures;
  context: CloudContext;
}

export interface CloudNameImageRequest {
  tool: string;
  image: string;
  context: CloudContext;
}

export interface CloudNameResponse {
  name: string;
  description: string;
  style: string;
}

export interface CloudDescriptionRequest {
  cloudName: string;
  imageFeatures: ImageFeatures;
  tool: string;
}

export interface CloudDescriptionImageRequest {
  tool: string;
  image: string;
  context?: CloudContext;
  cloudName?: string;
}

export interface CloudDescriptionResponse {
  description: string;
  keywords: string[];
}

export interface CloudAnalysisRequest {
  image: string;
  options: {
    detectShape: boolean;
    detectColor: boolean;
    detectTexture: boolean;
  };
}

export interface CloudAnalysisResponse {
  features: {
    shape: string;
    color: string;
    texture: string;
    confidence: number;
  };
  metadata: {
    width: number;
    height: number;
    format: string;
  };
}

// 天气相关类型
export interface WeatherResponse {
  weather: {
    main: string;
    description: string;
    icon: string;
    temperature: number;
  };
  location_id: string;
  location_info: {
    address: string;
    city: string;
    country: string;
  };
}

// 分享图片类型
export interface ShareImageRequest {
  image_url: string;
  cloud_name: string;
  description: string;
  tool_icon: string;
  captured_at: string;
  location: string;
}

export interface ShareImageResponse {
  share_image_url: string;
}

// EXIF 相关类型
export interface ExifGpsInfo {
  latitude: number;
  longitude: number;
  source: string;
}

export interface ExifLocationInfo {
  address: string;
  city: string;
  country: string;
  source: string;
}

export interface ExifResponse {
  has_gps: boolean;
  gps_info?: ExifGpsInfo;
  location_info?: ExifLocationInfo;
  capture_time?: string;
  has_capture_time: boolean;
}

// 云朵收藏响应类型
export interface CloudCollectionResponse {
  id: string;
  user_id: string;
  tool_id: string;
  tool_name: string;
  tool_emoji: string;
  original_image_url: string;
  cropped_image_url?: string;
  thumbnail_url?: string;
  cloud_name: string;
  cloud_description?: string;
  keywords: string[];
  capture_time: string;
  is_favorite: boolean;
  view_count: number;
  location?: any;
  weather?: any;
  created_at: string;
}

// ============== 存储管理 API ==============
export const storageAPI = {
  /**
   * 上传图片到Supabase Storage（通过后端API）
   */
  async uploadImage(
    file: File, 
    bucket: string = 'cloud-images',
    folder: string = 'original'
  ): Promise<ApiResponse<{ url: string; path: string }>> {
    try {
      // 验证文件
      if (!isValidImageFile(file)) {
        return {
          error: '不支持的文件类型或文件过大（最大10MB）',
          success: false
        };
      }

      // 创建FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('bucket', bucket);
      formData.append('folder', folder);

      console.log(`开始上传文件到 ${bucket}/${folder}`);

      // 通过JWT认证的后端API上传
      const response = await jwtUploadRequest<{ url: string; path: string }>(
        '/api/v2/storage/upload-image', 
        formData
      );

      if (response.success && response.data) {
        console.log('图片上传成功:', response.data.url);
        return response;
      } else {
        return {
          error: response.error || '图片上传失败',
          success: false
        };
      }

    } catch (error) {
      console.error('Upload image error:', error);
      return {
        error: error instanceof Error ? error.message : '上传失败',
        success: false
      };
    }
  },

  /**
   * 删除Storage中的图片（通过后端API）
   */
  async deleteImage(
    filePath: string,
    bucket: string = 'cloud-images'
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await jwtApiRequest<{ message: string }>(`/api/v2/storage/delete-image`, {
        method: 'DELETE',
        body: JSON.stringify({ filePath, bucket })
      });

      return response;

    } catch (error) {
      return {
        error: error instanceof Error ? error.message : '删除失败',
        success: false
      };
    }
  },

  /**
   * 获取图片的公共URL（通过后端API）
   */
  async getPublicUrl(filePath: string, bucket: string = 'cloud-images'): Promise<string> {
    try {
      const response = await jwtApiRequest<{ url: string }>('/api/v2/storage/public-url', {
        method: 'POST',
        body: JSON.stringify({ filePath, bucket })
      });

      return response.data?.url || '';
    } catch (error) {
      console.error('Get public URL error:', error);
      return '';
    }
  },

  // 提取图片EXIF信息
  extractExif: async (file: File): Promise<ApiResponse<ExifResponse>> => {
    const formData = new FormData();
    formData.append('file', file);
    
    return jwtUploadRequest<ExifResponse>('/api/v2/storage/extract-exif', formData);
  },
};

// ============== 工具函数 ==============
/**
 * 获取设备ID（用于匿名用户）
 */
export function getDeviceId(): string {
  if (typeof window === 'undefined') return '';
  
  let deviceId = localStorage.getItem('cloud_collector_device_id');
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('cloud_collector_device_id', deviceId);
  }
  return deviceId;
}

/**
 * 获取用户ID（如果已登录）
 */
export function getUserId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('cloud_collector_user_id');
}

/**
 * 设置用户ID
 */
export function setUserId(userId: string) {
  if (typeof window === 'undefined') return;
  localStorage.setItem('cloud_collector_user_id', userId);
}

/**
 * 通用 API 请求函数
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // 添加默认请求头
    const headers: Record<string, string> = {
      ...DEFAULT_HEADERS,
      ...(options.headers as Record<string, string>),
    };

    // 添加设备ID和用户ID到请求头
    const deviceId = getDeviceId();
    const userId = getUserId();
    
    if (deviceId) {
      headers['X-Device-ID'] = deviceId;
    }
    if (userId) {
      headers['X-User-ID'] = userId;
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return { data, success: true };
  } catch (error) {
    console.error('API Request Error:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      success: false,
    };
  }
}

/**
 * 文件上传请求函数
 */
async function uploadRequest<T>(
  endpoint: string,
  formData: FormData
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // 文件上传不需要设置 Content-Type，让浏览器自动设置
    const headers: Record<string, string> = {};

    // 添加设备ID和用户ID到请求头
    const deviceId = getDeviceId();
    const userId = getUserId();
    
    if (deviceId) {
      headers['X-Device-ID'] = deviceId;
    }
    if (userId) {
      headers['X-User-ID'] = userId;
    }

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return { data, success: true };
  } catch (error) {
    console.error('Upload Request Error:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      success: false,
    };
  }
}

// ============== 用户管理 API ==============
export const userAPI = {
  /**
   * 创建或获取用户
   */
  async createOrGetUser(request: UserCreateRequest): Promise<ApiResponse<User>> {
    return apiRequest<User>('/api/users', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * 获取用户信息
   */
  async getUser(userId: string): Promise<ApiResponse<User>> {
    return apiRequest<User>(`/api/users/${userId}`);
  },
};

// ============== 捕云工具 API ==============
export const captureToolAPI = {
  /**
   * 获取所有捕云工具
   */
  async getCaptureTools(): Promise<ApiResponse<CaptureTool[]>> {
    return apiRequest<CaptureTool[]>('/api/capture-tools');
  },

  /**
   * 获取指定捕云工具
   */
  async getCaptureTool(toolId: string): Promise<ApiResponse<CaptureTool>> {
    return apiRequest<CaptureTool>(`/api/capture-tools/${toolId}`);
  },
};

// ============== JWT认证版本的云朵收藏API ==============
export const cloudCollectionAPI = {
  /**
   * 创建云朵收藏记录（JWT认证版本）
   */
  async createCloudCollection(request: CloudCollectionCreateRequest): Promise<ApiResponse<CloudCollectionResponse>> {
    return jwtApiRequest<CloudCollectionResponse>('/api/v2/cloud-collections', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * 获取我的云朵收藏列表（JWT认证版本）
   */
  async getMyCollections(
    page: number = 1,
    pageSize: number = 20,
    toolId?: string,
    isFavorite?: boolean
  ): Promise<ApiResponse<CloudCollectionListResponse>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    
    if (toolId) params.append('tool_id', toolId);
    if (isFavorite !== undefined) params.append('is_favorite', isFavorite.toString());
    
    return jwtApiRequest<CloudCollectionListResponse>(`/api/v2/my-collections?${params}`);
  },

  /**
   * 切换收藏状态（JWT认证版本）
   */
  async toggleFavorite(collectionId: string): Promise<ApiResponse<{ message: string; is_favorite: boolean }>> {
    return jwtApiRequest<{ message: string; is_favorite: boolean }>(`/api/v2/cloud-collections/${collectionId}/favorite`, {
      method: 'PATCH',
    });
  },

  /**
   * 删除云朵收藏（JWT认证版本）
   */
  async deleteCollection(collectionId: string): Promise<ApiResponse<{ message: string }>> {
    return jwtApiRequest<{ message: string }>(`/api/v2/cloud-collections/${collectionId}`, {
      method: 'DELETE',
    });
  },

  /**
   * 从上传的图片创建完整的云朵收藏记录（JWT认证版本）
   */
  async createFromImageUpload(
    file: File,
    tool: string,
    context: {
      time?: string;
      location?: string;
      weather?: string;
      latitude?: number;
      longitude?: number;
    } = {}
  ): Promise<ApiResponse<CloudCollectionResponse>> {
    try {
      console.log('=== JWT API调用：createFromImageUpload ===');
      console.log('文件:', {
        name: file.name,
        type: file.type,
        size: file.size
      });
      console.log('工具:', tool);
      console.log('上下文:', context);
      
      const formData = new FormData();
      formData.append('file', file);
      formData.append('tool', tool);
      if (context.time) formData.append('time', context.time);
      if (context.location) formData.append('location', context.location);
      if (context.weather) formData.append('weather', context.weather);
      if (context.latitude !== undefined) formData.append('latitude', context.latitude.toString());
      if (context.longitude !== undefined) formData.append('longitude', context.longitude.toString());

      console.log('FormData内容:');
      for (let [key, value] of formData.entries()) {
        console.log(`  ${key}:`, value);
      }

      const result = await jwtUploadRequest<CloudCollectionResponse>('/api/v2/cloud/create-from-image-upload', formData);
      console.log('JWT API调用结果:', result);
      console.log('=== JWT API调用结束 ===');
      
      return result;
    } catch (error) {
      console.error('JWT API调用失败:', error);
      return {
        error: error instanceof Error ? error.message : '创建云朵收藏失败',
        success: false
      };
    }
  }
};

// ============== JWT认证请求函数 ==============

/**
 * JWT认证的API请求函数
 */
async function jwtApiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // 获取JWT Token
    const token = await getJWTToken();
    if (!token) {
      return {
        error: '用户未登录，请先登录',
        success: false
      };
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...((options.headers as Record<string, string>) || {}),
    };

    const response = await fetch(url, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return { data, success: true };
  } catch (error) {
    console.error('JWT API Request Error:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      success: false,
    };
  }
}

/**
 * JWT认证的文件上传请求函数
 */
async function jwtUploadRequest<T>(
  endpoint: string,
  formData: FormData
): Promise<ApiResponse<T>> {
  try {
    const url = `${API_BASE_URL}${endpoint}`;
    
    // 获取JWT Token
    const token = await getJWTToken();
    if (!token) {
      return {
        error: '用户未登录，请先登录',
        success: false
      };
    }

    // 文件上传不需要设置 Content-Type，让浏览器自动设置
    const headers: Record<string, string> = {
      'Authorization': `Bearer ${token}`,
    };

    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();
    return { data, success: true };
  } catch (error) {
    console.error('JWT Upload Request Error:', error);
    return {
      error: error instanceof Error ? error.message : 'Unknown error occurred',
      success: false,
    };
  }
}

/**
 * 获取JWT Token
 */
async function getJWTToken(): Promise<string | null> {
  try {
    // 从Supabase获取当前用户的JWT Token
    const { data: { session } } = await supabase.auth.getSession();
    return session?.access_token || null;
  } catch (error) {
    console.error('获取JWT Token失败:', error);
    return null;
  }
}

// ============== AI 相关 API ==============
export const aiAPI = {
  /**
   * 基于特征生成云朵名称
   */
  async generateCloudName(request: CloudNameRequest): Promise<ApiResponse<CloudNameResponse>> {
    return apiRequest<CloudNameResponse>('/api/cloud/name', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * 基于图像生成云朵名称
   */
  async generateCloudNameFromImage(request: CloudNameImageRequest): Promise<ApiResponse<CloudNameResponse>> {
    return apiRequest<CloudNameResponse>('/api/cloud/name-from-image', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * 基于特征生成云朵描述
   */
  async generateCloudDescription(request: CloudDescriptionRequest): Promise<ApiResponse<CloudDescriptionResponse>> {
    return apiRequest<CloudDescriptionResponse>('/api/cloud/description', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * 基于图像生成云朵描述
   */
  async generateCloudDescriptionFromImage(request: CloudDescriptionImageRequest): Promise<ApiResponse<CloudDescriptionResponse>> {
    return apiRequest<CloudDescriptionResponse>('/api/cloud/description-from-image', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * 分析云朵图像
   */
  async analyzeCloudImage(request: CloudAnalysisRequest): Promise<ApiResponse<CloudAnalysisResponse>> {
    return apiRequest<CloudAnalysisResponse>('/api/cloud/analyze', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  /**
   * 从上传文件生成云朵名称
   */
  async generateCloudNameFromUpload(
    file: File,
    tool: string,
    context: { time?: string; location?: string; weather?: string } = {}
  ): Promise<ApiResponse<CloudNameResponse>> {
    console.log('=== API调用：generateCloudNameFromUpload ===');
    console.log('文件:', {
      name: file.name,
      type: file.type,
      size: file.size
    });
    console.log('工具:', tool);
    console.log('上下文:', context);
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tool', tool);
    if (context.time) formData.append('time', context.time);
    if (context.location) formData.append('location', context.location);
    if (context.weather) formData.append('weather', context.weather);

    console.log('FormData内容:');
    for (let [key, value] of formData.entries()) {
      console.log(`  ${key}:`, value);
    }

    const result = await uploadRequest<CloudNameResponse>('/api/cloud/name-from-image-upload', formData);
    console.log('API调用结果:', result);
    console.log('=== API调用结束 ===');
    
    return result;
  },

  /**
   * 从上传文件生成云朵描述
   */
  async generateCloudDescriptionFromUpload(
    file: File,
    tool: string,
    context: { time?: string; location?: string; weather?: string; cloud_name?: string } = {}
  ): Promise<ApiResponse<CloudDescriptionResponse>> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('tool', tool);
    if (context.time) formData.append('time', context.time);
    if (context.location) formData.append('location', context.location);
    if (context.weather) formData.append('weather', context.weather);
    if (context.cloud_name) formData.append('cloud_name', context.cloud_name);

    return uploadRequest<CloudDescriptionResponse>('/api/cloud/description-from-image-upload', formData);
  },
};

// ============== 天气 API ==============
export const weatherAPI = {
  /**
   * 获取当前天气数据
   */
  async getCurrentWeather(latitude: number, longitude: number, units: string = 'metric'): Promise<ApiResponse<WeatherResponse>> {
    const params = new URLSearchParams({
      latitude: latitude.toString(),
      longitude: longitude.toString(),
      units,
    });
    
    return apiRequest<WeatherResponse>(`/api/weather/current?${params}`);
  },
};

// ============== 分享图片 API ==============
export const shareAPI = {
  /**
   * 生成分享图片
   */
  async generateShareImage(request: ShareImageRequest): Promise<ApiResponse<ShareImageResponse>> {
    return apiRequest<ShareImageResponse>('/api/share/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },
};

// ============== 工具函数 ==============
/**
 * 将文件转换为 base64 字符串
 */
export function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const result = reader.result as string;
      // 移除 data:image/jpeg;base64, 前缀
      const base64 = result.split(',')[1];
      resolve(base64);
    };
    reader.onerror = (error) => reject(error);
  });
}

/**
 * 获取当前位置
 */
export function getCurrentLocation(): Promise<{ latitude: number; longitude: number }> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocation is not supported by this browser.'));
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (error) => {
        reject(error);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000, // 5 minutes
      }
    );
  });
}

/**
 * 格式化日期时间
 */
export function formatDateTime(date: Date = new Date()): string {
  return date.toISOString();
}

/**
 * 检查是否为有效的图片文件
 */
export function isValidImageFile(file: File): boolean {
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/gif'];
  const maxSize = 10 * 1024 * 1024; // 10MB
  
  return validTypes.includes(file.type) && file.size <= maxSize;
} 

// ============== Supabase 客户端 ==============
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!;
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!;

export const supabase = createClient(supabaseUrl, supabaseAnonKey); 