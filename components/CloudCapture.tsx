'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Camera, Sparkles, MapPin, Cloud, Heart } from 'lucide-react';
import { useRouter } from 'next/navigation';

// 导入我们创建的API函数
import {
  aiAPI,
  captureToolAPI,
  weatherAPI,
  cloudCollectionAPI,
  getCurrentLocation,
  formatDateTime,
  isValidImageFile,
  getDeviceId,
  userAPI,
  fileToBase64,
  type CaptureTool,
  type CloudNameResponse,
  type CloudDescriptionResponse,
  type WeatherResponse,
  type User,
  storageAPI
} from '@/utils/api';
import { useAuth } from '@/contexts/AuthContext';
import { authenticatedFetch } from '@/lib/api';

interface CloudCaptureProps {
  className?: string;
}

export default function CloudCapture({ className = '' }: CloudCaptureProps) {
  // ============== 状态管理 ==============
  const { user } = useAuth()
  const router = useRouter()
  const [selectedTool, setSelectedTool] = useState<CaptureTool | null>(null);
  const [captureTools, setCaptureTools] = useState<CaptureTool[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  
  // AI 生成结果
  const [cloudName, setCloudName] = useState<CloudNameResponse | null>(null);
  const [cloudDescription, setCloudDescription] = useState<CloudDescriptionResponse | null>(null);
  const [weatherData, setWeatherData] = useState<WeatherResponse | null>(null);
  const [location, setLocation] = useState<{ latitude: number; longitude: number } | null>(null);
  const [locationInfo, setLocationInfo] = useState<{ address: string; city: string; country: string } | null>(null);
  
  // 加载状态
  const [isLoadingTools, setIsLoadingTools] = useState(false);
  const [isGeneratingName, setIsGeneratingName] = useState(false);
  const [isGeneratingDescription, setIsGeneratingDescription] = useState(false);
  const [isGettingWeather, setIsGettingWeather] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // 错误状态
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  
  // 引用
  const fileInputRef = useRef<HTMLInputElement>(null);

  // ============== 初始化 ==============
  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // 获取捕云工具列表
      await loadCaptureTools();
      
      // 获取当前位置和天气
      await getCurrentLocationAndWeather();
    } catch (error) {
      console.error('App initialization error:', error);
      setError('应用初始化失败，请刷新页面重试');
    }
  };

  const loadCaptureTools = async () => {
    setIsLoadingTools(true);
    try {
      const response = await captureToolAPI.getCaptureTools();
      if (response.success && response.data) {
        setCaptureTools(response.data);
        // 默认选择第一个工具
        if (response.data.length > 0) {
          setSelectedTool(response.data[0]);
        }
      } else {
        setError(response.error || '获取捕云工具失败');
      }
    } catch (error) {
      setError('获取捕云工具失败，请稍后重试');
    } finally {
      setIsLoadingTools(false);
    }
  };

  const getCurrentLocationAndWeather = async () => {
    setIsGettingWeather(true);
    try {
      const position = await getCurrentLocation();
      setLocation(position);
      
      const weatherResponse = await weatherAPI.getCurrentWeather(
        position.latitude,
        position.longitude
      );
      
      if (weatherResponse.success && weatherResponse.data) {
        setWeatherData(weatherResponse.data);
        // 保存地点信息
        setLocationInfo(weatherResponse.data.location_info);
        console.log('获取到的地点信息:', weatherResponse.data.location_info);
      }
    } catch (error) {
      console.warn('获取位置或天气信息失败:', error);
      // 这不是致命错误，继续执行
    } finally {
      setIsGettingWeather(false);
    }
  };

  // ============== 文件处理 ==============
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // 验证文件
    if (!isValidImageFile(file)) {
      setError('请选择有效的图片文件（JPEG、PNG、WebP、GIF，小于10MB）');
      return;
    }

    setSelectedFile(file);
    setError('');
    setSuccess('');
    
    // 重置之前的结果
    setCloudName(null);
    setCloudDescription(null);

    // 创建预览URL
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const clearFile = () => {
    setSelectedFile(null);
    setPreviewUrl('');
    setCloudName(null);
    setCloudDescription(null);
    setError('');
    setSuccess('');
    
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // ============== AI 功能 ==============
  const generateCloudName = async () => {
    if (!selectedFile || !selectedTool) {
      setError('请选择图片和捕云工具');
      return;
    }

    setIsGeneratingName(true);
    setError('');

    try {
      const context = {
        time: formatDateTime(),
        location: location ? `纬度${location.latitude.toFixed(4)}, 经度${location.longitude.toFixed(4)}` : '未知位置',
        weather: weatherData?.weather.description
      };

      const response = await aiAPI.generateCloudNameFromUpload(
        selectedFile,
        selectedTool.id,
        context
      );

      if (response.success && response.data) {
        setCloudName(response.data);
        setSuccess('✨ 云朵名称生成成功！');
      } else {
        setError(response.error || '生成云朵名称失败');
      }
    } catch (error) {
      setError('生成云朵名称时发生错误，请稍后重试');
    } finally {
      setIsGeneratingName(false);
    }
  };

  const generateCloudDescription = async () => {
    if (!selectedFile || !selectedTool) {
      setError('请选择图片和捕云工具');
      return;
    }

    setIsGeneratingDescription(true);
    setError('');

    try {
      const context = {
        time: formatDateTime(),
        location: locationInfo?.address || (location ? `纬度${location.latitude.toFixed(4)}, 经度${location.longitude.toFixed(4)}` : '未知位置'),
        weather: weatherData?.weather.description,
        cloud_name: cloudName?.name
      };

      const response = await aiAPI.generateCloudDescriptionFromUpload(
        selectedFile,
        selectedTool.id,
        context
      );

      if (response.success && response.data) {
        setCloudDescription(response.data);
        setSuccess('📝 云朵描述生成成功！');
      } else {
        setError(response.error || '生成云朵描述失败');
      }
    } catch (error) {
      setError('生成云朵描述时发生错误，请稍后重试');
    } finally {
      setIsGeneratingDescription(false);
    }
  };

  // ============== 保存收藏 ==============
  const saveCloudCollection = async () => {
    if (!selectedFile || !cloudName || !user || !selectedTool || !location) {
      setError('请确保已选择图片、生成云朵名称，并获取位置信息');
      return;
    }

    setIsSaving(true);
    setError('');

    try {
      console.log('开始保存云朵收藏...');

      // 第一步：上传图片到Supabase Storage
      console.log('正在上传图片到Storage...');
      const uploadResult = await storageAPI.uploadImage(selectedFile, 'cloud-images', 'original');
      
      if (!uploadResult.success || !uploadResult.data) {
        throw new Error(uploadResult.error || '图片上传失败');
      }

      console.log('图片上传成功:', uploadResult.data.url);

      // 第二步：准备收藏数据（使用Storage URL而不是base64）
      const collectionData = {
        tool_id: selectedTool.id,
        latitude: location.latitude,
        longitude: location.longitude,
        address: locationInfo?.address || `位置 ${location.latitude.toFixed(4)}, ${location.longitude.toFixed(4)}`,
        city: locationInfo?.city || '未知城市',
        country: locationInfo?.country || '中国',
        original_image_url: uploadResult.data.url, // 使用Storage URL
        cloud_name: cloudName.name,
        cloud_description: cloudDescription?.description,
        keywords: cloudDescription?.keywords || [],
        capture_time: formatDateTime(),
        weather_data: weatherData ? {
          main: weatherData.weather.main,
          description: weatherData.weather.description,
          temperature: weatherData.weather.temperature
        } : undefined
      };

      console.log('准备保存云朵收藏:', {
        tool_id: collectionData.tool_id,
        cloud_name: collectionData.cloud_name,
        image_url: uploadResult.data.url,
        user_id: user.id,
        location: `${location.latitude}, ${location.longitude}`
      });

      // 第三步：使用JWT认证的API保存到数据库
      const response = await authenticatedFetch('/api/v2/cloud-collections', {
        method: 'POST',
        body: JSON.stringify(collectionData)
      });

      console.log('保存请求发送完成');
      console.log('响应状态:', response.status);
      console.log('响应状态文本:', response.statusText);
      console.log('响应头:', Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        const errorText = await response.text();
        console.error('保存失败，响应内容:', errorText);
        throw new Error(`保存失败: ${response.status} - ${errorText}`);
      }

      const savedCollection = await response.json();
      console.log('=== 保存成功详情 ===');
      console.log('保存成功的完整响应:', savedCollection);
      console.log('保存的用户ID:', user.id);
      console.log('保存的用户邮箱:', user.email);
      console.log('保存的云朵名称:', cloudName.name);
      console.log('保存时间:', new Date().toISOString());
      console.log('保存的收藏ID:', savedCollection.id);
      console.log('===================');
      setSuccess('云朵已成功保存到你的天空！✨ 正在跳转到收藏页面...');
      
      // 保存成功后，延迟跳转到收藏页面
      setTimeout(() => {
        router.push('/collection');
      }, 1500);
      
    } catch (error) {
      console.error('保存云朵收藏失败:', error);
      setError(error instanceof Error ? error.message : '保存失败，请稍后重试');
    } finally {
      setIsSaving(false);
    }
  };

  // ============== 渲染 ==============
  return (
    <div className={`max-w-4xl mx-auto p-6 space-y-6 ${className}`}>
      {/* 标题区域 */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold flex items-center justify-center gap-2">
          <Cloud className="h-8 w-8 text-blue-500" />
          云彩收集手册
        </h1>
        <p className="text-gray-600">用AI为你的云朵起名字，记录天空中的美好瞬间</p>
      </div>

      {/* 用户信息 */}
      {user && (
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-sm text-gray-600">
              <span>👋 欢迎，{user.email}</span>
              {weatherData && (
                <>
                  <span>•</span>
                  <MapPin className="h-4 w-4" />
                  <span>{weatherData.weather.description} {weatherData.weather.temperature}°C</span>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* 捕云工具选择 */}
      <Card>
        <CardHeader>
          <CardTitle>选择你的捕云工具</CardTitle>
          <CardDescription>每种工具都有独特的命名风格</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoadingTools ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-6 w-6 animate-spin" />
              <span className="ml-2">加载捕云工具中...</span>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {captureTools.map((tool) => (
                <Button
                  key={tool.id}
                  variant={selectedTool?.id === tool.id ? "default" : "outline"}
                  className="h-auto p-4 flex flex-col items-center gap-2"
                  onClick={() => setSelectedTool(tool)}
                >
                  <span className="text-2xl">{tool.emoji}</span>
                  <span className="text-sm font-medium">{tool.name}</span>
                  <span className="text-xs text-gray-500 text-center">{tool.description}</span>
                </Button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* 图片上传区域 */}
      <Card>
        <CardHeader>
          <CardTitle>上传云朵图片</CardTitle>
          <CardDescription>选择一张包含云朵的照片</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <Button
              onClick={() => fileInputRef.current?.click()}
              variant="outline"
              className="flex items-center gap-2"
            >
              <Camera className="h-4 w-4" />
              选择图片
            </Button>
            {selectedFile && (
              <Button onClick={clearFile} variant="ghost" size="sm">
                清除
              </Button>
            )}
          </div>

          {previewUrl && (
            <div className="relative">
              <img
                src={previewUrl}
                alt="云朵预览"
                className="w-full max-w-md mx-auto rounded-lg shadow-md"
              />
              <Badge className="absolute top-2 right-2 bg-green-500">
                {selectedFile?.name}
              </Badge>
            </div>
          )}
        </CardContent>
      </Card>

      {/* AI 生成区域 */}
      {selectedFile && selectedTool && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-yellow-500" />
              AI 云朵命名
            </CardTitle>
            <CardDescription>
              使用 {selectedTool.name} {selectedTool.emoji} 的风格为云朵起名
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* 生成名称 */}
            <div className="space-y-2">
              <Button
                onClick={generateCloudName}
                disabled={isGeneratingName}
                className="w-full sm:w-auto"
              >
                {isGeneratingName ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    正在生成名称...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-4 w-4 mr-2" />
                    生成云朵名称
                  </>
                )}
              </Button>

              {cloudName && (
                <Card className="bg-blue-50">
                  <CardContent className="pt-4">
                    <div className="space-y-2">
                      <h3 className="font-semibold text-lg">{cloudName.name}</h3>
                      <p className="text-gray-600">{cloudName.description}</p>
                      <Badge variant="secondary">{cloudName.style} 风格</Badge>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* 生成描述 */}
            <div className="space-y-2">
              <Button
                onClick={generateCloudDescription}
                disabled={isGeneratingDescription}
                variant="outline"
                className="w-full sm:w-auto"
              >
                {isGeneratingDescription ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    正在生成描述...
                  </>
                ) : (
                  <>
                    📝 生成详细描述
                  </>
                )}
              </Button>

              {cloudDescription && (
                <Card className="bg-green-50">
                  <CardContent className="pt-4">
                    <div className="space-y-2">
                      <p className="text-gray-700">{cloudDescription.description}</p>
                      {cloudDescription.keywords.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {cloudDescription.keywords.map((keyword, index) => (
                            <Badge key={index} variant="outline" className="text-xs">
                              {keyword}
                            </Badge>
                          ))}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* 保存收藏 */}
            {cloudName && (
              <Button
                onClick={saveCloudCollection}
                disabled={isSaving}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    保存中...
                  </>
                ) : (
                  <>
                    <Heart className="h-4 w-4 mr-2" />
                    保存到我的收藏
                  </>
                )}
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* 错误和成功提示 */}
      {error && (
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-700">{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <AlertDescription className="text-green-700">{success}</AlertDescription>
        </Alert>
      )}

      {/* 天气信息显示 */}
      {isGettingWeather && (
        <div className="text-center text-sm text-gray-500">
          <Loader2 className="h-4 w-4 animate-spin inline mr-2" />
          获取天气信息中...
        </div>
      )}

      {/* 天气和位置信息 */}
      {(weatherData || locationInfo) && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MapPin className="h-4 w-4" />
              当前环境
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {locationInfo && (
              <div className="flex items-center gap-2 text-sm">
                <MapPin className="h-3 w-3 text-gray-500" />
                <span className="text-gray-600">地点:</span>
                <span className="font-medium">{locationInfo.city}</span>
                <span className="text-gray-400 text-xs">({locationInfo.address})</span>
              </div>
            )}
            {weatherData && (
              <div className="flex items-center gap-2 text-sm">
                <Cloud className="h-3 w-3 text-blue-500" />
                <span className="text-gray-600">天气:</span>
                <span className="font-medium">{weatherData.weather.description}</span>
                <span className="text-blue-600">{weatherData.weather.temperature}°C</span>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
} 