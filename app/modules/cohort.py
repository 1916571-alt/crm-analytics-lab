"""
모듈 3: Cohort 리텐션 분석
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from components.question_card import QuestionCard, Question


QUESTIONS = [
    Question(
        id="cohort_1",
        title="Q1. 월별 가입 코호트 생성",
        description="""
        **상황:** Growth팀에서 월별 고객 리텐션을 추적하고 싶어합니다.
        언제 가입한 고객들이 가장 오래 유지되는지 알아야 합니다.

        **과제:** 고객을 가입 월 기준으로 코호트로 분류하세요.

        **요구사항:**
        - 고객의 가입월(cohort_month) 추출
        - 코호트별 고객 수 계산
        - 결과 컬럼: cohort_month, customer_count
        - 가입월 순으로 정렬
        """,
        hint="""고객의 가입일에서 년-월을 추출하여 코호트를 정의하고, 각 코호트별 고객 수를 집계합니다.
---
필요한 함수: strftime('%Y-%m', date), COUNT(*), GROUP BY, ORDER BY
---
SELECT
    strftime('%Y-%m', signup_date) as cohort_month,
    COUNT(*) as customer_count
FROM customers
GROUP BY ...
ORDER BY ...""",
        answer_query="""
SELECT
    strftime('%Y-%m', signup_date) as cohort_month,
    COUNT(*) as customer_count
FROM customers
GROUP BY strftime('%Y-%m', signup_date)
ORDER BY cohort_month
""",
        explanation="""
        **코호트(Cohort)**는 특정 기간에 공통 경험을 한 사용자 그룹입니다.

        가입 월 기준 코호트가 가장 일반적이며,
        시간에 따른 행동 변화를 추적하는 데 사용됩니다.

        strftime()은 SQLite의 날짜 포맷팅 함수입니다.
        """,
        interview_tip="""
        **Q: 코호트 분석이 뭔가요?**

        코호트 분석은 동일한 특성을 가진 사용자 그룹의 시간에 따른 행동을 추적하는 분석 방법입니다.

        예를 들어 1월에 가입한 고객들(1월 코호트)이 2월, 3월에 얼마나 재구매하는지 추적합니다.

        코호트 분석이 중요한 이유:
        - **리텐션 측정**: 시간이 지나도 고객이 유지되는지
        - **품질 비교**: 프로모션 때 온 고객 vs 일반 고객
        - **개선 효과 측정**: 제품 개선 후 새 코호트가 더 나은지
        """,
        difficulty=1
    ),
    Question(
        id="cohort_2",
        title="Q2. 코호트별 첫 구매까지 기간",
        description="""
        **상황:** 마케팅팀에서 온보딩 캠페인의 효과를 측정하려고 합니다.
        가입 후 첫 구매까지 걸리는 시간이 코호트별로 다른지 확인이 필요합니다.

        **과제:** 코호트별 가입 후 첫 구매까지 걸리는 평균 일수를 계산하세요.

        **요구사항:**
        - 고객별 가입일 ~ 첫 구매일 기간 계산
        - 코호트별 평균 기간
        - 결과 컬럼: cohort_month, avg_days_to_first_purchase
        """,
        hint="""고객별 첫 구매일을 구하고, 가입일과의 차이를 계산한 후 코호트별 평균을 구합니다.
---
필요한 함수: MIN(), julianday(), AVG(), ROUND(), CTE(WITH절), JOIN
---
WITH first_purchase AS (
    SELECT customer_id, MIN(transaction_date) as first_purchase_date
    FROM transactions
    GROUP BY customer_id
)
SELECT
    strftime('%Y-%m', c.signup_date) as cohort_month,
    ROUND(AVG(julianday(fp.first_purchase_date) - julianday(c.signup_date)), 1) as avg_days
FROM customers c
JOIN first_purchase fp ON ...""",
        answer_query="""
WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(transaction_date) as first_purchase_date
    FROM transactions
    GROUP BY customer_id
)
SELECT
    strftime('%Y-%m', c.signup_date) as cohort_month,
    ROUND(AVG(julianday(fp.first_purchase_date) - julianday(c.signup_date)), 1) as avg_days_to_first_purchase
FROM customers c
JOIN first_purchase fp ON c.customer_id = fp.customer_id
GROUP BY strftime('%Y-%m', c.signup_date)
ORDER BY cohort_month
""",
        explanation="""
        **첫 구매까지 기간**은 온보딩 효과를 측정하는 지표입니다.

        기간이 짧을수록:
        - 온보딩이 효과적
        - 고객 의도가 명확
        - 초기 전환 유도가 잘 됨

        julianday()는 날짜를 일수로 변환하는 SQLite 함수입니다.
        """,
        interview_tip="""
        **Q: 첫 구매까지 기간(Time to First Purchase)이 왜 중요한가요?**

        첫 구매까지 기간은 고객 온보딩의 효율성을 측정하는 핵심 지표입니다.

        이 지표가 중요한 이유:
        - **전환 예측**: 일정 기간 내 첫 구매가 없으면 이탈 가능성이 높음
        - **온보딩 효과 측정**: 웰컴 이메일, 쿠폰 등의 효과를 정량화
        - **코호트 품질 비교**: 어떤 채널에서 온 고객이 빠르게 전환하는지 파악

        일반적으로 첫 구매까지 기간이 짧을수록 장기 LTV도 높은 경향이 있습니다.
        """,
        difficulty=2
    ),
    Question(
        id="cohort_3",
        title="Q3. M+1 리텐션 계산",
        description="""
        **상황:** CEO가 "우리 고객들이 다음 달에도 돌아오나요?"라고 물었습니다.
        리텐션 현황을 숫자로 보여달라는 요청입니다.

        **과제:** 코호트별 M+1 리텐션(가입 다음 달 재구매율)을 계산하세요.

        **요구사항:**
        - 코호트별 전체 고객 수
        - M+1에 구매한 고객 수
        - M+1 리텐션율 (%)
        - 결과 컬럼: cohort_month, total_customers, m1_customers, m1_retention
        """,
        hint="""코호트별 전체 고객 수와 M+1(가입 다음 달)에 구매한 고객 수를 구해 리텐션율을 계산합니다.
---
필요한 함수: strftime(), COUNT(DISTINCT), COALESCE(), 월 차이 계산식, LEFT JOIN
---
-- 월 차이 계산 공식:
(strftime('%Y', t.transaction_date) - strftime('%Y', c.signup_date)) * 12 +
(strftime('%m', t.transaction_date) - strftime('%m', c.signup_date)) as month_diff

-- month_diff = 1인 고객을 집계하여 M+1 리텐션 계산""",
        answer_query="""
WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
customer_activity AS (
    SELECT
        t.customer_id,
        cc.cohort_month,
        (strftime('%Y', t.transaction_date) - strftime('%Y', c.signup_date)) * 12 +
        (strftime('%m', t.transaction_date) - strftime('%m', c.signup_date)) as month_diff
    FROM transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    JOIN customer_cohort cc ON t.customer_id = cc.customer_id
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) as total_customers
    FROM customer_cohort
    GROUP BY cohort_month
),
m1_activity AS (
    SELECT
        cohort_month,
        COUNT(DISTINCT customer_id) as m1_customers
    FROM customer_activity
    WHERE month_diff = 1
    GROUP BY cohort_month
)
SELECT
    cs.cohort_month,
    cs.total_customers,
    COALESCE(m1.m1_customers, 0) as m1_customers,
    ROUND(COALESCE(m1.m1_customers, 0) * 100.0 / cs.total_customers, 2) as m1_retention
FROM cohort_size cs
LEFT JOIN m1_activity m1 ON cs.cohort_month = m1.cohort_month
ORDER BY cs.cohort_month
""",
        explanation="""
        **M+1 리텐션**은 가입 다음 달에 재구매하는 비율입니다.

        가장 중요한 리텐션 지표 중 하나로,
        초기 고객 경험의 품질을 나타냅니다.

        일반적인 기준:
        - E-commerce: 20-30%
        - SaaS: 80-90%
        - Mobile App: 25-35%
        """,
        interview_tip="""
        **Q: M+1 리텐션이란 무엇이고, 왜 중요한가요?**

        M+1 리텐션은 가입 다음 달에 재구매/재방문하는 고객 비율입니다. M+0은 가입 당월, M+1은 다음 달을 의미합니다.

        M+1 리텐션이 중요한 이유:
        - **초기 경험 품질 측정**: 첫 달에 돌아오지 않으면 이후에도 돌아올 가능성이 낮음
        - **성장 예측**: 높은 M+1 리텐션 = 건강한 성장 기반
        - **빠른 피드백**: 제품 변경의 효과를 빠르게 확인 가능

        업계별 벤치마크:
        - E-commerce: 20-30%
        - SaaS: 80-90%
        - Mobile App: 25-35%
        """,
        difficulty=3
    ),
    Question(
        id="cohort_4",
        title="Q4. 리텐션 매트릭스 생성",
        description="""
        **상황:** 경영진 회의에서 리텐션 현황을 한눈에 보여줄 시각화가 필요합니다.
        코호트별로 시간이 지남에 따라 리텐션이 어떻게 변하는지 보여줘야 합니다.

        **과제:** 코호트별 M+0 ~ M+5 리텐션 매트릭스를 생성하세요.

        **요구사항:**
        - 각 코호트의 M+0, M+1, M+2, M+3, M+4, M+5 리텐션
        - 리텐션 = 해당 월 활성 고객 / 코호트 전체 고객 × 100
        - 결과: 코호트별 월간 리텐션 (히트맵용 데이터)
        """,
        hint="""코호트별, 경과월별 활성 고객 비율을 계산하고 PIVOT 형태로 변환합니다.
---
필요한 함수: COUNT(DISTINCT), ROUND(), CASE WHEN, MAX(), GROUP BY, CTE 여러 개
---
-- 리텐션 계산 후 PIVOT 변환:
SELECT
    cohort_month,
    MAX(CASE WHEN month_diff = 0 THEN retention_rate END) as m0,
    MAX(CASE WHEN month_diff = 1 THEN retention_rate END) as m1,
    MAX(CASE WHEN month_diff = 2 THEN retention_rate END) as m2,
    ...
FROM retention
GROUP BY cohort_month""",
        answer_query="""
WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
activity_months AS (
    SELECT
        cc.cohort_month,
        (strftime('%Y', t.transaction_date) - strftime('%Y', c.signup_date)) * 12 +
        (strftime('%m', t.transaction_date) - strftime('%m', c.signup_date)) as month_diff,
        COUNT(DISTINCT t.customer_id) as active_customers
    FROM transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    JOIN customer_cohort cc ON t.customer_id = cc.customer_id
    GROUP BY cc.cohort_month, month_diff
),
cohort_size AS (
    SELECT cohort_month, COUNT(*) as total_customers
    FROM customer_cohort
    GROUP BY cohort_month
),
retention AS (
    SELECT
        am.cohort_month,
        am.month_diff,
        ROUND(am.active_customers * 100.0 / cs.total_customers, 1) as retention_rate
    FROM activity_months am
    JOIN cohort_size cs ON am.cohort_month = cs.cohort_month
    WHERE am.month_diff BETWEEN 0 AND 5
)
SELECT
    cohort_month,
    MAX(CASE WHEN month_diff = 0 THEN retention_rate END) as m0,
    MAX(CASE WHEN month_diff = 1 THEN retention_rate END) as m1,
    MAX(CASE WHEN month_diff = 2 THEN retention_rate END) as m2,
    MAX(CASE WHEN month_diff = 3 THEN retention_rate END) as m3,
    MAX(CASE WHEN month_diff = 4 THEN retention_rate END) as m4,
    MAX(CASE WHEN month_diff = 5 THEN retention_rate END) as m5
FROM retention
GROUP BY cohort_month
ORDER BY cohort_month
""",
        explanation="""
        **리텐션 매트릭스**는 코호트 분석의 핵심 시각화입니다.

        행: 코호트 (가입 월)
        열: 경과 월 (M+0, M+1, ...)
        값: 리텐션율 (%)

        이 매트릭스를 히트맵으로 시각화하면
        시간에 따른 리텐션 패턴을 한눈에 파악할 수 있습니다.
        """,
        interview_tip="""
        **Q: 리텐션 매트릭스(Retention Matrix)란 무엇이고 어떻게 해석하나요?**

        리텐션 매트릭스는 코호트별 시간에 따른 리텐션을 테이블 형태로 보여주는 분석 도구입니다.

        구조:
        - **행(Row)**: 코호트 (예: 가입 월)
        - **열(Column)**: 경과 기간 (M+0, M+1, M+2...)
        - **값(Value)**: 해당 시점의 리텐션율

        해석 방법:
        - **세로로 읽기**: 같은 경과 기간에 코호트별 리텐션 비교 (제품 개선 효과 확인)
        - **가로로 읽기**: 한 코호트의 시간별 리텐션 감소 패턴 확인
        - **대각선 읽기**: 같은 달력 월의 모든 코호트 리텐션 (외부 요인 영향 확인)
        """,
        difficulty=4
    ),
    Question(
        id="cohort_5",
        title="Q5. 코호트별 누적 매출",
        description="""
        **상황:** 재무팀에서 고객 획득 비용(CAC) 대비 수익성을 분석하려고 합니다.
        각 코호트가 시간이 지남에 따라 얼마나 매출을 발생시키는지 알아야 합니다.

        **과제:** 코호트별 누적 매출(Cumulative Revenue)을 계산하세요.

        **요구사항:**
        - 코호트별, 경과월별 누적 매출
        - M+0 ~ M+5까지
        - 결과 컬럼: cohort_month, m0_revenue, m1_revenue, ..., m5_revenue
        """,
        hint="""코호트별, 경과월별 매출을 집계하고 윈도우 함수로 누적 합계를 구한 후 PIVOT 형태로 변환합니다.
---
필요한 함수: SUM(), SUM() OVER(PARTITION BY ... ORDER BY ...), CASE WHEN, MAX()
---
-- 누적 매출 계산:
SUM(revenue) OVER (
    PARTITION BY cohort_month
    ORDER BY month_diff
) as cumulative_revenue

-- 이후 CASE WHEN으로 PIVOT 변환""",
        answer_query="""
WITH customer_cohort AS (
    SELECT
        customer_id,
        strftime('%Y-%m', signup_date) as cohort_month
    FROM customers
),
monthly_revenue AS (
    SELECT
        cc.cohort_month,
        (strftime('%Y', t.transaction_date) - strftime('%Y', c.signup_date)) * 12 +
        (strftime('%m', t.transaction_date) - strftime('%m', c.signup_date)) as month_diff,
        SUM(t.amount) as revenue
    FROM transactions t
    JOIN customers c ON t.customer_id = c.customer_id
    JOIN customer_cohort cc ON t.customer_id = cc.customer_id
    GROUP BY cc.cohort_month, month_diff
),
cumulative AS (
    SELECT
        cohort_month,
        month_diff,
        SUM(revenue) OVER (
            PARTITION BY cohort_month
            ORDER BY month_diff
        ) as cumulative_revenue
    FROM monthly_revenue
    WHERE month_diff BETWEEN 0 AND 5
)
SELECT
    cohort_month,
    MAX(CASE WHEN month_diff = 0 THEN cumulative_revenue END) as m0_revenue,
    MAX(CASE WHEN month_diff = 1 THEN cumulative_revenue END) as m1_revenue,
    MAX(CASE WHEN month_diff = 2 THEN cumulative_revenue END) as m2_revenue,
    MAX(CASE WHEN month_diff = 3 THEN cumulative_revenue END) as m3_revenue,
    MAX(CASE WHEN month_diff = 4 THEN cumulative_revenue END) as m4_revenue,
    MAX(CASE WHEN month_diff = 5 THEN cumulative_revenue END) as m5_revenue
FROM cumulative
GROUP BY cohort_month
ORDER BY cohort_month
""",
        explanation="""
        **누적 매출**은 코호트의 장기 가치를 측정합니다.

        LTV 예측에 활용:
        - M+6 시점의 누적 매출로 패턴 파악
        - 새 코호트의 LTV를 조기에 예측 가능

        윈도우 함수 SUM() OVER()로 누적 합계를 계산합니다.
        """,
        interview_tip="""
        **Q: 코호트별 누적 매출 분석은 왜 중요하고 어떻게 활용하나요?**

        누적 매출 분석은 고객의 장기 가치(LTV)를 예측하고 마케팅 투자 수익을 계산하는 데 핵심적인 도구입니다.

        활용 방법:
        - **CAC Payback 계산**: 고객 획득 비용을 몇 개월 만에 회수하는지
        - **LTV 예측**: 초기 몇 개월 데이터로 장기 가치 예측
        - **코호트 품질 비교**: 어떤 채널/캠페인의 고객이 더 가치있는지

        핵심 인사이트:
        - 누적 매출 곡선이 평평해지는 시점 = 추가 리텐션 노력이 필요한 시점
        - 코호트 간 누적 매출 격차 = 고객 품질 차이
        """,
        difficulty=4
    ),
]


def show_cohort_module():
    """Cohort 분석 모듈"""

    # 모듈 헤더
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.5rem !important;">📅 Cohort 리텐션 분석</h1>
        <p style="font-size: 1.1rem !important; color: #6B7280 !important;">
            코호트 기반 리텐션 분석 · 시간에 따른 고객 유지율 추적
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📚 핵심 개념 보기", expanded=False):
        st.markdown("""
        ### 코호트(Cohort)란?

        특정 기간에 공통 경험(가입, 첫 구매 등)을 한 사용자 그룹

        ### 리텐션 매트릭스

        ```
        코호트    M+0   M+1   M+2   M+3   M+4
        2024-01  100%  45%   30%   25%   22%
        2024-02  100%  48%   32%   27%   -
        2024-03  100%  42%   28%   -     -
        ```

        ### 핵심 지표

        | 지표 | 설명 |
        |------|------|
        | **M+1 리텐션** | 첫 달 재방문율 (가장 중요) |
        | **안정화 시점** | 리텐션이 평평해지는 월 |
        | **누적 매출** | 코호트의 장기 가치 |
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
    card = QuestionCard(selected_question, "cohort")
    card.render()
