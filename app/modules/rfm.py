"""
모듈 4: RFM 세그먼테이션
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from components.question_card import QuestionCard, Question


QUESTIONS = [
    Question(
        id="rfm_1",
        title="Q1. 고객별 R, F, M 값 계산",
        description="""
        **상황:** CRM팀에서 고객을 세분화하여 맞춤 마케팅을 하고 싶어합니다.
        먼저 각 고객의 구매 패턴을 수치화해야 합니다.

        **과제:** 각 고객의 RFM 지표를 계산하세요.

        **RFM 정의:**
        - R (Recency): 마지막 구매 후 경과일
        - F (Frequency): 총 구매 횟수
        - M (Monetary): 총 구매 금액

        **요구사항:**
        - 기준일: '2024-06-30'
        - 결과 컬럼: customer_id, recency, frequency, monetary
        - recency가 낮은 순으로 상위 10명
        """,
        hint="""
        **힌트:**
        - Recency: julianday('2024-06-30') - julianday(MAX(transaction_date))
        - Frequency: COUNT(*)
        - Monetary: SUM(amount)

        ```sql
        SELECT
            customer_id,
            julianday('2024-06-30') - julianday(MAX(transaction_date)) as recency,
            COUNT(*) as frequency,
            SUM(amount) as monetary
        FROM transactions
        GROUP BY customer_id
        ```
        """,
        answer_query="""
SELECT
    customer_id,
    ROUND(julianday('2024-06-30') - julianday(MAX(transaction_date)), 0) as recency,
    COUNT(*) as frequency,
    SUM(amount) as monetary
FROM transactions
GROUP BY customer_id
ORDER BY recency ASC
LIMIT 10
""",
        explanation="""
        **RFM**은 고객을 세 가지 지표로 분류합니다:

        - **R (Recency)**: 최근성 - 낮을수록 좋음 (최근에 구매)
        - **F (Frequency)**: 빈도 - 높을수록 좋음 (자주 구매)
        - **M (Monetary)**: 금액 - 높을수록 좋음 (많이 구매)

        이 세 지표를 조합하여 고객 세그먼트를 정의합니다.
        """,
        interview_tip="""
        **Q: RFM 분석이란 무엇인가요?**

        RFM은 고객을 Recency(최근성), Frequency(빈도), Monetary(금액) 세 가지 지표로 분류하는 고객 세분화 기법입니다.

        각 지표의 의미:
        - **Recency**: 마지막 구매로부터 경과일 (낮을수록 좋음 - 최근에 구매한 고객)
        - **Frequency**: 총 구매 횟수 (높을수록 좋음 - 자주 구매하는 고객)
        - **Monetary**: 총 구매 금액 (높을수록 좋음 - 많이 구매하는 고객)

        RFM의 장점:
        - **간단함**: 구매 데이터만으로 구현 가능
        - **실용적**: 세그먼트별 액션이 명확함
        - **검증됨**: 수십 년간 마케팅에서 활용된 기법
        """,
        difficulty=1
    ),
    Question(
        id="rfm_2",
        title="Q2. RFM 5분위 점수 부여",
        description="""
        **상황:** RFM 값을 계산했지만 숫자 범위가 제각각이라 비교가 어렵습니다.
        모든 지표를 동일한 척도(1-5점)로 변환해야 합니다.

        **과제:** 각 RFM 지표를 5분위로 나누어 점수를 부여하세요.

        **요구사항:**
        - NTILE(5)로 5분위 분할
        - R: 낮을수록 높은 점수 (최근 구매가 좋음)
        - F, M: 높을수록 높은 점수
        - 결과 컬럼: customer_id, recency, frequency, monetary, r_score, f_score, m_score
        """,
        hint="""
        **힌트:**
        1. 먼저 RFM 값을 계산하는 CTE
        2. NTILE(5)로 분위수 계산
        3. R은 역순 (낮을수록 높은 점수)

        ```sql
        NTILE(5) OVER (ORDER BY recency DESC) as r_score,  -- 역순
        NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) as m_score
        ```
        """,
        answer_query="""
WITH rfm AS (
    SELECT
        customer_id,
        ROUND(julianday('2024-06-30') - julianday(MAX(transaction_date)), 0) as recency,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM transactions
    GROUP BY customer_id
)
SELECT
    customer_id,
    recency,
    frequency,
    monetary,
    NTILE(5) OVER (ORDER BY recency DESC) as r_score,
    NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
    NTILE(5) OVER (ORDER BY monetary ASC) as m_score
FROM rfm
ORDER BY r_score DESC, f_score DESC, m_score DESC
LIMIT 20
""",
        explanation="""
        **NTILE(5)**는 데이터를 5개의 동일한 크기 그룹으로 나눕니다.

        점수 해석:
        - 5점: 상위 20% (최고)
        - 1점: 하위 20% (최저)

        **R은 역순**인 이유:
        - Recency가 **낮을수록** 최근에 구매한 것 (좋음)
        - 따라서 ORDER BY recency **DESC**로 해야
          낮은 recency가 높은 점수를 받음
        """,
        interview_tip="""
        **Q: RFM에서 분위수(Quantile) 점수를 사용하는 이유는 무엇인가요?**

        분위수 점수는 RFM 값을 표준화하여 비교 가능하게 만드는 방법입니다.

        분위수 사용 이유:
        - **이상치에 강건함**: 극단값에 영향받지 않음
        - **직관적 해석**: 1-5점으로 쉽게 이해 가능
        - **비교 용이**: 서로 다른 단위(일, 횟수, 금액)를 동일한 척도로 비교

        주의할 점:
        - Recency는 낮을수록 좋으므로 ORDER BY DESC로 역순 정렬 필요
        - 5분위가 일반적이지만, 비즈니스에 따라 3분위나 4분위도 사용
        - 분위 개수가 많으면 세분화되지만 관리가 복잡해짐
        """,
        difficulty=2
    ),
    Question(
        id="rfm_3",
        title="Q3. RFM 세그먼트 분류",
        description="""
        **상황:** 마케팅팀에서 세그먼트별 맞춤 캠페인을 준비하고 있습니다.
        RFM 점수를 기반으로 고객을 의미있는 그룹으로 분류해야 합니다.

        **과제:** RFM 점수 조합으로 고객 세그먼트를 분류하세요.

        **세그먼트 정의:**
        - Champions: R>=4 AND F>=4 AND M>=4
        - Loyal: F>=4
        - At Risk: R<=2 AND F>=3
        - Lost: R<=2 AND F<=2
        - Others: 나머지

        **요구사항:**
        - 세그먼트별 고객 수와 평균 monetary
        - 결과 컬럼: segment, customer_count, avg_monetary
        """,
        hint="""
        **힌트:**
        1. RFM 점수 계산 CTE
        2. CASE WHEN으로 세그먼트 분류
        3. 세그먼트별 집계

        ```sql
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN f_score >= 4 THEN 'Loyal'
            ...
        END as segment
        ```
        """,
        answer_query="""
WITH rfm AS (
    SELECT
        customer_id,
        ROUND(julianday('2024-06-30') - julianday(MAX(transaction_date)), 0) as recency,
        COUNT(*) as frequency,
        SUM(amount) as monetary
    FROM transactions
    GROUP BY customer_id
),
rfm_scores AS (
    SELECT
        customer_id,
        recency,
        frequency,
        monetary,
        NTILE(5) OVER (ORDER BY recency DESC) as r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) as f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) as m_score
    FROM rfm
),
segmented AS (
    SELECT
        customer_id,
        monetary,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
            WHEN f_score >= 4 THEN 'Loyal'
            WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Others'
        END as segment
    FROM rfm_scores
)
SELECT
    segment,
    COUNT(*) as customer_count,
    ROUND(AVG(monetary), 0) as avg_monetary
FROM segmented
GROUP BY segment
ORDER BY avg_monetary DESC
""",
        explanation="""
        **RFM 세그먼트**는 마케팅 전략 수립에 직접 활용됩니다:

        | 세그먼트 | 특성 | 전략 |
        |---------|------|------|
        | Champions | 최고 고객 | VIP 프로그램, 신제품 얼리 액세스 |
        | Loyal | 충성 고객 | 크로스셀링, 로열티 리워드 |
        | At Risk | 이탈 위험 | 윈백 캠페인, 특별 할인 |
        | Lost | 이탈 고객 | 재활성화 또는 포기 |
        """,
        interview_tip="""
        **Q: RFM 세그먼트별로 어떤 마케팅 전략을 사용하나요?**

        RFM 세그먼트는 각 고객 그룹의 특성에 맞는 차별화된 전략을 가능하게 합니다.

        세그먼트별 전략:
        - **Champions** (R높, F높, M높): VIP 프로그램, 신제품 얼리 액세스, 추천 프로그램 참여 유도
        - **Loyal** (F높): 크로스셀링, 업셀링, 로열티 리워드
        - **At Risk** (R낮, F높): 윈백 캠페인, 특별 할인, "보고 싶어요" 메시지
        - **Lost** (R낮, F낮): 재활성화 시도 또는 비용 효율을 위해 포기 결정

        핵심 원칙:
        - 각 세그먼트에 동일한 리소스를 투입하지 않음
        - Champions 유지에 집중하고, At Risk 전환에 우선순위
        """,
        difficulty=3
    ),
    Question(
        id="rfm_4",
        title="Q4. 파레토 분석 (80/20 법칙)",
        description="""
        **상황:** 경영진에서 "핵심 고객에게 집중하라"는 방침을 내렸습니다.
        VIP 프로그램을 만들기 위해 핵심 고객의 기준을 정해야 합니다.

        **과제:** 매출의 80%를 차지하는 상위 고객 비율을 분석하세요.

        **요구사항:**
        - 고객별 매출 순위
        - 누적 매출 비율 계산
        - 80% 매출을 달성하는 고객 비율
        - 결과: 상위 몇 %가 80% 매출 달성하는지
        """,
        hint="""
        **힌트:**
        1. 고객별 매출 계산 및 순위 부여
        2. 누적 매출 계산 (윈도우 함수)
        3. 전체 대비 누적 비율 계산
        4. 80% 도달 시점 찾기

        ```sql
        SUM(monetary) OVER (ORDER BY monetary DESC) as cumulative_revenue
        ```
        """,
        answer_query="""
WITH customer_revenue AS (
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
        ROW_NUMBER() OVER (ORDER BY monetary DESC) as rank,
        SUM(monetary) OVER (ORDER BY monetary DESC) as cumulative_revenue,
        SUM(monetary) OVER () as total_revenue,
        COUNT(*) OVER () as total_customers
    FROM customer_revenue
),
with_pct AS (
    SELECT
        *,
        ROUND(cumulative_revenue * 100.0 / total_revenue, 2) as cumulative_pct,
        ROUND(rank * 100.0 / total_customers, 2) as customer_pct
    FROM ranked
)
SELECT
    customer_pct as top_customer_percent,
    cumulative_pct as revenue_percent
FROM with_pct
WHERE cumulative_pct >= 80
ORDER BY rank
LIMIT 1
""",
        explanation="""
        **파레토 법칙 (80/20 법칙)**:
        상위 20%의 고객이 전체 매출의 80%를 차지한다는 경험 법칙

        실제 비율은 산업/비즈니스마다 다르지만,
        핵심 고객에 집중하는 전략의 근거가 됩니다.

        이 분석으로 VIP 고객 정의 기준을 설정할 수 있습니다.
        """,
        interview_tip="""
        **Q: 파레토 분석(80/20 법칙)이란 무엇이고 어떻게 활용하나요?**

        파레토 분석은 "소수의 핵심 요인이 대부분의 결과를 만든다"는 원리를 검증하는 분석입니다. 이탈리아 경제학자 파레토가 발견한 법칙에서 유래했습니다.

        비즈니스 활용:
        - **VIP 정의**: 상위 몇 %가 매출의 80%를 차지하는지 파악 -> VIP 기준 설정
        - **리소스 배분**: 핵심 고객에게 집중적인 리소스 투입
        - **리스크 관리**: 상위 고객 이탈 시 영향도 계산

        분석 결과 해석:
        - 상위 20%가 80% 매출 -> 전형적인 파레토 분포
        - 상위 10%가 80% 매출 -> 매우 집중된 구조 (소수 의존 위험)
        - 상위 40%가 80% 매출 -> 분산된 구조 (안정적이나 VIP 전략 어려움)
        """,
        difficulty=3
    ),
    Question(
        id="rfm_5",
        title="Q5. 세그먼트별 이동 분석",
        description="""
        **상황:** 마케팅 캠페인의 효과를 측정하려면 고객들의 세그먼트 변화를 추적해야 합니다.
        지난달 대비 고객들이 어떤 세그먼트로 이동했는지 알아야 합니다.

        **과제:** 전월 대비 세그먼트 이동 현황을 분석하세요.

        **요구사항:**
        - 5월 기준 RFM 세그먼트
        - 6월 기준 RFM 세그먼트
        - 세그먼트 이동 매트릭스 (from_segment → to_segment)
        - 이동 고객 수
        """,
        hint="""
        **힌트:**
        1. 5월 기준 RFM 계산 (기준일: 2024-05-31)
        2. 6월 기준 RFM 계산 (기준일: 2024-06-30)
        3. 두 결과를 JOIN하여 이동 분석

        두 개의 큰 CTE가 필요합니다.
        """,
        answer_query="""
WITH rfm_may AS (
    SELECT
        customer_id,
        NTILE(5) OVER (ORDER BY julianday('2024-05-31') - julianday(MAX(transaction_date)) DESC) as r,
        NTILE(5) OVER (ORDER BY COUNT(*) ASC) as f,
        NTILE(5) OVER (ORDER BY SUM(amount) ASC) as m
    FROM transactions
    WHERE transaction_date <= '2024-05-31'
    GROUP BY customer_id
),
segment_may AS (
    SELECT
        customer_id,
        CASE
            WHEN r >= 4 AND f >= 4 AND m >= 4 THEN 'Champions'
            WHEN f >= 4 THEN 'Loyal'
            WHEN r <= 2 AND f >= 3 THEN 'At Risk'
            WHEN r <= 2 AND f <= 2 THEN 'Lost'
            ELSE 'Others'
        END as segment_may
    FROM rfm_may
),
rfm_june AS (
    SELECT
        customer_id,
        NTILE(5) OVER (ORDER BY julianday('2024-06-30') - julianday(MAX(transaction_date)) DESC) as r,
        NTILE(5) OVER (ORDER BY COUNT(*) ASC) as f,
        NTILE(5) OVER (ORDER BY SUM(amount) ASC) as m
    FROM transactions
    WHERE transaction_date <= '2024-06-30'
    GROUP BY customer_id
),
segment_june AS (
    SELECT
        customer_id,
        CASE
            WHEN r >= 4 AND f >= 4 AND m >= 4 THEN 'Champions'
            WHEN f >= 4 THEN 'Loyal'
            WHEN r <= 2 AND f >= 3 THEN 'At Risk'
            WHEN r <= 2 AND f <= 2 THEN 'Lost'
            ELSE 'Others'
        END as segment_june
    FROM rfm_june
)
SELECT
    sm.segment_may as from_segment,
    sj.segment_june as to_segment,
    COUNT(*) as customers
FROM segment_may sm
JOIN segment_june sj ON sm.customer_id = sj.customer_id
WHERE sm.segment_may != sj.segment_june
GROUP BY sm.segment_may, sj.segment_june
ORDER BY customers DESC
LIMIT 10
""",
        explanation="""
        **세그먼트 이동 분석**으로 고객 상태 변화를 추적합니다.

        주요 관찰 포인트:
        - **긍정적 이동**: Others → Loyal, At Risk → Champions
        - **부정적 이동**: Champions → At Risk, Loyal → Lost

        부정적 이동이 많은 세그먼트에 집중적인 리텐션 활동이 필요합니다.
        """,
        interview_tip="""
        **Q: 세그먼트 이동 분석(Segment Migration Analysis)이란 무엇인가요?**

        세그먼트 이동 분석은 고객들이 시간이 지남에 따라 어떤 세그먼트에서 어떤 세그먼트로 이동하는지 추적하는 분석입니다.

        분석의 가치:
        - **캠페인 효과 측정**: At Risk -> Champions 이동이 늘었다면 윈백 캠페인 성공
        - **이탈 조기 경보**: Champions -> At Risk 이동이 늘면 문제 신호
        - **자연적 패턴 파악**: 개입 없이도 발생하는 이동 규모 파악

        핵심 지표:
        - **긍정적 이동률**: Others -> Loyal, At Risk -> Champions
        - **부정적 이동률**: Champions -> At Risk, Loyal -> Lost
        - **순이동(Net Migration)**: 긍정적 이동 - 부정적 이동
        """,
        difficulty=4
    ),
]


def show_rfm_module():
    """RFM 세그먼테이션 모듈"""

    st.title("🎯 RFM 세그먼테이션")

    st.markdown("""
    > **RFM 분석**은 Recency, Frequency, Monetary 세 지표로
    > 고객을 세그먼트로 분류하여 맞춤 마케팅을 실행합니다.
    """)

    with st.expander("📚 핵심 개념 보기", expanded=False):
        st.markdown("""
        ### RFM이란?

        | 지표 | 의미 | 좋은 값 |
        |------|------|--------|
        | **R** (Recency) | 마지막 구매 후 경과일 | 낮을수록 좋음 |
        | **F** (Frequency) | 구매 횟수 | 높을수록 좋음 |
        | **M** (Monetary) | 구매 금액 | 높을수록 좋음 |

        ### 세그먼트 예시

        | 세그먼트 | R | F | M | 전략 |
        |---------|---|---|---|------|
        | Champions | 5 | 5 | 5 | VIP 대우 |
        | Loyal | - | 5 | - | 크로스셀링 |
        | At Risk | 2 | 4 | - | 윈백 캠페인 |
        | Lost | 1 | 1 | - | 재활성화/포기 |
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
    card = QuestionCard(selected_question, "rfm")
    card.render()
