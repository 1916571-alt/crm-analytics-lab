-- 04. RFM 세그먼테이션 정답
-- 실습 후 자신의 답과 비교해보세요

-- ============================================
-- Mission 1-1: 고객별 RFM 원시값 계산
-- ============================================
WITH max_date AS (
    SELECT MAX(transaction_date) as reference_date
    FROM transactions
)
SELECT
    customer_id,
    julianday(m.reference_date) - julianday(MAX(transaction_date)) as recency,
    COUNT(*) as frequency,
    SUM(amount) as monetary
FROM transactions t, max_date m
GROUP BY customer_id
ORDER BY monetary DESC
LIMIT 10;


-- ============================================
-- Mission 2-1: NTILE을 사용한 점수 부여
-- ============================================
WITH max_date AS (
    SELECT MAX(transaction_date) as reference_date
    FROM transactions
),
rfm_raw AS (
    SELECT
        customer_id,
        julianday(m.reference_date) - julianday(MAX(transaction_date)) as recency,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM transactions t, max_date m
    GROUP BY customer_id
)
SELECT
    customer_id,
    recency,
    frequency,
    monetary,
    -- R은 작을수록 좋으므로 ASC 정렬 후 높은 분위 = 높은 점수
    NTILE(5) OVER (ORDER BY recency ASC) as r_score,
    -- F는 클수록 좋음
    NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
    -- M은 클수록 좋음
    NTILE(5) OVER (ORDER BY monetary DESC) as m_score
FROM rfm_raw
ORDER BY r_score + f_score + m_score DESC
LIMIT 10;


-- ============================================
-- Mission 2-2: RFM 점수 합계 및 조합
-- ============================================
WITH max_date AS (
    SELECT MAX(transaction_date) as reference_date FROM transactions
),
rfm_raw AS (
    SELECT
        customer_id,
        julianday(m.reference_date) - julianday(MAX(transaction_date)) as recency,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM transactions t, max_date m
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency ASC) as r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) as m_score
    FROM rfm_raw
)
SELECT
    customer_id,
    r_score,
    f_score,
    m_score,
    r_score || f_score || m_score as rfm_score,
    r_score + f_score + m_score as rfm_sum
FROM rfm_scores
ORDER BY rfm_sum DESC
LIMIT 10;


-- ============================================
-- Mission 3-1: 세그먼트 정의
-- ============================================
WITH max_date AS (
    SELECT MAX(transaction_date) as reference_date FROM transactions
),
rfm_raw AS (
    SELECT
        customer_id,
        julianday(m.reference_date) - julianday(MAX(transaction_date)) as recency,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM transactions t, max_date m
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency ASC) as r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) as m_score
    FROM rfm_raw
)
SELECT
    customer_id,
    r_score,
    f_score,
    m_score,
    r_score || f_score || m_score as rfm_score,
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'Cannot Lose'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN f_score >= 4 THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score >= 4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalist'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
        ELSE 'Others'
    END as segment
FROM rfm_scores
ORDER BY r_score + f_score + m_score DESC
LIMIT 20;


-- ============================================
-- Mission 3-2: 세그먼트별 요약 통계
-- ============================================
WITH max_date AS (
    SELECT MAX(transaction_date) as reference_date FROM transactions
),
rfm_raw AS (
    SELECT
        customer_id,
        julianday(m.reference_date) - julianday(MAX(transaction_date)) as recency,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM transactions t, max_date m
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency ASC) as r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) as m_score
    FROM rfm_raw
),
rfm_segments AS (
    SELECT
        customer_id,
        monetary,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'Cannot Lose'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN f_score >= 4 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score >= 4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalist'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END as segment
    FROM rfm_scores
),
total_revenue AS (
    SELECT SUM(monetary) as total FROM rfm_segments
)
SELECT
    segment,
    COUNT(*) as customer_count,
    ROUND(AVG(monetary), 0) as avg_monetary,
    ROUND(SUM(monetary), 0) as total_monetary,
    ROUND(SUM(monetary) * 100.0 / total, 2) as revenue_share
FROM rfm_segments, total_revenue
GROUP BY segment
ORDER BY revenue_share DESC;


-- ============================================
-- Mission 4-1: 상위 20% 고객의 매출 비중
-- ============================================
WITH customer_monetary AS (
    SELECT
        customer_id,
        SUM(amount) as monetary
    FROM transactions
    GROUP BY customer_id
),
ranked AS (
    SELECT
        customer_id,
        monetary,
        NTILE(5) OVER (ORDER BY monetary DESC) as quintile
    FROM customer_monetary
),
total AS (
    SELECT SUM(monetary) as total_revenue FROM customer_monetary
)
SELECT
    'Top 20%' as segment,
    COUNT(*) as customers,
    ROUND(SUM(r.monetary), 0) as revenue,
    ROUND(SUM(r.monetary) * 100.0 / t.total_revenue, 2) as revenue_share
FROM ranked r, total t
WHERE quintile = 1;


-- ============================================
-- Mission 4-2: 누적 매출 비중
-- ============================================
WITH customer_monetary AS (
    SELECT
        customer_id,
        SUM(amount) as monetary
    FROM transactions
    GROUP BY customer_id
),
ranked AS (
    SELECT
        customer_id,
        monetary,
        NTILE(5) OVER (ORDER BY monetary DESC) as quintile
    FROM customer_monetary
),
quintile_summary AS (
    SELECT
        quintile,
        COUNT(*) as customers,
        SUM(monetary) as revenue
    FROM ranked
    GROUP BY quintile
),
total AS (
    SELECT SUM(revenue) as total_revenue FROM quintile_summary
)
SELECT
    'Top ' || (quintile * 20) || '%' as segment,
    SUM(q.customers) OVER (ORDER BY q.quintile) as cumulative_customers,
    ROUND(SUM(q.revenue) OVER (ORDER BY q.quintile), 0) as cumulative_revenue,
    ROUND(SUM(q.revenue) OVER (ORDER BY q.quintile) * 100.0 / t.total_revenue, 2) as cumulative_share
FROM quintile_summary q, total t
ORDER BY q.quintile;


-- ============================================
-- Mission 5: 실무 시나리오 (예시 답안)
-- ============================================

-- 세그먼트별 상세 분석 및 마케팅 권고
WITH max_date AS (
    SELECT MAX(transaction_date) as reference_date FROM transactions
),
rfm_raw AS (
    SELECT
        customer_id,
        julianday(m.reference_date) - julianday(MAX(transaction_date)) as recency,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM transactions t, max_date m
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency ASC) as r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) as m_score
    FROM rfm_raw
),
rfm_segments AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        r_score,
        f_score,
        m_score,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'Cannot Lose'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN f_score >= 4 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score >= 4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalist'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END as segment
    FROM rfm_scores
),
segment_summary AS (
    SELECT
        segment,
        COUNT(*) as customers,
        ROUND(AVG(recency), 1) as avg_recency,
        ROUND(AVG(frequency), 1) as avg_frequency,
        ROUND(AVG(monetary), 0) as avg_monetary,
        ROUND(SUM(monetary), 0) as total_monetary
    FROM rfm_segments
    GROUP BY segment
),
total AS (
    SELECT SUM(total_monetary) as grand_total FROM segment_summary
)
SELECT
    s.segment,
    s.customers,
    s.avg_recency || ' days' as avg_days_since_purchase,
    s.avg_frequency || ' orders' as avg_orders,
    s.avg_monetary as avg_spend,
    ROUND(s.total_monetary * 100.0 / t.grand_total, 1) || '%' as revenue_share,
    CASE s.segment
        WHEN 'Champions' THEN 'VIP program, early access, referral program'
        WHEN 'Loyal' THEN 'Upselling, cross-selling, loyalty rewards'
        WHEN 'Potential Loyalist' THEN 'Membership offers, personalized recommendations'
        WHEN 'New Customers' THEN 'Onboarding emails, welcome discount'
        WHEN 'At Risk' THEN 'Win-back campaign, special offers'
        WHEN 'Cannot Lose' THEN 'URGENT: Personal outreach, exclusive deals'
        WHEN 'Lost' THEN 'Low-cost reactivation or deprioritize'
        ELSE 'Monitor'
    END as marketing_action,
    CASE s.segment
        WHEN 'Champions' THEN 1
        WHEN 'Cannot Lose' THEN 2
        WHEN 'At Risk' THEN 3
        WHEN 'Loyal' THEN 4
        WHEN 'Potential Loyalist' THEN 5
        WHEN 'New Customers' THEN 6
        WHEN 'Lost' THEN 7
        ELSE 8
    END as action_priority
FROM segment_summary s, total t
ORDER BY action_priority;


-- 보너스: 채널별 세그먼트 분포
WITH max_date AS (
    SELECT MAX(transaction_date) as reference_date FROM transactions
),
rfm_raw AS (
    SELECT
        t.customer_id,
        c.acquisition_channel,
        julianday(m.reference_date) - julianday(MAX(t.transaction_date)) as recency,
        COUNT(*) as frequency,
        SUM(t.amount) as monetary
    FROM transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    CROSS JOIN max_date m
    GROUP BY t.customer_id, c.acquisition_channel
),
rfm_scores AS (
    SELECT
        customer_id,
        acquisition_channel,
        NTILE(5) OVER (ORDER BY recency ASC) as r_score,
        NTILE(5) OVER (ORDER BY frequency DESC) as f_score,
        NTILE(5) OVER (ORDER BY monetary DESC) as m_score
    FROM rfm_raw
),
rfm_segments AS (
    SELECT
        customer_id,
        acquisition_channel,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN r_score <= 2 AND f_score >= 4 AND m_score >= 4 THEN 'Cannot Lose'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN f_score >= 4 THEN 'Loyal'
            WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
            WHEN r_score >= 4 AND f_score BETWEEN 2 AND 3 THEN 'Potential Loyalist'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END as segment
    FROM rfm_scores
)
SELECT
    acquisition_channel,
    segment,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY acquisition_channel), 1) as pct_of_channel
FROM rfm_segments
GROUP BY acquisition_channel, segment
ORDER BY acquisition_channel, customer_count DESC;
