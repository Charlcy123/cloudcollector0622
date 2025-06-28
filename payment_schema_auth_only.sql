-- 基于 auth.users 的支付系统数据库架构
-- 不需要 public.users 表，直接使用 auth.uid()

-- 1. 用户订阅表
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- 直接引用 auth.uid()，不需要外键约束
    stripe_customer_id VARCHAR(255) UNIQUE,
    stripe_subscription_id VARCHAR(255) UNIQUE,
    
    -- 订阅状态
    subscription_status VARCHAR(50) DEFAULT 'free', -- free, active, canceled, past_due, unpaid
    plan_type VARCHAR(50) DEFAULT 'basic', -- basic, pro, premium
    
    -- 计费周期
    billing_cycle VARCHAR(20) DEFAULT 'monthly', -- monthly, yearly
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    
    -- 试用期
    trial_start TIMESTAMPTZ,
    trial_end TIMESTAMPTZ,
    
    -- 使用配额 (JSON格式，灵活扩展)
    usage_quota JSONB DEFAULT '{
        "cloud_collections_limit": 50,
        "storage_limit_mb": 100,
        "api_calls_per_month": 1000
    }',
    
    -- 当前使用量
    current_usage JSONB DEFAULT '{
        "cloud_collections_count": 0,
        "storage_used_mb": 0,
        "api_calls_this_month": 0
    }',
    
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 2. 支付历史表
CREATE TABLE payment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- 直接引用 auth.uid()
    
    -- Stripe 相关ID
    stripe_payment_intent_id VARCHAR(255),
    stripe_invoice_id VARCHAR(255),
    stripe_charge_id VARCHAR(255),
    
    -- 支付信息
    amount INTEGER NOT NULL, -- 金额（分为单位）
    currency VARCHAR(3) DEFAULT 'USD',
    description TEXT,
    
    -- 支付状态
    payment_status VARCHAR(50), -- succeeded, pending, failed, canceled, refunded
    payment_method VARCHAR(50), -- card, bank_transfer, etc.
    
    -- 关联订阅
    subscription_id UUID REFERENCES user_subscriptions(id),
    
    -- 发票信息
    invoice_url TEXT,
    receipt_url TEXT,
    
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 3. 使用量跟踪表（可选，用于详细分析）
CREATE TABLE usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL, -- 直接引用 auth.uid()
    
    -- 使用类型
    usage_type VARCHAR(50), -- cloud_collection_created, storage_used, api_call
    
    -- 使用量
    amount INTEGER DEFAULT 1,
    metadata JSONB, -- 额外信息，如文件大小、API端点等
    
    created_at TIMESTAMPTZ DEFAULT now()
);

-- 创建索引
CREATE INDEX idx_user_subscriptions_user_id ON user_subscriptions(user_id);
CREATE INDEX idx_user_subscriptions_stripe_customer ON user_subscriptions(stripe_customer_id);
CREATE INDEX idx_payment_history_user_id ON payment_history(user_id);
CREATE INDEX idx_payment_history_created_at ON payment_history(created_at);
CREATE INDEX idx_usage_logs_user_id_type ON usage_logs(user_id, usage_type);
CREATE INDEX idx_usage_logs_created_at ON usage_logs(created_at);

-- 创建更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_subscriptions_updated_at 
    BEFORE UPDATE ON user_subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- RLS 策略
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE payment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- 用户只能访问自己的订阅信息
CREATE POLICY "Users can manage own subscriptions" ON user_subscriptions
    FOR ALL USING (auth.uid() = user_id);

-- 用户只能查看自己的支付历史
CREATE POLICY "Users can view own payment history" ON payment_history
    FOR SELECT USING (auth.uid() = user_id);

-- 用户只能查看自己的使用记录
CREATE POLICY "Users can view own usage logs" ON usage_logs
    FOR SELECT USING (auth.uid() = user_id);

-- 系统可以插入使用记录（通过 service_role）
CREATE POLICY "System can insert usage logs" ON usage_logs
    FOR INSERT WITH CHECK (true);

-- 创建视图：用户当前订阅状态
CREATE VIEW user_current_subscription AS
SELECT 
    us.user_id,
    us.subscription_status,
    us.plan_type,
    us.billing_cycle,
    us.current_period_end,
    us.usage_quota,
    us.current_usage,
    -- 计算是否在试用期
    CASE 
        WHEN us.trial_end IS NOT NULL AND us.trial_end > now() 
        THEN true 
        ELSE false 
    END as is_trial,
    -- 计算订阅是否过期
    CASE 
        WHEN us.current_period_end IS NOT NULL AND us.current_period_end < now() 
        THEN true 
        ELSE false 
    END as is_expired
FROM user_subscriptions us;

-- 创建函数：检查用户是否可以执行某个操作
CREATE OR REPLACE FUNCTION check_user_quota(
    p_user_id UUID,
    p_usage_type VARCHAR(50),
    p_amount INTEGER DEFAULT 1
)
RETURNS BOOLEAN AS $$
DECLARE
    v_subscription user_subscriptions%ROWTYPE;
    v_current_count INTEGER;
    v_limit INTEGER;
BEGIN
    -- 获取用户订阅信息
    SELECT * INTO v_subscription 
    FROM user_subscriptions 
    WHERE user_id = p_user_id;
    
    -- 如果没有订阅记录，创建免费账户
    IF NOT FOUND THEN
        INSERT INTO user_subscriptions (user_id) VALUES (p_user_id);
        SELECT * INTO v_subscription 
        FROM user_subscriptions 
        WHERE user_id = p_user_id;
    END IF;
    
    -- 检查具体的配额
    CASE p_usage_type
        WHEN 'cloud_collection' THEN
            v_current_count := (v_subscription.current_usage->>'cloud_collections_count')::INTEGER;
            v_limit := (v_subscription.usage_quota->>'cloud_collections_limit')::INTEGER;
        WHEN 'storage_mb' THEN
            v_current_count := (v_subscription.current_usage->>'storage_used_mb')::INTEGER;
            v_limit := (v_subscription.usage_quota->>'storage_limit_mb')::INTEGER;
        WHEN 'api_call' THEN
            v_current_count := (v_subscription.current_usage->>'api_calls_this_month')::INTEGER;
            v_limit := (v_subscription.usage_quota->>'api_calls_per_month')::INTEGER;
        ELSE
            RETURN true; -- 未知类型，默认允许
    END CASE;
    
    -- 检查是否超出限制
    RETURN (v_current_count + p_amount) <= v_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 创建函数：更新用户使用量
CREATE OR REPLACE FUNCTION update_user_usage(
    p_user_id UUID,
    p_usage_type VARCHAR(50),
    p_amount INTEGER DEFAULT 1
)
RETURNS VOID AS $$
DECLARE
    v_current_usage JSONB;
BEGIN
    -- 记录使用日志
    INSERT INTO usage_logs (user_id, usage_type, amount)
    VALUES (p_user_id, p_usage_type, p_amount);
    
    -- 更新当前使用量
    SELECT current_usage INTO v_current_usage
    FROM user_subscriptions
    WHERE user_id = p_user_id;
    
    -- 如果没有订阅记录，先创建
    IF NOT FOUND THEN
        INSERT INTO user_subscriptions (user_id) VALUES (p_user_id);
        v_current_usage := '{"cloud_collections_count": 0, "storage_used_mb": 0, "api_calls_this_month": 0}';
    END IF;
    
    -- 更新对应的使用量
    CASE p_usage_type
        WHEN 'cloud_collection' THEN
            v_current_usage := jsonb_set(
                v_current_usage, 
                '{cloud_collections_count}', 
                ((v_current_usage->>'cloud_collections_count')::INTEGER + p_amount)::text::jsonb
            );
        WHEN 'storage_mb' THEN
            v_current_usage := jsonb_set(
                v_current_usage, 
                '{storage_used_mb}', 
                ((v_current_usage->>'storage_used_mb')::INTEGER + p_amount)::text::jsonb
            );
        WHEN 'api_call' THEN
            v_current_usage := jsonb_set(
                v_current_usage, 
                '{api_calls_this_month}', 
                ((v_current_usage->>'api_calls_this_month')::INTEGER + p_amount)::text::jsonb
            );
    END CASE;
    
    -- 更新数据库
    UPDATE user_subscriptions 
    SET current_usage = v_current_usage
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 