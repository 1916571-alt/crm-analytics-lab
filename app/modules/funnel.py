"""
모듈 2: Funnel 분석
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from components.question_card import QuestionCard, Question


QUESTIONS = [
    Question(
        id="funnel_1",
        title="Q1. 전체 퍼널 전환율 계산",
        description="""
        **상황:** PM이 "우리 서비스의 전환율이 어떻게 되나요?"라고 물었습니다.
        page_view부터 purchase까지의 전환 퍼널을 분석해야 합니다.

        **과제:** 이벤트 로그를 기반으로 전환 퍼널의 각 단계별 사용자 수와 전환율을 계산하세요.

        **퍼널 단계:**
        1. page_view (페이지 방문)
        2. product_view (상품 조회)
        3. add_to_cart (장바구니 추가)
        4. purchase (구매)

        **테이블:** `events` (user_id, event_type, event_date)

        **요구사항:**
        - 각 단계별 고유 사용자 수
        - 첫 단계(page_view) 대비 전환율 (%)
        - 결과 컬럼: `step`, `users`, `conversion_rate`
        """,
        hint="""각 단계별 고유 사용자 수를 먼저 구하고,
첫 단계(page_view) 대비 비율로 전환율을 계산합니다.
---
필요한 함수: COUNT(DISTINCT), GROUP BY, CASE WHEN
page_view 사용자 수를 서브쿼리나 CTE로 가져와서 나눕니다.
---
WITH funnel AS (
    SELECT event_type as step, COUNT(DISTINCT user_id) as users
    FROM events
    WHERE event_type IN ('page_view', 'product_view', 'add_to_cart', 'purchase')
    GROUP BY event_type
),
total AS (SELECT users as total_users FROM funnel WHERE step = 'page_view')
SELECT f.step, f.users, ROUND(f.users * 100.0 / t.total_users, 2) as conversion_rate
FROM funnel f, total t""",
        answer_query="""
WITH funnel AS (
    SELECT
        event_type as step,
        COUNT(DISTINCT user_id) as users
    FROM events
    WHERE event_type IN ('page_view', 'product_view', 'add_to_cart', 'purchase')
    GROUP BY event_type
),
total AS (
    SELECT users as total_users FROM funnel WHERE step = 'page_view'
)
SELECT
    f.step,
    f.users,
    ROUND(f.users * 100.0 / t.total_users, 2) as conversion_rate
FROM funnel f, total t
ORDER BY
    CASE f.step
        WHEN 'page_view' THEN 1
        WHEN 'product_view' THEN 2
        WHEN 'add_to_cart' THEN 3
        WHEN 'purchase' THEN 4
    END
""",
        explanation="""
        **퍼널 분석**은 사용자가 목표(구매)까지 거치는 단계를 추적합니다.

        전환율 = 해당 단계 사용자 / 첫 단계 사용자 × 100

        이 데이터에서:
        - page_view → product_view: 높은 전환율 (관심 있는 방문자)
        - add_to_cart → purchase: 낮은 전환율 (결제 이탈)

        가장 큰 이탈이 발생하는 단계가 **병목 지점**입니다.
        """,
        interview_tip="""
        **Q: 퍼널 분석이 뭔가요?**

        "퍼널 분석은 사용자가 최종 목표(보통 구매나 가입)까지 거치는 단계별 전환을
        시각화하고 분석하는 방법입니다.

        예를 들어 이커머스에서:
        방문(100%) → 상품조회(50%) → 장바구니(10%) → 구매(2%)

        위처럼 단계가 진행될수록 사용자가 줄어들기 때문에
        '깔때기(Funnel)' 모양이 됩니다.

        퍼널 분석의 핵심은 **가장 큰 이탈이 발생하는 병목 지점**을 찾는 것입니다.
        그 지점을 개선하면 전체 전환율에 가장 큰 영향을 미칩니다."
        """,
        difficulty=1
    ),
    Question(
        id="funnel_2",
        title="Q2. 단계별 이탈률 계산",
        description="""
        **상황:** 전환율만 봐서는 어디가 문제인지 명확하지 않습니다.
        각 단계에서 다음 단계로 넘어가지 않는 사용자 비율을 알아야 합니다.

        **과제:** 각 단계에서 다음 단계로 넘어가지 않는 이탈률을 계산하세요.

        **테이블:** `events` (user_id, event_type, event_date)

        **요구사항:**
        - 각 단계의 사용자 수
        - 이전 단계 대비 이탈률 (drop_off_rate)
        - 결과 컬럼: `step`, `users`, `prev_users`, `drop_off_rate`
        """,
        hint="""이탈률 = (이전 단계 사용자 - 현재 단계 사용자) / 이전 단계 사용자 × 100
이전 단계 값을 가져와야 합니다.
---
LAG() 윈도우 함수: 이전 행의 값을 가져옴
LAG(users) OVER (ORDER BY step_order) → 이전 단계 사용자 수
---
WITH funnel AS (
    SELECT event_type as step, COUNT(DISTINCT user_id) as users,
           CASE event_type WHEN 'page_view' THEN 1 WHEN 'product_view' THEN 2
                           WHEN 'add_to_cart' THEN 3 WHEN 'purchase' THEN 4 END as step_order
    FROM events WHERE event_type IN ('page_view','product_view','add_to_cart','purchase')
    GROUP BY event_type
)
SELECT step, users, LAG(users) OVER (ORDER BY step_order) as prev_users,
       ROUND((LAG(users) OVER (ORDER BY step_order) - users) * 100.0 / LAG(users) OVER (ORDER BY step_order), 2) as drop_off_rate
FROM funnel""",
        answer_query="""
WITH funnel AS (
    SELECT
        event_type as step,
        COUNT(DISTINCT user_id) as users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'purchase' THEN 4
        END as step_order
    FROM events
    WHERE event_type IN ('page_view', 'product_view', 'add_to_cart', 'purchase')
    GROUP BY event_type
)
SELECT
    step,
    users,
    LAG(users) OVER (ORDER BY step_order) as prev_users,
    ROUND(
        (LAG(users) OVER (ORDER BY step_order) - users) * 100.0 /
        LAG(users) OVER (ORDER BY step_order),
        2
    ) as drop_off_rate
FROM funnel
ORDER BY step_order
""",
        explanation="""
        **이탈률(Drop-off Rate)**은 각 단계에서 다음 단계로 진행하지 않는 비율입니다.

        이탈률 = (이전 단계 - 현재 단계) / 이전 단계 × 100

        LAG() 윈도우 함수를 사용하면 이전 행의 값을 가져올 수 있습니다.

        이탈률이 가장 높은 단계가 개선 우선순위입니다.
        """,
        interview_tip="""
        **Q: 이탈률은 어떻게 계산하고, 왜 중요한가요?**

        "이탈률은 한 단계에서 다음 단계로 넘어가지 않는 비율입니다.

        예를 들어 상품조회 100명 중 장바구니 담기가 20명이면,
        이탈률은 80%입니다.

        전환율과 이탈률의 차이:
        - **전환율**: 첫 단계 대비 현재 단계 (전체 흐름 파악)
        - **이탈률**: 직전 단계 대비 현재 단계 (구간별 문제 파악)

        이탈률이 중요한 이유는 **어디를 고쳐야 하는지** 알려주기 때문입니다.
        전환율 2%를 개선하고 싶다면, 가장 이탈률이 높은 단계를 찾아 집중해야 합니다."
        """,
        difficulty=2
    ),
    Question(
        id="funnel_3",
        title="Q3. 디바이스별 퍼널 비교",
        description="""
        **상황:** 모바일 트래픽이 전체의 70%인데, 매출은 30%밖에 안 됩니다.
        디바이스별로 퍼널을 비교해서 문제를 찾아야 합니다.

        **과제:** 디바이스(mobile/desktop)별로 퍼널 전환율을 비교하세요.

        **테이블:** `events` (user_id, event_type, device, event_date)

        **요구사항:**
        - 디바이스별, 단계별 사용자 수
        - 디바이스별 첫 단계 대비 전환율
        - 결과 컬럼: `device`, `step`, `users`, `conversion_rate`
        - 디바이스, 단계 순으로 정렬
        """,
        hint="""device와 event_type 두 가지로 그룹화해서
디바이스별로 각각 첫 단계 대비 전환율을 계산합니다.
---
PARTITION BY device: 디바이스별로 따로 계산
FIRST_VALUE(): 각 파티션의 첫 번째 값 (page_view 사용자 수)
---
SELECT device, step, users,
       ROUND(users * 100.0 / FIRST_VALUE(users) OVER (PARTITION BY device ORDER BY step_order), 2) as conversion_rate
FROM (
    SELECT device, event_type as step, COUNT(DISTINCT user_id) as users,
           CASE event_type WHEN 'page_view' THEN 1 WHEN 'product_view' THEN 2
                           WHEN 'add_to_cart' THEN 3 WHEN 'purchase' THEN 4 END as step_order
    FROM events WHERE event_type IN ('page_view','product_view','add_to_cart','purchase')
    GROUP BY device, event_type
)""",
        answer_query="""
WITH funnel AS (
    SELECT
        device,
        event_type as step,
        COUNT(DISTINCT user_id) as users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'purchase' THEN 4
        END as step_order
    FROM events
    WHERE event_type IN ('page_view', 'product_view', 'add_to_cart', 'purchase')
    GROUP BY device, event_type
)
SELECT
    device,
    step,
    users,
    ROUND(
        users * 100.0 /
        FIRST_VALUE(users) OVER (PARTITION BY device ORDER BY step_order),
        2
    ) as conversion_rate
FROM funnel
ORDER BY device, step_order
""",
        explanation="""
        **디바이스별 퍼널 분석**으로 UX 개선 포인트를 찾습니다.

        일반적인 패턴:
        - Desktop: 전환율 높음, 객단가 높음
        - Mobile: 트래픽 많음, 전환율 낮음

        Mobile 전환율이 현저히 낮다면 모바일 UX 개선이 우선입니다.
        """,
        interview_tip="""
        **Q: 디바이스별로 퍼널을 분석하는 이유는 뭔가요?**

        "모바일과 데스크탑은 사용자 행동이 다르기 때문입니다.

        일반적으로:
        - **모바일**: 탐색 위주, 짧은 세션, 결제 불편
        - **데스크탑**: 구매 목적, 긴 세션, 결제 용이

        그래서 모바일 트래픽은 70%인데 매출은 30%일 수 있습니다.

        디바이스별 퍼널을 보면 어디서 차이가 나는지 알 수 있습니다.
        예를 들어 모바일에서 '장바구니→결제' 이탈이 높다면,
        간편결제 도입이나 모바일 결제 UX 개선이 필요합니다."
        """,
        difficulty=2
    ),
    Question(
        id="funnel_4",
        title="Q4. 병목 지점 자동 식별",
        description="""
        **상황:** 매주 퍼널 분석 리포트를 작성하는데, 병목 지점을 매번
        수동으로 찾기 번거롭습니다. 자동으로 찾는 쿼리가 필요합니다.

        **과제:** 가장 큰 이탈이 발생하는 병목 지점을 자동으로 찾으세요.

        **테이블:** `events` (user_id, event_type, event_date)

        **요구사항:**
        - 단계별 이탈률 계산
        - 이탈률이 가장 높은 단계 식별
        - 결과: 병목 단계명, 이탈률, 이탈 사용자 수
        """,
        hint="""먼저 단계별 이탈률을 계산하고,
가장 높은 이탈률을 가진 단계를 찾습니다.
---
이탈률 계산 후 ORDER BY drop_off_rate DESC LIMIT 1
또는 WHERE drop_off_rate = (SELECT MAX(drop_off_rate) ...)
---
WITH funnel AS (...이전 문제와 동일...),
with_dropoff AS (
    SELECT step, users,
           LAG(users) OVER (ORDER BY step_order) - users as dropped_users,
           ROUND((LAG(users) OVER (...) - users) * 100.0 / LAG(users) OVER (...), 2) as drop_off_rate
    FROM funnel
)
SELECT step as bottleneck_step, drop_off_rate, dropped_users
FROM with_dropoff
WHERE drop_off_rate IS NOT NULL
ORDER BY drop_off_rate DESC LIMIT 1""",
        answer_query="""
WITH funnel AS (
    SELECT
        event_type as step,
        COUNT(DISTINCT user_id) as users,
        CASE event_type
            WHEN 'page_view' THEN 1
            WHEN 'product_view' THEN 2
            WHEN 'add_to_cart' THEN 3
            WHEN 'purchase' THEN 4
        END as step_order
    FROM events
    WHERE event_type IN ('page_view', 'product_view', 'add_to_cart', 'purchase')
    GROUP BY event_type
),
with_dropoff AS (
    SELECT
        step,
        users,
        LAG(users) OVER (ORDER BY step_order) as prev_users,
        LAG(users) OVER (ORDER BY step_order) - users as dropped_users,
        ROUND(
            (LAG(users) OVER (ORDER BY step_order) - users) * 100.0 /
            LAG(users) OVER (ORDER BY step_order),
            2
        ) as drop_off_rate
    FROM funnel
)
SELECT
    step as bottleneck_step,
    drop_off_rate,
    dropped_users
FROM with_dropoff
WHERE drop_off_rate IS NOT NULL
ORDER BY drop_off_rate DESC
LIMIT 1
""",
        explanation="""
        **병목 지점(Bottleneck)**은 가장 큰 이탈이 발생하는 단계입니다.

        이 단계를 개선하면 전체 전환율에 가장 큰 영향을 미칩니다.

        병목 식별 후:
        1. 해당 단계의 UX 분석
        2. 사용자 피드백 수집
        3. A/B 테스트로 개선안 검증
        """,
        interview_tip="""
        **Q: 병목 지점을 어떻게 찾나요?**

        "병목 지점은 이탈률이 가장 높은 단계입니다.

        예를 들어 퍼널이:
        - page_view → product_view: 50% 이탈
        - product_view → add_to_cart: 80% 이탈
        - add_to_cart → purchase: 60% 이탈

        여기서 병목은 'product_view → add_to_cart' 단계입니다.

        이 단계를 개선하면 전체 전환율에 가장 큰 영향을 미칩니다.
        왜냐하면 80%나 이탈하던 곳에서 10%만 줄여도
        전체 구매자가 크게 증가하기 때문입니다."
        """,
        difficulty=3
    ),
    Question(
        id="funnel_5",
        title="Q5. 시간대별 전환율 패턴",
        description="""
        **상황:** 마케팅팀에서 푸시 알림을 보내는 최적 시간을 알고 싶어합니다.
        시간대별로 전환율이 다른지 분석해야 합니다.

        **과제:** 시간대별 구매 전환율 패턴을 분석하세요.

        **테이블:** `events` (user_id, event_type, event_date)

        **요구사항:**
        - 시간대(0-23시)별 page_view 수와 purchase 수
        - 시간대별 구매 전환율
        - 결과 컬럼: `hour`, `page_views`, `purchases`, `conversion_rate`
        - 시간 순으로 정렬
        """,
        hint="""시간대별로 그룹화하고, 각 시간대에서
page_view와 purchase 사용자 수를 각각 집계합니다.
---
strftime('%H', event_date): 시간(00-23) 추출
CASE WHEN + COUNT(DISTINCT): 조건별 고유 사용자 수
NULLIF(x, 0): 0으로 나누기 방지
---
SELECT strftime('%H', event_date) as hour,
       COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as page_views,
       COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as purchases,
       ROUND(purchases * 100.0 / NULLIF(page_views, 0), 2) as conversion_rate
FROM events
WHERE event_type IN ('page_view', 'purchase')
GROUP BY hour ORDER BY hour""",
        answer_query="""
SELECT
    strftime('%H', event_date) as hour,
    COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as page_views,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as purchases,
    ROUND(
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 100.0 /
        NULLIF(COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END), 0),
        2
    ) as conversion_rate
FROM events
WHERE event_type IN ('page_view', 'purchase')
GROUP BY strftime('%H', event_date)
ORDER BY hour
""",
        explanation="""
        **시간대별 전환율**은 마케팅 타이밍 최적화에 활용됩니다.

        일반적인 패턴:
        - 점심(12-14시): 트래픽 높음, 전환율 중간
        - 저녁(20-22시): 트래픽/전환율 모두 높음
        - 심야(02-06시): 트래픽 낮음, 전환율 높음 (의도적 구매)

        NULLIF로 0으로 나누는 오류를 방지합니다.
        """,
        interview_tip="""
        **Q: 시간대별 전환율을 분석하는 이유는 뭔가요?**

        "마케팅 타이밍을 최적화하기 위해서입니다.

        예를 들어:
        - 저녁 8-10시: 전환율 4% (가장 높음)
        - 점심 12-2시: 전환율 2% (트래픽만 높음)

        이런 패턴을 발견하면:
        1. **광고**: 전환율 높은 시간대에 예산 집중
        2. **푸시 알림**: 구매 의향 높은 시간대에 발송
        3. **프로모션**: 트래픽+전환율 모두 높은 시간대에 진행

        같은 비용으로 더 많은 전환을 얻을 수 있습니다."
        """,
        difficulty=3
    ),
]


def show_funnel_module():
    """Funnel 분석 모듈"""

    # 모듈 헤더
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.5rem !important;">🔄 Funnel 분석</h1>
        <p style="font-size: 1.1rem !important; color: #6B7280 !important;">
            전환 퍼널 분석 · 사용자 여정의 병목 지점을 찾고 전환율 개선
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📚 핵심 개념 보기", expanded=False):
        st.markdown("""
        ### 퍼널(Funnel)이란?

        사용자가 최종 목표까지 거치는 단계를 깔때기 모양으로 시각화한 것

        ```
        [페이지 방문] 10,000명
             ↓
        [상품 조회]   5,000명 (50%)
             ↓
        [장바구니]    1,000명 (10%)
             ↓
        [구매 완료]     200명 (2%)
        ```

        ### 핵심 지표

        | 지표 | 설명 |
        |------|------|
        | **전환율** | 특정 단계 도달 비율 |
        | **이탈률** | 다음 단계로 안 가는 비율 |
        | **병목 지점** | 가장 큰 이탈 구간 |

        ### 개선 우선순위

        **가장 큰 이탈이 발생하는 단계**를 먼저 개선하면
        전체 전환율에 가장 큰 영향을 미칩니다.
        """)

    st.divider()

    question_titles = [f"{q.title}" for q in QUESTIONS]
    selected_idx = st.selectbox(
        "문제 선택",
        range(len(QUESTIONS)),
        format_func=lambda x: question_titles[x]
    )

    st.divider()

    selected_question = QUESTIONS[selected_idx]
    card = QuestionCard(selected_question, "funnel")
    card.render()
