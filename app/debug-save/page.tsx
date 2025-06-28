'use client';

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Upload, CheckCircle, XCircle } from 'lucide-react';

// 导入API函数
import {
  cloudCollectionAPI,
  captureToolAPI,
  userAPI,
  fileToBase64,
  getDeviceId,
  formatDateTime,
  isValidImageFile,
  type CloudCollectionCreateRequest,
  type User,
  type CaptureTool
} from '@/utils/api';

export default function DebugSavePage() {
  // 状态管理
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [captureTools, setCaptureTools] = useState<CaptureTool[]>([]);
  const [selectedTool, setSelectedTool] = useState<CaptureTool | null>(null);
  
  // 测试状态
  const [testSteps, setTestSteps] = useState<{[key: string]: 'pending' | 'success' | 'error'}>({});
  const [testResults, setTestResults] = useState<{[key: string]: any}>({});
  const [isRunning, setIsRunning] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 更新测试步骤状态
  const updateStep = (step: string, status: 'pending' | 'success' | 'error', result?: any) => {
    setTestSteps(prev => ({ ...prev, [step]: status }));
    if (result) {
      setTestResults(prev => ({ ...prev, [step]: result }));
    }
  };

  // 文件选择处理
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!isValidImageFile(file)) {
      alert('请选择有效的图片文件（JPEG、PNG、WebP、GIF，小于10MB）');
      return;
    }

    setSelectedFile(file);
    
    // 创建预览URL
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
    
    // 重置测试状态
    setTestSteps({});
    setTestResults({});
  };

  // 运行完整测试
  const runFullTest = async () => {
    if (!selectedFile) {
      alert('请先选择图片文件');
      return;
    }

    setIsRunning(true);
    
    try {
      // 步骤1: 初始化用户
      updateStep('user', 'pending');
      try {
        const deviceId = getDeviceId();
        const userResponse = await userAPI.createOrGetUser({
          device_id: deviceId,
          display_name: `调试用户_${deviceId.slice(-6)}`
        });
        
        if (userResponse.success && userResponse.data) {
          setCurrentUser(userResponse.data);
          updateStep('user', 'success', userResponse.data);
        } else {
          throw new Error(userResponse.error || '用户初始化失败');
        }
      } catch (error) {
        updateStep('user', 'error', error);
        return;
      }

      // 步骤2: 获取工具列表
      updateStep('tools', 'pending');
      try {
        const toolsResponse = await captureToolAPI.getCaptureTools();
        
        if (toolsResponse.success && toolsResponse.data) {
          setCaptureTools(toolsResponse.data);
          setSelectedTool(toolsResponse.data[0]); // 选择第一个工具
          updateStep('tools', 'success', toolsResponse.data);
        } else {
          throw new Error(toolsResponse.error || '获取工具失败');
        }
      } catch (error) {
        updateStep('tools', 'error', error);
        return;
      }

      // 步骤3: 转换图片为base64
      updateStep('base64', 'pending');
      try {
        const base64Result = await fileToBase64(selectedFile);
        updateStep('base64', 'success', {
          length: base64Result.length,
          sizeKB: Math.round(base64Result.length / 1024),
          preview: base64Result.substring(0, 100) + '...'
        });
      } catch (error) {
        updateStep('base64', 'error', error);
        return;
      }

      // 步骤4: 构建保存数据
      updateStep('prepare', 'pending');
      try {
        const imageUrl = await fileToBase64(selectedFile);
        const collectionData: CloudCollectionCreateRequest = {
          tool_id: captureTools[0].id,
          latitude: 31.2304,
          longitude: 121.4737,
          address: '测试地址 31.2304, 121.4737',
          city: '上海',
          country: '中国',
          original_image_url: imageUrl,
          cloud_name: '调试测试云朵',
          cloud_description: '这是一个用于调试保存功能的测试云朵',
          keywords: ['测试', '调试', '白云'],
          capture_time: formatDateTime(),
          weather_data: {
            main: '晴天',
            description: '万里无云',
            temperature: 25
          }
        };
        
        updateStep('prepare', 'success', {
          ...collectionData,
          image_preview: imageUrl.substring(0, 100) + '...'
        });
      } catch (error) {
        updateStep('prepare', 'error', error);
        return;
      }

      // 步骤5: 调用保存API
      updateStep('save', 'pending');
      try {
        const imageUrl = await fileToBase64(selectedFile);
        const collectionData: CloudCollectionCreateRequest = {
          tool_id: captureTools[0].id,
          latitude: 31.2304,
          longitude: 121.4737,
          address: '测试地址 31.2304, 121.4737',
          city: '上海',
          country: '中国',
          original_image_url: imageUrl,
          cloud_name: '调试测试云朵',
          cloud_description: '这是一个用于调试保存功能的测试云朵',
          keywords: ['测试', '调试', '白云'],
          capture_time: formatDateTime(),
          weather_data: {
            main: '晴天',
            description: '万里无云',
            temperature: 25
          }
        };

        const response = await cloudCollectionAPI.createCloudCollection(collectionData);
        
        if (response.success && response.data) {
          updateStep('save', 'success', response.data);
        } else {
          throw new Error(response.error || '保存失败');
        }
      } catch (error) {
        updateStep('save', 'error', error);
        return;
      }

    } finally {
      setIsRunning(false);
    }
  };

  // 渲染步骤状态
  const renderStepStatus = (step: string, label: string) => {
    const status = testSteps[step];
    const result = testResults[step];
    
    return (
      <Card className="mb-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-sm">
            {status === 'success' && <CheckCircle className="h-4 w-4 text-green-500" />}
            {status === 'error' && <XCircle className="h-4 w-4 text-red-500" />}
            {status === 'pending' && <Loader2 className="h-4 w-4 animate-spin text-blue-500" />}
            {!status && <div className="h-4 w-4 rounded-full border-2 border-gray-300" />}
            {label}
          </CardTitle>
        </CardHeader>
        {result && (
          <CardContent>
            <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-32">
              {typeof result === 'string' 
                ? result 
                : JSON.stringify(result, null, 2)
              }
            </pre>
          </CardContent>
        )}
      </Card>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* 标题 */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">🔧 保存功能调试工具</h1>
        <p className="text-gray-600">测试"保存到我的天空"功能的每个步骤</p>
      </div>

      {/* 文件上传区域 */}
      <Card>
        <CardHeader>
          <CardTitle>1. 选择测试图片</CardTitle>
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
              <Upload className="h-4 w-4" />
              选择图片
            </Button>
            {selectedFile && (
              <span className="text-sm text-gray-600">
                已选择: {selectedFile.name} ({Math.round(selectedFile.size / 1024)}KB)
              </span>
            )}
          </div>

          {previewUrl && (
            <div className="relative">
              <img
                src={previewUrl}
                alt="测试图片预览"
                className="w-full max-w-md mx-auto rounded-lg shadow-md"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* 测试控制 */}
      {selectedFile && (
        <Card>
          <CardHeader>
            <CardTitle>2. 运行调试测试</CardTitle>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={runFullTest} 
              disabled={isRunning}
              className="w-full"
            >
              {isRunning ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  测试进行中...
                </>
              ) : (
                '🚀 开始完整测试'
              )}
            </Button>
          </CardContent>
        </Card>
      )}

      {/* 测试步骤结果 */}
      {Object.keys(testSteps).length > 0 && (
        <div className="space-y-4">
          <h2 className="text-xl font-bold">📊 测试结果</h2>
          
          {renderStepStatus('user', '用户初始化')}
          {renderStepStatus('tools', '获取捕云工具')}
          {renderStepStatus('base64', '图片Base64转换')}
          {renderStepStatus('prepare', '准备保存数据')}
          {renderStepStatus('save', '调用保存API')}
        </div>
      )}

      {/* 用户信息显示 */}
      {currentUser && (
        <Card>
          <CardHeader>
            <CardTitle>👤 当前用户信息</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm space-y-1">
              <div>ID: {currentUser.id}</div>
              <div>设备ID: {currentUser.device_id}</div>
              <div>显示名称: {currentUser.display_name}</div>
              <div>匿名用户: {currentUser.is_anonymous ? '是' : '否'}</div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 使用说明 */}
      <Alert>
        <AlertDescription>
          <strong>使用说明：</strong>
          <ol className="list-decimal list-inside mt-2 space-y-1">
            <li>选择一张测试图片（建议小于2MB）</li>
            <li>点击"开始完整测试"按钮</li>
            <li>观察每个步骤的执行结果</li>
            <li>如果某个步骤失败，查看详细错误信息</li>
            <li>将错误信息反馈给开发者</li>
          </ol>
        </AlertDescription>
      </Alert>
    </div>
  );
} 