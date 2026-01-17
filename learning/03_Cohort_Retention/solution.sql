-- 03. Cohort & Retention 분석 정답
-- 실습 후 자신의 답과 비교해보세요

-- ============================================
-- Mission 1-1: 월별 코호트 생성
-- ============================================
SELECT
    strftime('%Y-%m', signup_date) as cohort_month,
    COUNT(*) as cohort_size
FROM customers
GROUP BY strftime('%Y-%m', signup_date)
ORDER BY cohort_month;


-- ============================================
-- Mission 1-2: 고객별 코호트 할당
-- ============================================
SELECT
    customer_id,
    signup_date,
    strftime('%Y-%m', signup_date) as cohort_month
FROM customers
ORDER BY signup_date
LIMIT 10;


-- ============================================
-- Mission 2-1: 활동 월 계산
-- ============================================
SELECT DISTINCT
    customer_id,
    strftime('%Y-%m', transaction_date) as activity_month
FROM transactions
ORDER BY customer_id, activity_month
LIMIT 20;


-- ============================================
-- Mission 2-2: 가입 후 경과 기간 계산
-- ============================================
WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
customer_activity AS (
    SELECT DISTINCT
        customer_id,
        strftime('%Y-%m', transaction_date) as activity_month
    FROM transactions
)
SELECT
    a.customer_id,
    c.cohort_month,
    a.activity_month,
    (CAST(strftime('%Y', a.activity_month || '-01') AS INTEGER) -
     CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
    (CAST(strftime('%m', a.activity_month || '-01') AS INTEGER) -
     CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) as periods_since_signup
FROM customer_activity a
JOIN customer_cohort c ON a.customer_id = c.customer_id
ORDER BY a.customer_id, a.activity_month
LIMIT 20;


-- ============================================
-- Mission 2-3: 코호트별 리텐션 매트릭스
-- ============================================
WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
cohort_size AS (
    SELECT
        cohort_month,
        COUNT(*) as size
    FROM customer_cohort
    GROUP BY cohort_month
),
customer_activity AS (
    SELECT DISTINCT
        t.customer_id,
        c.cohort_month,
        strftime('%Y-%m', t.transaction_date) as activity_month,
        (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
         CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
        (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
         CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) as period
    FROM transactions t
    JOIN customer_cohort c ON t.customer_id = c.customer_id
),
retention_data AS (
    SELECT
        cohort_month,
        period,
        COUNT(DISTINCT customer_id) as active_customers
    FROM customer_activity
    WHERE period >= 0
    GROUP BY cohort_month, period
)
SELECT
    r.cohort_month,
    r.period,
    r.active_customers,
    s.size as cohort_size,
    ROUND(r.active_customers * 100.0 / s.size, 2) as retention_rate
FROM retention_data r
JOIN cohort_size s ON r.cohort_month = s.cohort_month
WHERE r.period <= 6
ORDER BY r.cohort_month, r.period;


-- ============================================
-- Mission 3-1: 기간별 평균 리텐션
-- ============================================
WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) as size
    FROM customer_cohort
    GROUP BY cohort_month
),
customer_activity AS (
    SELECT DISTINCT
        t.customer_id,
        c.cohort_month,
        (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
         CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
        (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
         CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) as period
    FROM transactions t
    JOIN customer_cohort c ON t.customer_id = c.customer_id
),
cohort_retention AS (
    SELECT
        a.cohort_month,
        a.period,
        COUNT(DISTINCT a.customer_id) * 100.0 / s.size as retention_rate
    FROM customer_activity a
    JOIN cohort_size s ON a.cohort_month = s.cohort_month
    WHERE a.period >= 0
    GROUP BY a.cohort_month, a.period, s.size
)
SELECT
    period,
    ROUND(AVG(retention_rate), 2) as avg_retention,
    ROUND(MIN(retention_rate), 2) as min_retention,
    ROUND(MAX(retention_rate), 2) as max_retention
FROM cohort_retention
WHERE period <= 6
GROUP BY period
ORDER BY period;


-- ============================================
-- Mission 3-2: 최고/최저 성과 코호트
-- ============================================
WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) as size
    FROM customer_cohort
    GROUP BY cohort_month
),
month3_retention AS (
    SELECT
        c.cohort_month,
        COUNT(DISTINCT t.customer_id) * 100.0 / s.size as retention_rate,
        s.size as cohort_size
    FROM customer_cohort c
    JOIN cohort_size s ON c.cohort_month = s.cohort_month
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
        AND (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
             CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
            (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
             CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) = 3
    GROUP BY c.cohort_month, s.size
)
SELECT
    cohort_month,
    cohort_size,
    ROUND(retention_rate, 2) as month3_retention,
    CASE
        WHEN retention_rate = (SELECT MAX(retention_rate) FROM month3_retention) THEN 'BEST'
        WHEN retention_rate = (SELECT MIN(retention_rate) FROM month3_retention) THEN 'WORST'
        ELSE ''
    END as ranking
FROM month3_retention
ORDER BY retention_rate DESC;


-- ============================================
-- Mission 4-1: 채널별 3개월 리텐션
-- ============================================
WITH customer_info AS (
    SELECT
        customer_id,
        acquisition_channel,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
month3_activity AS (
    SELECT DISTINCT
        c.customer_id,
        c.acquisition_channel
    FROM customer_info c
    JOIN transactions t ON c.customer_id = t.customer_id
    WHERE (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
           CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
          (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
           CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) = 3
)
SELECT
    c.acquisition_channel as channel,
    COUNT(DISTINCT c.customer_id) as total_customers,
    COUNT(DISTINCT a.customer_id) as retained_at_month3,
    ROUND(COUNT(DISTINCT a.customer_id) * 100.0 / COUNT(DISTINCT c.customer_id), 2) as retention_rate
FROM customer_info c
LEFT JOIN month3_activity a ON c.customer_id = a.customer_id
GROUP BY c.acquisition_channel
ORDER BY retention_rate DESC;


-- ============================================
-- Mission 5: 실무 시나리오 (예시 답안)
-- ============================================

-- 1. 기간별 이탈 분석
WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) as size
    FROM customer_cohort
    GROUP BY cohort_month
),
period_retention AS (
    SELECT
        a.period,
        SUM(a.active_customers) as total_active,
        SUM(s.size) as total_cohort_size,
        SUM(a.active_customers) * 100.0 / SUM(s.size) as avg_retention
    FROM (
        SELECT
            c.cohort_month,
            (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
             CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
            (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
             CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) as period,
            COUNT(DISTINCT t.customer_id) as active_customers
        FROM customer_cohort c
        LEFT JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.cohort_month, period
    ) a
    JOIN cohort_size s ON a.cohort_month = s.cohort_month
    WHERE a.period >= 0 AND a.period <= 6
    GROUP BY a.period
)
SELECT
    period,
    ROUND(avg_retention, 2) as retention_rate,
    ROUND(LAG(avg_retention) OVER (ORDER BY period) - avg_retention, 2) as dropoff,
    CASE
        WHEN period = 0 THEN 'Baseline'
        WHEN LAG(avg_retention) OVER (ORDER BY period) - avg_retention > 20 THEN 'HIGH DROP - Priority'
        WHEN LAG(avg_retention) OVER (ORDER BY period) - avg_retention > 10 THEN 'MEDIUM DROP'
        ELSE 'STABLE'
    END as status
FROM period_retention
ORDER BY period;


-- 2. 채널별 리텐션 트렌드 (복수 기간)
WITH customer_info AS (
    SELECT
        customer_id,
        acquisition_channel,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
channel_retention AS (
    SELECT
        c.acquisition_channel,
        (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
         CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
        (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
         CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) as period,
        COUNT(DISTINCT t.customer_id) as active_customers
    FROM customer_info c
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
    WHERE (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
           CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
          (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
           CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) BETWEEN 0 AND 6
    GROUP BY c.acquisition_channel, period
),
channel_size AS (
    SELECT
        acquisition_channel,
        COUNT(*) as total
    FROM customer_info
    GROUP BY acquisition_channel
)
SELECT
    r.acquisition_channel as channel,
    r.period,
    ROUND(r.active_customers * 100.0 / s.total, 2) as retention_rate
FROM channel_retention r
JOIN channel_size s ON r.acquisition_channel = s.acquisition_channel
ORDER BY r.acquisition_channel, r.period;


-- 3. 종합 권고안 (채널 × 리텐션 매트릭스)
WITH customer_info AS (
    SELECT
        customer_id,
        acquisition_channel,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
channel_metrics AS (
    SELECT
        c.acquisition_channel,
        COUNT(DISTINCT c.customer_id) as total_customers,
        COUNT(DISTINCT CASE
            WHEN (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
                  CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
                 (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
                  CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) = 1
            THEN t.customer_id END) as month1_retained,
        COUNT(DISTINCT CASE
            WHEN (CAST(strftime('%Y', t.transaction_date) AS INTEGER) -
                  CAST(strftime('%Y', c.cohort_month || '-01') AS INTEGER)) * 12 +
                 (CAST(strftime('%m', t.transaction_date) AS INTEGER) -
                  CAST(strftime('%m', c.cohort_month || '-01') AS INTEGER)) = 3
            THEN t.customer_id END) as month3_retained
    FROM customer_info c
    LEFT JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.acquisition_channel
)
SELECT
    acquisition_channel as channel,
    total_customers,
    ROUND(month1_retained * 100.0 / total_customers, 2) as month1_retention,
    ROUND(month3_retained * 100.0 / total_customers, 2) as month3_retention,
    CASE
        WHEN month3_retained * 100.0 / total_customers > 20 THEN 'HIGH VALUE - Scale up'
        WHEN month3_retained * 100.0 / total_customers > 10 THEN 'MEDIUM - Optimize'
        ELSE 'LOW - Review or reduce'
    END as recommendation
FROM channel_metrics
ORDER BY month3_retention DESC;
