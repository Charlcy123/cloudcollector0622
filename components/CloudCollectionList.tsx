'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Loader2, 
  Heart, 
  MapPin, 
  Calendar, 
  Eye, 
  Trash2, 
  Filter,
  Grid,
  List,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

// 导入API函数
import {
  cloudCollectionAPI,
  captureToolAPI,
  userAPI,
  getDeviceId,
  type CloudCollection,
  type CloudCollectionListResponse,
  type CaptureTool,
  type User
} from '@/utils/api';

interface CloudCollectionListProps {
  className?: string;
  userId?: string; // 可选的用户ID，如果不提供则使用当前用户
}

export default function CloudCollectionList({ className = '', userId }: CloudCollectionListProps) {
  // ============== 状态管理 ==============
  const [collections, setCollections] = useState<CloudCollection[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [captureTools, setCaptureTools] = useState<CaptureTool[]>([]);
  
  // 分页和筛选状态
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [pageSize] = useState(12);
  const [selectedToolId, setSelectedToolId] = useState<string>('');
  const [showFavoritesOnly, setShowFavoritesOnly] = useState(false);
  
  // UI 状态
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  // ============== 初始化 ==============
  useEffect(() => {
    initializeComponent();
  }, [userId]);

  useEffect(() => {
    if (currentUser) {
      loadCollections();
    }
  }, [currentUser, currentPage, selectedToolId, showFavoritesOnly]);

  const initializeComponent = async () => {
    try {
      // 初始化用户
      if (userId) {
        const userResponse = await userAPI.getUser(userId);
        if (userResponse.success && userResponse.data) {
          setCurrentUser(userResponse.data);
        }
      } else {
        // 使用当前设备用户
        const deviceId = getDeviceId();
        const userResponse = await userAPI.createOrGetUser({
          device_id: deviceId,
          display_name: `云朵收集者_${deviceId.slice(-6)}`
        });
        if (userResponse.success && userResponse.data) {
          setCurrentUser(userResponse.data);
        }
      }

      // 加载捕云工具列表（用于筛选）
      const toolsResponse = await captureToolAPI.getCaptureTools();
      if (toolsResponse.success && toolsResponse.data) {
        setCaptureTools(toolsResponse.data);
      }
    } catch (error) {
      console.error('Component initialization error:', error);
      setError('初始化失败，请刷新页面重试');
    }
  };

  const loadCollections = async () => {
    if (!currentUser) return;

    setIsLoading(true);
    setError('');

    try {
      const params = {
        page: currentPage,
        page_size: pageSize,
        tool_id: selectedToolId || undefined,
        is_favorite: showFavoritesOnly || undefined
      };

      const response = await cloudCollectionAPI.getUserCloudCollections(
        currentUser.id,
        params
      );

      if (response.success && response.data) {
        setCollections(response.data.collections);
        setTotalCount(response.data.total);
        setTotalPages(Math.ceil(response.data.total / pageSize));
      } else {
        setError(response.error || '加载收藏列表失败');
      }
    } catch (error) {
      setError('加载收藏列表时发生错误，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  // ============== 操作函数 ==============
  const toggleFavorite = async (collectionId: string) => {
    try {
      const response = await cloudCollectionAPI.toggleFavorite(collectionId);
      if (response.success && response.data) {
        // 更新本地状态
        setCollections(prev => 
          prev.map(collection => 
            collection.id === collectionId 
              ? { ...collection, is_favorite: response.data!.is_favorite }
              : collection
          )
        );
        setSuccess(response.data.is_favorite ? '已添加到收藏' : '已取消收藏');
        setTimeout(() => setSuccess(''), 2000);
      } else {
        setError(response.error || '操作失败');
      }
    } catch (error) {
      setError('操作失败，请稍后重试');
    }
  };

  const deleteCollection = async (collectionId: string) => {
    if (!confirm('确定要删除这个云朵收藏吗？此操作无法撤销。')) {
      return;
    }

    try {
      const response = await cloudCollectionAPI.deleteCloudCollection(collectionId);
      if (response.success) {
        // 从本地状态中移除
        setCollections(prev => prev.filter(collection => collection.id !== collectionId));
        setTotalCount(prev => prev - 1);
        setSuccess('删除成功');
        setTimeout(() => setSuccess(''), 2000);
      } else {
        setError(response.error || '删除失败');
      }
    } catch (error) {
      setError('删除失败，请稍后重试');
    }
  };

  // ============== 筛选和分页 ==============
  const handleToolFilter = (toolId: string) => {
    setSelectedToolId(toolId);
    setCurrentPage(1); // 重置到第一页
  };

  const handleFavoriteFilter = () => {
    setShowFavoritesOnly(!showFavoritesOnly);
    setCurrentPage(1); // 重置到第一页
  };

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
  };

  // ============== 工具函数 ==============
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getToolInfo = (toolId: string) => {
    return captureTools.find(tool => tool.id === toolId);
  };

  // ============== 渲染组件 ==============
  const renderCollectionCard = (collection: CloudCollection) => {
    const toolInfo = getToolInfo(collection.tool_id);
    
    return (
      <Card key={collection.id} className="overflow-hidden hover:shadow-lg transition-shadow">
        <div className="relative">
          {collection.original_image_url && (
            <img
              src={collection.original_image_url}
              alt={collection.cloud_name}
              className="w-full h-48 object-cover"
            />
          )}
          <div className="absolute top-2 right-2 flex gap-1">
            <Button
              size="sm"
              variant="secondary"
              className="h-8 w-8 p-0 bg-white/80 hover:bg-white"
              onClick={() => toggleFavorite(collection.id)}
            >
              <Heart 
                className={`h-4 w-4 ${collection.is_favorite ? 'fill-red-500 text-red-500' : 'text-gray-600'}`} 
              />
            </Button>
            <Button
              size="sm"
              variant="secondary"
              className="h-8 w-8 p-0 bg-white/80 hover:bg-white text-red-600"
              onClick={() => deleteCollection(collection.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        <CardContent className="p-4">
          <div className="space-y-3">
            {/* 云朵名称和工具 */}
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-lg leading-tight">{collection.cloud_name}</h3>
                {toolInfo && (
                  <div className="flex items-center gap-1 mt-1">
                    <span className="text-sm">{toolInfo.emoji}</span>
                    <span className="text-xs text-gray-500">{toolInfo.name}</span>
                  </div>
                )}
              </div>
              <div className="flex items-center gap-1 text-xs text-gray-500">
                <Eye className="h-3 w-3" />
                {collection.view_count}
              </div>
            </div>

            {/* 描述 */}
            {collection.cloud_description && (
              <p className="text-sm text-gray-600 line-clamp-2">
                {collection.cloud_description}
              </p>
            )}

            {/* 关键词 */}
            {collection.keywords.length > 0 && (
              <div className="flex flex-wrap gap-1">
                {collection.keywords.slice(0, 3).map((keyword, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {keyword}
                  </Badge>
                ))}
                {collection.keywords.length > 3 && (
                  <Badge variant="outline" className="text-xs">
                    +{collection.keywords.length - 3}
                  </Badge>
                )}
              </div>
            )}

            {/* 时间和地点 */}
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {formatDate(collection.capture_time)}
              </div>
              {collection.location && (
                <div className="flex items-center gap-1">
                  <MapPin className="h-3 w-3" />
                  <span className="truncate max-w-20">
                    {collection.location.city || '未知地点'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  const renderCollectionList = (collection: CloudCollection) => {
    const toolInfo = getToolInfo(collection.tool_id);
    
    return (
      <Card key={collection.id} className="hover:shadow-md transition-shadow">
        <CardContent className="p-4">
          <div className="flex gap-4">
            {/* 缩略图 */}
            {collection.thumbnail_url && (
              <img
                src={collection.thumbnail_url}
                alt={collection.cloud_name}
                className="w-20 h-20 object-cover rounded-lg flex-shrink-0"
              />
            )}
            
            {/* 内容 */}
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between mb-2">
                <div>
                  <h3 className="font-semibold text-lg">{collection.cloud_name}</h3>
                  {toolInfo && (
                    <div className="flex items-center gap-1 mt-1">
                      <span className="text-sm">{toolInfo.emoji}</span>
                      <span className="text-xs text-gray-500">{toolInfo.name}</span>
                    </div>
                  )}
                </div>
                
                {/* 操作按钮 */}
                <div className="flex gap-1">
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 w-8 p-0"
                    onClick={() => toggleFavorite(collection.id)}
                  >
                    <Heart 
                      className={`h-4 w-4 ${collection.is_favorite ? 'fill-red-500 text-red-500' : 'text-gray-400'}`} 
                    />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 w-8 p-0 text-red-600"
                    onClick={() => deleteCollection(collection.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
              
              {/* 描述 */}
              {collection.cloud_description && (
                <p className="text-sm text-gray-600 mb-2 line-clamp-1">
                  {collection.cloud_description}
                </p>
              )}
              
              {/* 关键词 */}
              {collection.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1 mb-2">
                  {collection.keywords.slice(0, 4).map((keyword, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              )}
              
              {/* 底部信息 */}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    {formatDate(collection.capture_time)}
                  </div>
                  <div className="flex items-center gap-1">
                    <Eye className="h-3 w-3" />
                    {collection.view_count}
                  </div>
                </div>
                {collection.location && (
                  <div className="flex items-center gap-1">
                    <MapPin className="h-3 w-3" />
                    <span>{collection.location.city || '未知地点'}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  // ============== 主渲染 ==============
  return (
    <div className={`max-w-6xl mx-auto p-6 space-y-6 ${className}`}>
      {/* 标题和用户信息 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">我的云朵收藏</h1>
          {currentUser && (
            <p className="text-gray-600 mt-1">
              {currentUser.display_name} • 共 {totalCount} 个收藏
            </p>
          )}
        </div>
        
        {/* 视图切换 */}
        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant={viewMode === 'grid' ? 'default' : 'outline'}
            onClick={() => setViewMode('grid')}
          >
            <Grid className="h-4 w-4" />
          </Button>
          <Button
            size="sm"
            variant={viewMode === 'list' ? 'default' : 'outline'}
            onClick={() => setViewMode('list')}
          >
            <List className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* 筛选器 */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-gray-500" />
              <span className="text-sm font-medium">筛选：</span>
            </div>
            
            {/* 工具筛选 */}
            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                variant={selectedToolId === '' ? 'default' : 'outline'}
                onClick={() => handleToolFilter('')}
              >
                全部工具
              </Button>
              {captureTools.map(tool => (
                <Button
                  key={tool.id}
                  size="sm"
                  variant={selectedToolId === tool.id ? 'default' : 'outline'}
                  onClick={() => handleToolFilter(tool.id)}
                >
                  {tool.emoji} {tool.name}
                </Button>
              ))}
            </div>
            
            {/* 收藏筛选 */}
            <Button
              size="sm"
              variant={showFavoritesOnly ? 'default' : 'outline'}
              onClick={handleFavoriteFilter}
            >
              <Heart className="h-4 w-4 mr-1" />
              仅收藏
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* 加载状态 */}
      {isLoading && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin" />
          <span className="ml-2">加载中...</span>
        </div>
      )}

      {/* 收藏列表 */}
      {!isLoading && (
        <>
          {collections.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <div className="text-gray-500 space-y-4">
                  <div className="text-6xl">☁️</div>
                  <p className="text-lg">天空还很空旷</p>
                  <Button
                    onClick={() => window.location.href = '/'}
                    className="mt-4"
                  >
                    回到首页捕云
                  </Button>
                </div>
              </CardContent>
            </Card>
          ) : (
            <div className={
              viewMode === 'grid' 
                ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'
                : 'space-y-4'
            }>
              {collections.map(collection => 
                viewMode === 'grid' 
                  ? renderCollectionCard(collection)
                  : renderCollectionList(collection)
              )}
            </div>
          )}
        </>
      )}

      {/* 分页 */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            size="sm"
            variant="outline"
            disabled={currentPage === 1}
            onClick={() => handlePageChange(currentPage - 1)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          
          {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
            <Button
              key={page}
              size="sm"
              variant={currentPage === page ? 'default' : 'outline'}
              onClick={() => handlePageChange(page)}
            >
              {page}
            </Button>
          ))}
          
          <Button
            size="sm"
            variant="outline"
            disabled={currentPage === totalPages}
            onClick={() => handlePageChange(currentPage + 1)}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
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
    </div>
  );
} 