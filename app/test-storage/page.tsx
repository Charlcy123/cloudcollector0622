'use client';

import React, { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Upload, CheckCircle, XCircle, Image as ImageIcon } from 'lucide-react';
import { storageAPI } from '@/utils/api';

export default function TestStoragePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{ url: string; path: string } | null>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setUploadResult(null);
      setError('');
      setSuccess('');
      
      // 创建预览URL
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setError('请先选择图片文件');
      return;
    }

    setIsUploading(true);
    setError('');
    setSuccess('');

    try {
      console.log('开始上传图片到Storage...');
      const result = await storageAPI.uploadImage(selectedFile, 'cloud-images', 'test');
      
      if (result.success && result.data) {
        setUploadResult(result.data);
        setSuccess(`图片上传成功！URL: ${result.data.url}`);
        console.log('上传成功:', result.data);
      } else {
        throw new Error(result.error || '上传失败');
      }
    } catch (error) {
      console.error('上传失败:', error);
      setError(error instanceof Error ? error.message : '上传失败');
    } finally {
      setIsUploading(false);
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    setPreviewUrl('');
    setUploadResult(null);
    setError('');
    setSuccess('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* 标题 */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">📤 Storage API 测试</h1>
        <p className="text-gray-600">测试图片上传到Supabase Storage功能</p>
      </div>

      {/* 文件选择区域 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            选择图片文件
          </CardTitle>
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
              <ImageIcon className="h-4 w-4" />
              选择图片
            </Button>
            {selectedFile && (
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">
                  {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                </span>
                <Button onClick={clearFile} variant="ghost" size="sm">
                  清除
                </Button>
              </div>
            )}
          </div>

          {previewUrl && (
            <div className="space-y-2">
              <h4 className="text-sm font-medium">预览:</h4>
              <img
                src={previewUrl}
                alt="预览"
                className="w-full max-w-md mx-auto rounded-lg shadow-md"
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* 上传控制 */}
      <Card>
        <CardHeader>
          <CardTitle>上传控制</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Button
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className="w-full"
          >
            {isUploading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                上传中...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                上传到Storage
              </>
            )}
          </Button>

          {error && (
            <Alert variant="destructive">
              <XCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert>
              <CheckCircle className="h-4 w-4" />
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* 上传结果 */}
      {uploadResult && (
        <Card>
          <CardHeader>
            <CardTitle className="text-green-600">✅ 上传成功</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div>
                <strong>公共URL:</strong>
                <a 
                  href={uploadResult.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="ml-2 text-blue-600 hover:underline break-all"
                >
                  {uploadResult.url}
                </a>
              </div>
              <div>
                <strong>文件路径:</strong> 
                <span className="ml-2 font-mono text-sm">{uploadResult.path}</span>
              </div>
            </div>

            <div className="space-y-2">
              <h4 className="text-sm font-medium">Storage中的图片:</h4>
              <img
                src={uploadResult.url}
                alt="Storage中的图片"
                className="w-full max-w-md mx-auto rounded-lg shadow-md border"
                onError={(e) => {
                  console.error('图片加载失败');
                  e.currentTarget.style.display = 'none';
                }}
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* 说明信息 */}
      <Card>
        <CardHeader>
          <CardTitle>说明</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
            <li>此页面用于测试图片上传到Supabase Storage的功能</li>
            <li>图片会上传到 <code>cloud-images</code> bucket的 <code>test</code> 文件夹</li>
            <li>上传成功后会显示公共URL，可以直接访问</li>
            <li>支持的格式：JPEG, PNG, WebP, GIF</li>
            <li>最大文件大小：10MB</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  );
} 