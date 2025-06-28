import React, { useRef, useState, useEffect } from 'react';
import { Camera, X, RotateCcw, Check } from 'lucide-react';

interface CameraCaptureProps {
  onCapture: (file: File) => void;
  onClose: () => void;
}

export default function CameraCapture({ onCapture, onClose }: CameraCaptureProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [facingMode, setFacingMode] = useState<'user' | 'environment'>('environment');

  // 初始化摄像头
  useEffect(() => {
    initCamera();
    return () => {
      // 清理摄像头资源
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
    };
  }, [facingMode]);

  const initCamera = async () => {
    try {
      setIsLoading(true);
      setError('');

      // 停止之前的流
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }

      // 请求摄像头权限
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: facingMode,
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        },
        audio: false
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }

      setIsLoading(false);
    } catch (err) {
      console.error('摄像头初始化失败:', err);
      setError('无法访问摄像头，请检查权限设置');
      setIsLoading(false);
    }
  };

  // 拍照
  const takePhoto = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!ctx) return;

    // 设置canvas尺寸
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // 绘制当前视频帧到canvas
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // 获取图片数据
    const imageDataUrl = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImage(imageDataUrl);
  };

  // 确认使用拍摄的照片
  const confirmPhoto = () => {
    if (!capturedImage || !canvasRef.current) return;
    
    // 将canvas内容转换为File对象
    canvasRef.current.toBlob((blob) => {
      if (blob) {
        const file = new File([blob], `cloud-photo-${Date.now()}.jpg`, {
          type: 'image/jpeg'
        });
        
        // 添加调试信息
        console.log('摄像头拍摄的文件信息:', {
          name: file.name,
          type: file.type,
          size: file.size,
          lastModified: file.lastModified
        });
        
        onCapture(file);
      }
    }, 'image/jpeg', 0.8);
  };

  // 重新拍照
  const retakePhoto = () => {
    setCapturedImage(null);
  };

  // 切换前后摄像头
  const switchCamera = async () => {
    setFacingMode(prev => prev === 'user' ? 'environment' : 'user');
  };

  return (
    <div className="fixed inset-0 bg-black z-50 flex flex-col">
      {/* 顶部工具栏 */}
      <div className="flex justify-between items-center p-4 bg-black/50 text-white">
        <button
          onClick={onClose}
          className="p-2 rounded-full hover:bg-white/20 transition-colors"
        >
          <X className="w-6 h-6" />
        </button>

        <h2 className="text-lg font-semibold">拍摄云朵</h2>

        <button
          onClick={switchCamera}
          className="p-2 rounded-full hover:bg-white/20 transition-colors"
          disabled={isLoading}
        >
          <RotateCcw className="w-6 h-6" />
        </button>
      </div>

      {/* 摄像头视图区域 */}
      <div className="flex-1 relative overflow-hidden">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-black">
            <div className="text-white text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
              <p>正在启动摄像头...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-black">
            <div className="bg-white rounded-lg p-6 m-4 max-w-sm">
              <div className="text-center">
                <p className="text-red-600 mb-4">{error}</p>
                <button
                  onClick={initCamera}
                  className="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
                >
                  重试
                </button>
              </div>
            </div>
          </div>
        )}

        {capturedImage ? (
          <div className="w-full h-full flex items-center justify-center bg-black">
            <img
              src={capturedImage}
              alt="拍摄的照片"
              className="max-w-full max-h-full object-contain"
            />
          </div>
        ) : (
          <video
            ref={videoRef}
            className="w-full h-full object-cover"
            playsInline
            muted
          />
        )}

        {/* 隐藏的canvas用于拍照 */}
        <canvas ref={canvasRef} className="hidden" />
      </div>

      {/* 底部控制区域 */}
      <div className="p-6 bg-black/50">
        {capturedImage ? (
          <div className="flex justify-center gap-4">
            <button
              onClick={retakePhoto}
              className="px-8 py-3 border-2 border-white text-white rounded-lg hover:bg-white/20 transition-colors"
            >
              重拍
            </button>
            <button
              onClick={confirmPhoto}
              className="px-8 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors flex items-center"
            >
              <Check className="w-5 h-5 mr-2" />
              确认使用
            </button>
          </div>
        ) : (
          <div className="flex justify-center">
            <button
              onClick={takePhoto}
              disabled={isLoading || !!error}
              className="w-20 h-20 rounded-full bg-white hover:bg-gray-100 text-black transition-colors flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Camera className="w-8 h-8" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
} 