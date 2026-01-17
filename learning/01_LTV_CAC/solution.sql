-- 01. LTV & CAC 분석 정답
-- 실습 후 자신의 답과 비교해보세요

-- ============================================
-- Mission 1-1: AOV (Average Order Value) 계산
-- ============================================
SELECT
    SUM(amount) as total_revenue,
    COUNT(*) as total_orders,
    SUM(amount) / COUNT(*) as aov
    -- 또는 AVG(amount) as aov
FROM transactions;


-- ============================================
-- Mission 1-2: 고객당 평균 구매 빈도
-- ============================================
SELECT
    COUNT(*) as total_orders,
    COUNT(DISTINCT customer_id) as total_customers,
    COUNT(*) * 1.0 / COUNT(DISTINCT customer_id) as avg_purchase_frequency
FROM transactions;


-- ============================================
-- Mission 2-1: 고객별 총 매출 (Historical LTV)
-- ============================================
SELECT
    customer_id,
    SUM(amount) as total_revenue,
    COUNT(*) as order_count,
    MIN(transaction_date) as first_order_date,
    MAX(transaction_date) as last_order_date
FROM transactions
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================
-- Mission 2-2: 전체 평균 LTV
-- ============================================
SELECT
    SUM(amount) as total_revenue,
    COUNT(DISTINCT customer_id) as total_customers,
    SUM(amount) * 1.0 / COUNT(DISTINCT customer_id) as avg_ltv
FROM transactions;


-- ============================================
-- Mission 2-3: 채널별 LTV 비교
-- ============================================
SELECT
    c.acquisition_channel,
    COUNT(DISTINCT c.customer_id) as customer_count,
    COALESCE(SUM(t.amount), 0) as total_revenue,
    COALESCE(SUM(t.amount), 0) * 1.0 / COUNT(DISTINCT c.customer_id) as avg_ltv
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY c.acquisition_channel
ORDER BY avg_ltv DESC;


-- ============================================
-- Mission 3-1: 전체 CAC
-- ============================================
SELECT
    (SELECT SUM(spend) FROM campaigns) as total_marketing_cost,
    (SELECT COUNT(*) FROM customers) as total_customers,
    (SELECT SUM(spend) FROM campaigns) * 1.0 / (SELECT COUNT(*) FROM customers) as cac;


-- ============================================
-- Mission 3-2: 채널별 CAC 비교
-- ============================================
-- 방법 1: customers 테이블의 acquisition_cost 사용
SELECT
    c.acquisition_channel as channel,
    COUNT(*) as customer_count,
    SUM(c.acquisition_cost) as total_cost,
    AVG(c.acquisition_cost) as cac
FROM customers c
GROUP BY c.acquisition_channel
ORDER BY cac DESC;

-- 방법 2: campaigns 테이블과 조인 (더 복잡)
WITH channel_spend AS (
    SELECT
        channel,
        SUM(spend) as total_spend
    FROM campaigns
    GROUP BY channel
),
channel_customers AS (
    SELECT
        acquisition_channel as channel,
        COUNT(*) as customer_count
    FROM customers
    GROUP BY acquisition_channel
)
SELECT
    c.channel,
    COALESCE(s.total_spend, 0) as total_spend,
    c.customer_count,
    CASE
        WHEN c.customer_count > 0
        THEN COALESCE(s.total_spend, 0) * 1.0 / c.customer_count
        ELSE 0
    END as cac
FROM channel_customers c
LEFT JOIN channel_spend s ON c.channel = s.channel
ORDER BY cac DESC;


-- ============================================
-- Mission 4: LTV:CAC 비율 분석
-- ============================================
WITH channel_ltv AS (
    SELECT
        c.acquisition_channel as channel,
        COUNT(DISTINCT c.customer_id) as customer_count,
        COALESCE(SUM(t.amount), 0) as total_revenue,
        COALESCE(SUM(t.amount), 0) * 1.0 / COUNT(DISTINCT c.customer_id) as avg_ltv
    FROM customers c
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.acquisition_channel
),
channel_cac AS (
    SELECT
        acquisition_channel as channel,
        AVG(acquisition_cost) as cac
    FROM customers
    GROUP BY acquisition_channel
)
SELECT
    l.channel,
    l.customer_count,
    ROUND(l.avg_ltv, 2) as avg_ltv,
    ROUND(c.cac, 2) as cac,
    CASE
        WHEN c.cac = 0 THEN NULL
        ELSE ROUND(l.avg_ltv / c.cac, 2)
    END as ltv_cac_ratio,
    CASE
        WHEN c.cac = 0 THEN 'N/A (organic)'
        WHEN l.avg_ltv / c.cac > 5 THEN 'Excellent'
        WHEN l.avg_ltv / c.cac > 3 THEN 'Good'
        WHEN l.avg_ltv / c.cac > 1 THEN 'Warning'
        ELSE 'Critical'
    END as grade
FROM channel_ltv l
JOIN channel_cac c ON l.channel = c.channel
ORDER BY ltv_cac_ratio DESC NULLS LAST;


-- ============================================
-- Mission 5: 실무 시나리오 (예시 답안)
-- ============================================
-- 채널별 전체 성과 요약
WITH channel_metrics AS (
    SELECT
        c.acquisition_channel as channel,
        COUNT(DISTINCT c.customer_id) as customers,
        COALESCE(SUM(t.amount), 0) as revenue,
        COALESCE(SUM(t.amount), 0) * 1.0 / COUNT(DISTINCT c.customer_id) as ltv,
        AVG(c.acquisition_cost) as cac
    FROM customers c
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.acquisition_channel
)
SELECT
    channel,
    customers,
    ROUND(revenue, 0) as total_revenue,
    ROUND(ltv, 2) as avg_ltv,
    ROUND(cac, 2) as avg_cac,
    CASE WHEN cac > 0 THEN ROUND(ltv / cac, 2) ELSE NULL END as ltv_cac_ratio,
    -- 예산 배분 권고
    CASE
        WHEN cac = 0 THEN 'Maximize (free channel)'
        WHEN ltv / cac > 5 THEN 'Increase budget significantly'
        WHEN ltv / cac > 3 THEN 'Maintain or slight increase'
        WHEN ltv / cac > 1 THEN 'Optimize or reduce'
        ELSE 'Reduce significantly or pause'
    END as budget_recommendation
FROM channel_metrics
ORDER BY ltv_cac_ratio DESC NULLS LAST;


-- ============================================
-- 보너스: 월별 LTV 추세 분석
-- ============================================
SELECT
    strftime('%Y-%m', c.signup_date) as signup_month,
    COUNT(DISTINCT c.customer_id) as new_customers,
    COALESCE(SUM(t.amount), 0) as total_revenue,
    COALESCE(SUM(t.amount), 0) * 1.0 / COUNT(DISTINCT c.customer_id) as avg_ltv
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
GROUP BY strftime('%Y-%m', c.signup_date)
ORDER BY signup_month;
