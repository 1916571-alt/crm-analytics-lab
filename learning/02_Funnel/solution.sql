-- 02. Funnel 분석 정답
-- 실습 후 자신의 답과 비교해보세요

-- ============================================
-- Mission 1-1: 단계별 고유 사용자 수
-- ============================================
SELECT
    event_type,
    COUNT(DISTINCT user_id) as unique_users
FROM events
GROUP BY event_type
ORDER BY unique_users DESC;


-- ============================================
-- Mission 1-2: 퍼널 순서대로 정렬
-- ============================================
SELECT
    event_type,
    COUNT(DISTINCT user_id) as unique_users,
    CASE event_type
        WHEN 'page_view' THEN 1
        WHEN 'product_view' THEN 2
        WHEN 'add_to_cart' THEN 3
        WHEN 'checkout_start' THEN 4
        WHEN 'purchase' THEN 5
    END as step_order
FROM events
GROUP BY event_type
ORDER BY step_order;


-- ============================================
-- Mission 2-1: 전체 퍼널 전환율
-- ============================================
WITH funnel AS (
    SELECT
        event_type,
        COUNT(DISTINCT user_id) as unique_users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'checkout_start' THEN 4
            WHEN 'purchase' THEN 5
        END as step_order
    FROM events
    GROUP BY event_type
),
first_step AS (
    SELECT unique_users as total_users
    FROM funnel
    WHERE event_type = 'page_view'
)
SELECT
    f.step_order,
    f.event_type,
    f.unique_users,
    ROUND(f.unique_users * 100.0 / fs.total_users, 2) as conversion_rate
FROM funnel f, first_step fs
ORDER BY f.step_order;


-- ============================================
-- Mission 2-2: 단계별 전환율 (Step-to-Step)
-- ============================================
WITH funnel AS (
    SELECT
        event_type,
        COUNT(DISTINCT user_id) as unique_users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'checkout_start' THEN 4
            WHEN 'purchase' THEN 5
        END as step_order
    FROM events
    GROUP BY event_type
)
SELECT
    curr.step_order,
    curr.event_type,
    curr.unique_users,
    prev.unique_users as prev_step_users,
    ROUND(
        COALESCE(curr.unique_users * 100.0 / prev.unique_users, 100),
        2
    ) as step_conversion_rate
FROM funnel curr
LEFT JOIN funnel prev ON curr.step_order = prev.step_order + 1
ORDER BY curr.step_order;


-- ============================================
-- Mission 3-1: 디바이스별 퍼널
-- ============================================
WITH device_funnel AS (
    SELECT
        device,
        event_type,
        COUNT(DISTINCT user_id) as unique_users
    FROM events
    GROUP BY device, event_type
),
device_first_step AS (
    SELECT device, unique_users as total_users
    FROM device_funnel
    WHERE event_type = 'page_view'
)
SELECT
    f.device,
    f.event_type,
    f.unique_users,
    ROUND(f.unique_users * 100.0 / fs.total_users, 2) as conversion_rate
FROM device_funnel f
JOIN device_first_step fs ON f.device = fs.device
ORDER BY f.device,
    CASE f.event_type
        WHEN 'page_view' THEN 1
        WHEN 'product_view' THEN 2
        WHEN 'add_to_cart' THEN 3
        WHEN 'checkout_start' THEN 4
        WHEN 'purchase' THEN 5
    END;


-- ============================================
-- Mission 3-2: 채널별 최종 전환율 비교
-- ============================================
SELECT
    channel,
    SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END) as page_views,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) as purchases,
    ROUND(
        SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) * 100.0 /
        NULLIF(SUM(CASE WHEN event_type = 'page_view' THEN 1 ELSE 0 END), 0),
        2
    ) as overall_conversion_rate
FROM events
GROUP BY channel
ORDER BY overall_conversion_rate DESC;


-- ============================================
-- Mission 4-1: 드롭오프 분석
-- ============================================
WITH funnel AS (
    SELECT
        event_type,
        COUNT(DISTINCT user_id) as users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'checkout_start' THEN 4
            WHEN 'purchase' THEN 5
        END as step
    FROM events
    GROUP BY event_type
)
SELECT
    curr.step,
    curr.event_type,
    curr.users,
    COALESCE(prev.users - curr.users, 0) as dropoff_count,
    ROUND(
        CASE
            WHEN prev.users IS NULL THEN 0
            ELSE (prev.users - curr.users) * 100.0 / prev.users
        END,
        2
    ) as dropoff_rate
FROM funnel curr
LEFT JOIN funnel prev ON curr.step = prev.step + 1
ORDER BY curr.step;


-- ============================================
-- Mission 5: 실무 시나리오 (예시 답안)
-- ============================================

-- 1. 전체 퍼널 병목 분석 (가장 전환율이 낮은 단계 찾기)
WITH funnel AS (
    SELECT
        event_type,
        COUNT(DISTINCT user_id) as users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'checkout_start' THEN 4
            WHEN 'purchase' THEN 5
        END as step
    FROM events
    GROUP BY event_type
)
SELECT
    curr.step,
    curr.event_type as current_step,
    prev.event_type as previous_step,
    prev.users as prev_users,
    curr.users as curr_users,
    ROUND(curr.users * 100.0 / prev.users, 2) as conversion_rate,
    ROUND((prev.users - curr.users) * 100.0 / prev.users, 2) as dropoff_rate,
    CASE
        WHEN curr.users * 100.0 / prev.users < 50 THEN 'HIGH PRIORITY'
        WHEN curr.users * 100.0 / prev.users < 70 THEN 'MEDIUM PRIORITY'
        ELSE 'LOW PRIORITY'
    END as priority
FROM funnel curr
JOIN funnel prev ON curr.step = prev.step + 1
ORDER BY conversion_rate ASC;


-- 2. 디바이스별 병목 비교 (피봇 형태)
WITH device_funnel AS (
    SELECT
        device,
        event_type,
        COUNT(DISTINCT user_id) as users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'checkout_start' THEN 4
            WHEN 'purchase' THEN 5
        END as step
    FROM events
    GROUP BY device, event_type
),
device_step_conv AS (
    SELECT
        curr.device,
        curr.step,
        curr.event_type,
        ROUND(curr.users * 100.0 / prev.users, 2) as step_conversion
    FROM device_funnel curr
    JOIN device_funnel prev ON curr.device = prev.device AND curr.step = prev.step + 1
)
SELECT
    step,
    event_type,
    MAX(CASE WHEN device = 'mobile' THEN step_conversion END) as mobile_conv,
    MAX(CASE WHEN device = 'desktop' THEN step_conversion END) as desktop_conv,
    MAX(CASE WHEN device = 'tablet' THEN step_conversion END) as tablet_conv
FROM device_step_conv
GROUP BY step, event_type
ORDER BY step;


-- 3. 종합 개선 우선순위 권고
WITH funnel_analysis AS (
    SELECT
        event_type,
        COUNT(DISTINCT user_id) as users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'checkout_start' THEN 4
            WHEN 'purchase' THEN 5
        END as step
    FROM events
    GROUP BY event_type
),
step_metrics AS (
    SELECT
        curr.step,
        curr.event_type,
        prev.users - curr.users as dropoff_count,
        ROUND((prev.users - curr.users) * 100.0 / prev.users, 2) as dropoff_rate
    FROM funnel_analysis curr
    JOIN funnel_analysis prev ON curr.step = prev.step + 1
)
SELECT
    step,
    event_type as bottleneck_step,
    dropoff_count,
    dropoff_rate as dropoff_percent,
    CASE
        WHEN dropoff_rate > 60 THEN '1. URGENT: Immediate attention required'
        WHEN dropoff_rate > 40 THEN '2. HIGH: Prioritize for next sprint'
        WHEN dropoff_rate > 20 THEN '3. MEDIUM: Include in roadmap'
        ELSE '4. LOW: Monitor only'
    END as recommendation
FROM step_metrics
ORDER BY dropoff_rate DESC;


-- ============================================
-- 보너스: 시간대별 전환율 분석
-- ============================================
WITH hourly_events AS (
    SELECT
        CAST(strftime('%H', event_timestamp) AS INTEGER) as hour,
        event_type,
        COUNT(DISTINCT user_id) as users
    FROM events
    GROUP BY hour, event_type
)
SELECT
    hour,
    MAX(CASE WHEN event_type = 'page_view' THEN users ELSE 0 END) as page_views,
    MAX(CASE WHEN event_type = 'purchase' THEN users ELSE 0 END) as purchases,
    ROUND(
        MAX(CASE WHEN event_type = 'purchase' THEN users ELSE 0 END) * 100.0 /
        NULLIF(MAX(CASE WHEN event_type = 'page_view' THEN users ELSE 0 END), 0),
        2
    ) as conversion_rate
FROM hourly_events
GROUP BY hour
ORDER BY hour;
