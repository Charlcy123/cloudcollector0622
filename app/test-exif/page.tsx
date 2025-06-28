"use client"

import React, { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { storageAPI } from '@/utils/api'

export default function TestExifPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isExtracting, setIsExtracting] = useState(false)
  const [exifResult, setExifResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setExifResult(null)
      setError(null)
    }
  }

  const extractExif = async () => {
    if (!selectedFile) return

    setIsExtracting(true)
    setError(null)

    try {
      console.log('开始提取EXIF信息...')
      const result = await storageAPI.extractExif(selectedFile)
      
      console.log('EXIF提取结果:', result)
      
      if (result.success) {
        setExifResult(result.data)
      } else {
        setError(result.error || '提取失败')
      }
    } catch (err) {
      console.error('EXIF提取错误:', err)
      setError(err instanceof Error ? err.message : '未知错误')
    } finally {
      setIsExtracting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-200 via-sky-100 to-white p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-sky-800 text-center">EXIF 信息提取测试</h1>
        
        <Card className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                选择图片文件
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-sky-50 file:text-sky-700 hover:file:bg-sky-100"
              />
            </div>
            
            {selectedFile && (
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  已选择文件: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </p>
                
                <Button 
                  onClick={extractExif}
                  disabled={isExtracting}
                  className="w-full"
                >
                  {isExtracting ? '正在提取EXIF信息...' : '提取EXIF信息'}
                </Button>
              </div>
            )}
          </div>
        </Card>

        {error && (
          <Card className="p-4 bg-red-50 border-red-200">
            <div className="text-red-700">
              <h3 className="font-semibold">提取失败</h3>
              <p className="text-sm">{error}</p>
            </div>
          </Card>
        )}

        {exifResult && (
          <Card className="p-6">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">EXIF 提取结果</h2>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-700">GPS 信息</h3>
                <div className="bg-gray-50 p-3 rounded text-sm">
                  <p>有GPS信息: {exifResult.has_gps ? '是' : '否'}</p>
                  {exifResult.has_gps && exifResult.gps_info && (
                    <>
                      <p>纬度: {exifResult.gps_info.latitude}</p>
                      <p>经度: {exifResult.gps_info.longitude}</p>
                      <p>来源: {exifResult.gps_info.source}</p>
                    </>
                  )}
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-700">位置信息</h3>
                <div className="bg-gray-50 p-3 rounded text-sm">
                  {exifResult.location_info ? (
                    <>
                      <p>地址: {exifResult.location_info.address}</p>
                      <p>城市: {exifResult.location_info.city}</p>
                      <p>国家: {exifResult.location_info.country}</p>
                      <p>来源: {exifResult.location_info.source}</p>
                    </>
                  ) : (
                    <p>无位置信息</p>
                  )}
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-700">拍摄时间</h3>
                <div className="bg-gray-50 p-3 rounded text-sm">
                  <p>有拍摄时间: {exifResult.has_capture_time ? '是' : '否'}</p>
                  {exifResult.has_capture_time && exifResult.capture_time && (
                    <p>拍摄时间: {new Date(exifResult.capture_time).toLocaleString()}</p>
                  )}
                </div>
              </div>

              <div>
                <h3 className="font-medium text-gray-700">完整结果 (JSON)</h3>
                <pre className="bg-gray-50 p-3 rounded text-xs overflow-auto">
                  {JSON.stringify(exifResult, null, 2)}
                </pre>
              </div>
            </div>
          </Card>
        )}
      </div>
    </div>
  )
} 