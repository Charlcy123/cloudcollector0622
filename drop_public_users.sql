-- 删除 public.users 表的SQL脚本
-- 注意：执行前请确保已经完全迁移到auth.uid()

-- 1. 首先检查是否还有引用public.users表的外键约束
-- 如果有的话，需要先删除这些约束

-- 2. 删除public.users表
DROP TABLE IF EXISTS public.users CASCADE;

-- 3. 验证删除结果
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_schema = 'public' AND table_name = 'users'; 