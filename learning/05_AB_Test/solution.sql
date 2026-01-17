-- 05. A/B 테스트 분석 정답
-- 실습 후 자신의 답과 비교해보세요

-- ============================================
-- Mission 1-1: 그룹별 사용자 수 및 전환 수
-- ============================================
WITH visitors AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'page_view'
),
converters AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'purchase'
)
SELECT
    v.device as experiment_group,
    COUNT(DISTINCT v.user_id) as total_users,
    COUNT(DISTINCT c.user_id) as converted_users
FROM visitors v
LEFT JOIN converters c ON v.device = c.device AND v.user_id = c.user_id
GROUP BY v.device;


-- ============================================
-- Mission 1-2: 전환율 계산
-- ============================================
WITH visitors AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'page_view'
),
converters AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'purchase'
),
group_metrics AS (
    SELECT
        v.device as experiment_group,
        COUNT(DISTINCT v.user_id) as total_users,
        COUNT(DISTINCT c.user_id) as converted_users
    FROM visitors v
    LEFT JOIN converters c ON v.device = c.device AND v.user_id = c.user_id
    GROUP BY v.device
)
SELECT
    experiment_group,
    total_users,
    converted_users,
    ROUND(converted_users * 100.0 / total_users, 2) as conversion_rate
FROM group_metrics;


-- ============================================
-- Mission 2-1: 전환율 차이 계산
-- ============================================
WITH visitors AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'page_view'
),
converters AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'purchase'
),
group_metrics AS (
    SELECT
        v.device as experiment_group,
        COUNT(DISTINCT v.user_id) as total_users,
        COUNT(DISTINCT c.user_id) as converted_users,
        COUNT(DISTINCT c.user_id) * 100.0 / COUNT(DISTINCT v.user_id) as conversion_rate
    FROM visitors v
    LEFT JOIN converters c ON v.device = c.device AND v.user_id = c.user_id
    GROUP BY v.device
),
comparison AS (
    SELECT
        MAX(CASE WHEN experiment_group = 'desktop' THEN conversion_rate END) as control_rate,
        MAX(CASE WHEN experiment_group = 'mobile' THEN conversion_rate END) as treatment_rate
    FROM group_metrics
)
SELECT
    ROUND(control_rate, 2) as control_conversion_rate,
    ROUND(treatment_rate, 2) as treatment_conversion_rate,
    ROUND(treatment_rate - control_rate, 2) as absolute_difference,
    ROUND((treatment_rate - control_rate) * 100.0 / control_rate, 2) as relative_lift_percent
FROM comparison;


-- ============================================
-- Mission 2-2: 통계 검정용 데이터
-- ============================================
WITH visitors AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'page_view'
),
converters AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'purchase'
)
SELECT
    v.device as experiment_group,
    COUNT(DISTINCT v.user_id) as n,
    COUNT(DISTINCT c.user_id) as x,
    COUNT(DISTINCT c.user_id) * 1.0 / COUNT(DISTINCT v.user_id) as p
FROM visitors v
LEFT JOIN converters c ON v.device = c.device AND v.user_id = c.user_id
GROUP BY v.device;


-- ============================================
-- Mission 3-1: 채널별 전환율 비교
-- ============================================
WITH visitors AS (
    SELECT DISTINCT device, channel, user_id
    FROM events
    WHERE event_type = 'page_view'
),
converters AS (
    SELECT DISTINCT device, channel, user_id
    FROM events
    WHERE event_type = 'purchase'
),
channel_metrics AS (
    SELECT
        v.channel,
        v.device,
        COUNT(DISTINCT v.user_id) as total_users,
        COUNT(DISTINCT c.user_id) as converted_users,
        COUNT(DISTINCT c.user_id) * 100.0 / COUNT(DISTINCT v.user_id) as conversion_rate
    FROM visitors v
    LEFT JOIN converters c ON v.device = c.device AND v.channel = c.channel AND v.user_id = c.user_id
    GROUP BY v.channel, v.device
)
SELECT
    channel,
    ROUND(MAX(CASE WHEN device = 'desktop' THEN conversion_rate END), 2) as control_rate,
    ROUND(MAX(CASE WHEN device = 'mobile' THEN conversion_rate END), 2) as treatment_rate,
    ROUND(
        MAX(CASE WHEN device = 'mobile' THEN conversion_rate END) -
        MAX(CASE WHEN device = 'desktop' THEN conversion_rate END),
        2
    ) as difference
FROM channel_metrics
GROUP BY channel
ORDER BY difference DESC;


-- ============================================
-- Mission 3-2: 일별 전환율 추이
-- ============================================
WITH daily_visitors AS (
    SELECT DISTINCT device, event_date, user_id
    FROM events
    WHERE event_type = 'page_view'
),
daily_converters AS (
    SELECT DISTINCT device, event_date, user_id
    FROM events
    WHERE event_type = 'purchase'
),
daily_metrics AS (
    SELECT
        v.event_date,
        v.device,
        COUNT(DISTINCT v.user_id) as total_users,
        COUNT(DISTINCT c.user_id) as converted_users,
        COUNT(DISTINCT c.user_id) * 100.0 / NULLIF(COUNT(DISTINCT v.user_id), 0) as conversion_rate
    FROM daily_visitors v
    LEFT JOIN daily_converters c
        ON v.device = c.device AND v.event_date = c.event_date AND v.user_id = c.user_id
    GROUP BY v.event_date, v.device
)
SELECT
    event_date as date,
    ROUND(MAX(CASE WHEN device = 'desktop' THEN conversion_rate END), 2) as control_rate,
    ROUND(MAX(CASE WHEN device = 'mobile' THEN conversion_rate END), 2) as treatment_rate
FROM daily_metrics
GROUP BY event_date
ORDER BY event_date
LIMIT 14;


-- ============================================
-- Mission 4-1: 예상 추가 전환 수
-- ============================================
WITH visitors AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'page_view'
),
converters AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'purchase'
),
group_metrics AS (
    SELECT
        v.device as experiment_group,
        COUNT(DISTINCT v.user_id) as total_users,
        COUNT(DISTINCT c.user_id) as converted_users,
        COUNT(DISTINCT c.user_id) * 1.0 / COUNT(DISTINCT v.user_id) as conversion_rate
    FROM visitors v
    LEFT JOIN converters c ON v.device = c.device AND v.user_id = c.user_id
    GROUP BY v.device
)
SELECT
    treatment.total_users as treatment_users,
    treatment.converted_users as actual_conversions,
    ROUND(treatment.total_users * control.conversion_rate, 0) as expected_conversions_at_control_rate,
    treatment.converted_users - ROUND(treatment.total_users * control.conversion_rate, 0) as additional_conversions,
    CASE
        WHEN treatment.converted_users > treatment.total_users * control.conversion_rate
        THEN 'Treatment BETTER'
        WHEN treatment.converted_users < treatment.total_users * control.conversion_rate
        THEN 'Control BETTER'
        ELSE 'No difference'
    END as result
FROM group_metrics treatment, group_metrics control
WHERE treatment.experiment_group = 'mobile'
AND control.experiment_group = 'desktop';


-- ============================================
-- Mission 5: 종합 보고서용 쿼리
-- ============================================

-- 전체 실험 요약
WITH visitors AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'page_view'
),
converters AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'purchase'
),
group_metrics AS (
    SELECT
        v.device as experiment_group,
        COUNT(DISTINCT v.user_id) as total_users,
        COUNT(DISTINCT c.user_id) as converted_users,
        COUNT(DISTINCT c.user_id) * 100.0 / COUNT(DISTINCT v.user_id) as conversion_rate
    FROM visitors v
    LEFT JOIN converters c ON v.device = c.device AND v.user_id = c.user_id
    GROUP BY v.device
),
experiment_summary AS (
    SELECT
        MAX(CASE WHEN experiment_group = 'desktop' THEN total_users END) as control_users,
        MAX(CASE WHEN experiment_group = 'desktop' THEN converted_users END) as control_conversions,
        MAX(CASE WHEN experiment_group = 'desktop' THEN conversion_rate END) as control_rate,
        MAX(CASE WHEN experiment_group = 'mobile' THEN total_users END) as treatment_users,
        MAX(CASE WHEN experiment_group = 'mobile' THEN converted_users END) as treatment_conversions,
        MAX(CASE WHEN experiment_group = 'mobile' THEN conversion_rate END) as treatment_rate
    FROM group_metrics
)
SELECT
    '=== A/B TEST SUMMARY ===' as section,
    '' as value
UNION ALL
SELECT 'Control Group (Desktop)', ''
UNION ALL
SELECT '  - Users', control_users || '' FROM experiment_summary
UNION ALL
SELECT '  - Conversions', control_conversions || '' FROM experiment_summary
UNION ALL
SELECT '  - Conversion Rate', ROUND(control_rate, 2) || '%' FROM experiment_summary
UNION ALL
SELECT 'Treatment Group (Mobile)', ''
UNION ALL
SELECT '  - Users', treatment_users || '' FROM experiment_summary
UNION ALL
SELECT '  - Conversions', treatment_conversions || '' FROM experiment_summary
UNION ALL
SELECT '  - Conversion Rate', ROUND(treatment_rate, 2) || '%' FROM experiment_summary
UNION ALL
SELECT '=== RESULTS ===', ''
UNION ALL
SELECT '  - Absolute Difference', ROUND(treatment_rate - control_rate, 2) || '%p' FROM experiment_summary
UNION ALL
SELECT '  - Relative Lift', ROUND((treatment_rate - control_rate) * 100.0 / control_rate, 1) || '%' FROM experiment_summary
UNION ALL
SELECT '  - Additional Conversions', (treatment_conversions - ROUND(treatment_users * control_rate / 100, 0)) || '' FROM experiment_summary;


-- 신뢰구간 추정을 위한 데이터 (Python에서 처리 권장)
WITH visitors AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'page_view'
),
converters AS (
    SELECT DISTINCT device, user_id
    FROM events
    WHERE event_type = 'purchase'
)
SELECT
    v.device as group_name,
    COUNT(DISTINCT v.user_id) as n,
    COUNT(DISTINCT c.user_id) as successes,
    COUNT(DISTINCT c.user_id) * 1.0 / COUNT(DISTINCT v.user_id) as p,
    -- 표준오차 (SE) = sqrt(p * (1-p) / n)
    SQRT(
        (COUNT(DISTINCT c.user_id) * 1.0 / COUNT(DISTINCT v.user_id)) *
        (1 - COUNT(DISTINCT c.user_id) * 1.0 / COUNT(DISTINCT v.user_id)) /
        COUNT(DISTINCT v.user_id)
    ) as standard_error
FROM visitors v
LEFT JOIN converters c ON v.device = c.device AND v.user_id = c.user_id
GROUP BY v.device;
