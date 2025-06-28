"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft, TestTube, Upload, Sparkles, Share2, Cloud, User, Wrench, AlertTriangle, Terminal, Loader2 } from "lucide-react"
import { useRouter } from "next/navigation"
import { 
  aiAPI, 
  shareAPI, 
  captureToolAPI, 
  userAPI, 
  weatherAPI,
  getDeviceId,
  getUserId,
  fileToBase64,
  isValidImageFile 
} from "@/utils/api"

export default function TestAPIPage() {
  const router = useRouter()
  const [results, setResults] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)

  const addResult = (title: string, data: any, success: boolean = true) => {
    const result = {
      id: Date.now(),
      title,
      data,
      success,
      timestamp: new Date().toLocaleString()
    }
    setResults(prev => [result, ...prev])
  }

  const clearResults = () => {
    setResults([])
  }

  // 测试用户API
  const testUserAPI = async () => {
    setIsLoading(true)
    try {
      const deviceId = getDeviceId()
      addResult("获取设备ID", { deviceId })

      const createUserResponse = await userAPI.createOrGetUser({
        device_id: deviceId,
        display_name: "测试用户"
      })
      addResult("创建/获取用户", createUserResponse)

      if (createUserResponse.success && createUserResponse.data) {
        const userId = createUserResponse.data.id
        const getUserResponse = await userAPI.getUser(userId)
        addResult("获取用户详情", getUserResponse)
      }
    } catch (error) {
      addResult("用户API测试失败", { error: (error as Error).message }, false)
    } finally {
      setIsLoading(false)
    }
  }

  // 测试捕云工具API
  const testCaptureToolAPI = async () => {
    setIsLoading(true)
    try {
      const toolsResponse = await captureToolAPI.getCaptureTools()
      addResult("获取捕云工具列表", toolsResponse)

      if (toolsResponse.success && toolsResponse.data && toolsResponse.data.length > 0) {
        const firstTool = toolsResponse.data[0]
        const toolResponse = await captureToolAPI.getCaptureTool(firstTool.id)
        addResult("获取单个捕云工具", toolResponse)
      }
    } catch (error) {
      addResult("捕云工具API测试失败", { error: (error as Error).message }, false)
    } finally {
      setIsLoading(false)
    }
  }

  // 测试天气API
  const testWeatherAPI = async () => {
    setIsLoading(true)
    try {
      // 使用北京的坐标
      const weatherResponse = await weatherAPI.getCurrentWeather(39.9042, 116.4074)
      addResult("获取天气数据", weatherResponse)
    } catch (error) {
      addResult("天气API测试失败", { error: (error as Error).message }, false)
    } finally {
      setIsLoading(false)
    }
  }

  // 测试AI API（需要图片）
  const testAIAPI = async () => {
    if (!selectedFile) {
      addResult("AI API测试失败", { error: "请先选择图片文件" }, false)
      return
    }

    if (!isValidImageFile(selectedFile)) {
      addResult("AI API测试失败", { error: "请选择有效的图片文件" }, false)
      return
    }

    setIsLoading(true)
    try {
      // 测试云朵命名
      const nameResponse = await aiAPI.generateCloudNameFromUpload(
        selectedFile,
        "broom",
        {
          time: new Date().toISOString(),
          location: "测试地点"
        }
      )
      addResult("AI云朵命名", nameResponse)

      // 测试云朵描述
      const descResponse = await aiAPI.generateCloudDescriptionFromUpload(
        selectedFile,
        "broom",
        {
          time: new Date().toISOString(),
          location: "测试地点",
          cloud_name: "测试云朵"
        }
      )
      addResult("AI云朵描述", descResponse)

      // 测试图片分析
      const base64 = await fileToBase64(selectedFile)
      const analysisResponse = await aiAPI.analyzeCloudImage({
        image: base64,
        options: {
          detectShape: true,
          detectColor: true,
          detectTexture: true
        }
      })
      addResult("AI图片分析", analysisResponse)

    } catch (error) {
      addResult("AI API测试失败", { error: (error as Error).message }, false)
    } finally {
      setIsLoading(false)
    }
  }

  // 测试分享API
  const testShareAPI = async () => {
    if (!selectedFile) {
      addResult("分享API测试失败", { error: "请先选择图片文件" }, false)
      return
    }

    setIsLoading(true)
    try {
      const base64 = await fileToBase64(selectedFile)
      const shareResponse = await shareAPI.generateShareImage({
        image_url: base64,
        cloud_name: "测试云朵",
        description: "这是一朵用于测试的云朵",
        tool_icon: "🔮",
        captured_at: new Date().toLocaleString('zh-CN'),
        location: "测试地点"
      })
      addResult("生成分享图片", shareResponse)
    } catch (error) {
      addResult("分享API测试失败", { error: (error as Error).message }, false)
    } finally {
      setIsLoading(false)
    }
  }

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      addResult("选择文件", { 
        name: file.name, 
        size: file.size, 
        type: file.type,
        isValid: isValidImageFile(file)
      })
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sky-200 via-sky-100 to-white">
      <div className="container mx-auto px-4 py-8">
        {/* 头部 */}
        <div className="flex items-center gap-4 mb-8">
          <Button variant="ghost" size="icon" onClick={() => router.back()}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div className="flex items-center gap-3">
            <TestTube className="w-6 h-6 text-sky-600" />
            <h1 className="text-2xl font-bold text-sky-800">API 功能测试</h1>
          </div>
        </div>

        {/* API状态提示 */}
        <div className="mb-6">
          <Card className="p-4 border-amber-200 bg-amber-50">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-amber-600 mt-0.5" />
              <div>
                <h3 className="font-semibold text-amber-800 mb-2">⚠️ API状态说明</h3>
                <div className="text-sm text-amber-700 space-y-1">
                  <p><strong>当前状态：</strong>AI API配额不足（余额：$0.00）</p>
                  <p><strong>影响功能：</strong>云朵命名、描述生成、图片分析</p>
                  <p><strong>降级机制：</strong>系统会自动使用Mock数据，保证功能正常运行</p>
                  <p><strong>解决方案：</strong>为 api.tu-zi.com 账户充值以恢复AI功能</p>
                </div>
              </div>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 左侧：测试控制面板 */}
          <div className="space-y-6">
            {/* 文件上传 */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5" />
                文件上传
              </h2>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="file-upload">选择图片文件（用于AI和分享API测试）</Label>
                  <Input
                    id="file-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="mt-1"
                  />
                </div>
                {selectedFile && (
                  <div className="text-sm text-gray-600">
                    已选择: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                  </div>
                )}
              </div>
            </Card>

            {/* 测试按钮 */}
            <Card className="p-6">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Wrench className="w-5 h-5" />
                API 测试
              </h2>
              <div className="grid grid-cols-1 gap-3">
                <Button 
                  onClick={testUserAPI} 
                  disabled={isLoading}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <User className="w-4 h-4 mr-2" />
                  测试用户API
                </Button>
                
                <Button 
                  onClick={testCaptureToolAPI} 
                  disabled={isLoading}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Wrench className="w-4 h-4 mr-2" />
                  测试捕云工具API
                </Button>
                
                <Button 
                  onClick={testWeatherAPI} 
                  disabled={isLoading}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Cloud className="w-4 h-4 mr-2" />
                  测试天气API
                </Button>
                
                <Button 
                  onClick={testAIAPI} 
                  disabled={isLoading || !selectedFile}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  测试AI API
                </Button>
                
                <Button 
                  onClick={testShareAPI} 
                  disabled={isLoading || !selectedFile}
                  className="w-full justify-start"
                  variant="outline"
                >
                  <Share2 className="w-4 h-4 mr-2" />
                  测试分享API
                </Button>
              </div>
            </Card>

            {/* 控制按钮 */}
            <Card className="p-6">
              <div className="flex gap-3">
                <Button onClick={clearResults} variant="outline" className="flex-1">
                  清空结果
                </Button>
                <Button 
                  onClick={() => window.open('http://localhost:8000/docs', '_blank')}
                  className="flex-1"
                >
                  查看API文档
                </Button>
              </div>
            </Card>
          </div>

          {/* 右侧：测试结果 */}
          <div className="space-y-4">
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <Terminal className="w-5 h-5" />
                  测试结果
                </h2>
                {isLoading && (
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    测试中...
                  </div>
                )}
              </div>

              {/* 描述显示测试区域 */}
              {results.some(r => r.title.includes('AI')) && (
                <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
                  <h3 className="font-semibold text-amber-800 mb-2">📝 描述完整性测试</h3>
                  <p className="text-sm text-amber-700 mb-3">
                    检查AI生成的描述是否完整显示（无截断）
                  </p>
                  {results
                    .filter(r => r.title.includes('AI') && r.data?.description)
                    .slice(0, 2)
                    .map((result, index) => (
                      <div key={index} className="mb-3 p-3 bg-white rounded border">
                        <div className="text-xs text-gray-500 mb-1">
                          {result.title} - 完整描述展示:
                        </div>
                        <div className="text-base leading-relaxed text-gray-800 whitespace-pre-wrap break-words">
                          {result.data.description}
                        </div>
                        <div className="text-xs text-gray-400 mt-1">
                          字符数: {result.data.description?.length || 0}
                        </div>
                      </div>
                    ))}
                </div>
              )}

              {/* 测试结果列表 */}
              <div className="max-h-96 overflow-y-auto space-y-3">
                {results.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">暂无测试结果</p>
                ) : (
                  results.map((result, index) => (
                    <div
                      key={index}
                      className={`p-3 rounded-lg border ${
                        result.success 
                          ? 'bg-green-50 border-green-200' 
                          : 'bg-red-50 border-red-200'
                      }`}
                    >
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-2 h-2 rounded-full ${
                          result.success ? 'bg-green-500' : 'bg-red-500'
                        }`} />
                        <span className="font-medium text-sm">{result.title}</span>
                        <span className="text-xs text-gray-500">{result.timestamp}</span>
                      </div>
                      <pre className="text-xs bg-gray-100 p-2 rounded overflow-x-auto">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </div>
                  ))
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
} 