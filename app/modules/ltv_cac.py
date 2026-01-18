"""
모듈 1: LTV & CAC 분석
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from components.question_card import QuestionCard, Question


# 문제 정의
QUESTIONS = [
    Question(
        id="ltv_1",
        title="Q1. 전체 고객의 평균 LTV 계산",
        description="""
        **상황:** 당신은 이커머스 스타트업의 데이터 분석가입니다.
        경영진이 마케팅 예산 상한선을 정하기 위해 고객 1명의 평균 가치를 알고 싶어합니다.

        **과제:** 전체 고객의 평균 LTV(Customer Lifetime Value)를 계산하세요.

        **테이블:** `transactions` (customer_id, amount, transaction_date)

        **요구사항:**
        - 고객별 총 구매액을 먼저 계산
        - 전체 고객의 평균값을 산출
        - 결과 컬럼명: `avg_ltv`
        - 소수점 둘째자리까지 반올림
        """,
        hint="""고객별 총 구매액을 먼저 구하고, 그 평균을 계산하세요.
두 단계로 나눠서 생각하면 됩니다.
---
필요한 함수: SUM(), AVG(), GROUP BY, ROUND()
CTE(WITH절)를 사용하면 코드가 깔끔해집니다.
---
WITH customer_revenue AS (
    SELECT customer_id, SUM(amount) as total_revenue
    FROM transactions
    GROUP BY customer_id
)
SELECT ROUND(AVG(total_revenue), 2) as avg_ltv
FROM customer_revenue""",
        answer_query="""
WITH customer_revenue AS (
    SELECT
        customer_id,
        SUM(amount) as total_revenue
    FROM transactions
    GROUP BY customer_id
)
SELECT
    ROUND(AVG(total_revenue), 2) as avg_ltv
FROM customer_revenue
""",
        explanation="""
        **LTV (Customer Lifetime Value)**는 한 고객이 전체 기간 동안 창출하는 총 매출입니다.

        계산 방법:
        1. 고객별 총 구매액 계산 (SUM + GROUP BY)
        2. 전체 고객의 평균 산출 (AVG)

        이 방법은 **Historical LTV**로, 실제 발생한 매출 기준입니다.
        실무에서는 **Predictive LTV** (예상 미래 가치)도 함께 사용합니다.
        """,
        interview_tip="""
        **Q: LTV가 무엇인가요?**

        "LTV는 Customer Lifetime Value의 약자로, 한 고객이 우리 서비스를 이용하는
        전체 기간 동안 창출하는 총 가치를 의미합니다.

        크게 두 가지 방식으로 계산합니다:
        - **Historical LTV**: 실제 발생한 누적 매출 기반
        - **Predictive LTV**: 평균 주문액 × 구매 빈도 × 예상 활동 기간

        LTV는 마케팅 예산 상한선을 정하는 핵심 기준입니다.
        예를 들어 LTV가 10만원이면, 고객 획득에 10만원 이상 쓰면 손해입니다."
        """,
        difficulty=1
    ),
    Question(
        id="ltv_2",
        title="Q2. 채널별 CAC 계산",
        description="""
        **상황:** 마케팅팀에서 어떤 광고 채널이 가장 효율적인지 알고 싶어합니다.
        채널별로 고객 1명을 획득하는 데 드는 비용을 계산해주세요.

        **과제:** 마케팅 채널별 CAC(Customer Acquisition Cost)를 계산하세요.

        **테이블:** `campaigns` (channel, spend, conversions)
        - spend: 마케팅 비용
        - conversions: 획득한 고객 수

        **요구사항:**
        - 채널별로 총 비용 / 총 전환 수 계산
        - 결과 컬럼: `channel`, `total_spend`, `total_conversions`, `cac`
        - CAC가 낮은 순으로 정렬
        """,
        hint="""채널별로 그룹화해서 총 비용과 총 전환 수를 구하세요.
CAC = 총 비용 / 총 전환 수 입니다.
---
필요한 함수: SUM(), GROUP BY, ORDER BY
SQLite에서 정수 나눗셈 주의: * 1.0을 곱해서 실수로 변환하세요.
---
SELECT
    channel,
    SUM(spend) as total_spend,
    SUM(conversions) as total_conversions,
    ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) as cac
FROM campaigns
GROUP BY channel
ORDER BY cac ASC""",
        answer_query="""
SELECT
    channel,
    SUM(spend) as total_spend,
    SUM(conversions) as total_conversions,
    ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) as cac
FROM campaigns
GROUP BY channel
ORDER BY cac ASC
""",
        explanation="""
        **CAC (Customer Acquisition Cost)**는 신규 고객 1명을 획득하는 데 드는 비용입니다.

        계산: CAC = 마케팅 비용 / 획득 고객 수

        **주의:** SQLite에서 정수 나눗셈은 정수 결과를 반환하므로,
        `* 1.0`을 곱해 실수 나눗셈으로 변환해야 합니다.

        CAC가 낮을수록 효율적인 채널입니다.
        """,
        interview_tip="""
        **Q: CAC는 어떻게 계산하나요? 그리고 왜 중요한가요?**

        "CAC는 Customer Acquisition Cost로, 마케팅 비용을 획득한 고객 수로 나눈 값입니다.

        예를 들어 Google Ads에 100만원을 쓰고 50명을 획득했다면, CAC는 2만원입니다.

        CAC가 중요한 이유는 **LTV와 비교**해야 하기 때문입니다.
        CAC가 3만원인데 LTV가 2만원이면, 고객을 획득할수록 손해입니다.

        채널별 CAC를 비교하면 마케팅 예산을 어디에 집중해야 할지 알 수 있습니다.
        단, CAC만 보면 안 되고 해당 채널의 LTV도 함께 봐야 합니다."
        """,
        difficulty=1
    ),
    Question(
        id="ltv_3",
        title="Q3. 채널별 LTV:CAC 비율",
        description="""
        **상황:** CFO가 "어떤 채널에 마케팅 예산을 더 투자해야 하는가?"를 물었습니다.
        CAC만 보면 Referral이 가장 낮지만, 정말 그 채널이 최고일까요?

        **과제:** 채널별 LTV:CAC 비율을 계산하여 진정한 효율성을 평가하세요.

        **테이블:**
        - `customers` (customer_id, acquisition_channel, signup_date)
        - `transactions` (customer_id, amount, transaction_date)
        - `campaigns` (channel, spend, conversions)

        **요구사항:**
        - 채널별 평균 LTV (customers + transactions JOIN)
        - 채널별 CAC (campaigns 테이블)
        - LTV:CAC 비율 계산
        - 비율이 높은 순으로 정렬
        - 결과 컬럼: `channel`, `avg_ltv`, `cac`, `ltv_cac_ratio`
        """,
        hint="""두 가지 정보를 각각 구해서 합쳐야 합니다:
1) 채널별 평균 LTV (customers + transactions)
2) 채널별 CAC (campaigns)
---
필요한 개념: CTE 2개 만들기, JOIN
channel_ltv와 channel_cac 두 개의 CTE를 만들고 JOIN하세요.
---
WITH channel_ltv AS (
    SELECT c.acquisition_channel as channel,
           ROUND(SUM(t.amount) * 1.0 / COUNT(DISTINCT c.customer_id), 2) as avg_ltv
    FROM customers c JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.acquisition_channel
),
channel_cac AS (
    SELECT channel, ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) as cac
    FROM campaigns GROUP BY channel
)
SELECT l.channel, l.avg_ltv, c.cac, ROUND(l.avg_ltv / c.cac, 2) as ltv_cac_ratio
FROM channel_ltv l JOIN channel_cac c ON l.channel = c.channel""",
        answer_query="""
WITH channel_ltv AS (
    SELECT
        c.acquisition_channel as channel,
        ROUND(SUM(t.amount) * 1.0 / COUNT(DISTINCT c.customer_id), 2) as avg_ltv
    FROM customers c
    JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.acquisition_channel
),
channel_cac AS (
    SELECT
        channel,
        ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) as cac
    FROM campaigns
    GROUP BY channel
)
SELECT
    l.channel,
    l.avg_ltv,
    c.cac,
    ROUND(l.avg_ltv / c.cac, 2) as ltv_cac_ratio
FROM channel_ltv l
JOIN channel_cac c ON l.channel = c.channel
ORDER BY ltv_cac_ratio DESC
""",
        explanation="""
        **LTV:CAC 비율**은 마케팅 효율성의 핵심 지표입니다.

        해석 기준:
        - **3:1 이상**: 건전한 비즈니스 모델
        - **1:1 ~ 3:1**: 개선 필요
        - **1:1 미만**: 적자, 심각한 문제

        비율이 너무 높으면(예: 10:1) 마케팅에 충분히 투자하지 않는 것일 수 있습니다.
        """,
        interview_tip="""
        **Q: LTV:CAC 비율이 뭔가요? 기준은 어떻게 되나요?**

        "LTV:CAC 비율은 고객 획득 비용 대비 고객이 창출하는 가치의 비율입니다.

        예를 들어 CAC가 3만원이고 LTV가 9만원이면, 비율은 3:1입니다.
        이는 1원을 투자해서 3원을 번다는 의미입니다.

        일반적인 기준:
        - **3:1 이상**: 건전함. 마케팅 확대 고려 가능
        - **1:1 ~ 3:1**: 주의 필요. 효율화 필요
        - **1:1 미만**: 적자 상태. 즉시 개선 필요

        다만 업종마다 다릅니다. SaaS는 5:1 이상을 목표로 하고,
        리테일은 2:1도 괜찮을 수 있습니다."
        """,
        difficulty=2
    ),
    Question(
        id="ltv_4",
        title="Q4. Payback Period 계산",
        description="""
        **상황:** 회사의 현금 흐름이 빠듯합니다. 마케팅에 투자한 비용을
        얼마나 빨리 회수할 수 있는지 알아야 재투자 계획을 세울 수 있습니다.

        **과제:** 채널별 Payback Period(회수 기간)를 계산하세요.

        **공식:** Payback Period = CAC / 월평균 매출

        **테이블:**
        - `customers` (customer_id, acquisition_channel, signup_date)
        - `transactions` (customer_id, amount, transaction_date)
        - `campaigns` (channel, spend, conversions)

        **요구사항:**
        - 채널별 고객당 월평균 매출 계산
        - CAC / 월평균 매출 = 회수 개월 수
        - 결과 컬럼: `channel`, `monthly_revenue_per_customer`, `cac`, `payback_months`
        - 회수 기간이 짧은 순으로 정렬
        """,
        hint="""Payback = CAC / 월평균 매출
먼저 고객별 활동 기간(월)과 월평균 매출을 구해야 합니다.
---
활동 기간 계산: julianday() 함수로 날짜 차이 계산
(MAX날짜 - MIN날짜) / 30 + 1 = 활동 월수
CASE WHEN으로 거래가 1건인 경우 처리
---
WITH customer_monthly AS (
    SELECT c.customer_id, c.acquisition_channel as channel,
           SUM(t.amount) as total_revenue,
           CASE WHEN COUNT(t.transaction_id) = 1 THEN 1
                ELSE (julianday(MAX(t.transaction_date)) - julianday(MIN(t.transaction_date))) / 30.0 + 1
           END as months_active
    FROM customers c JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.customer_id, c.acquisition_channel
)
-- 이후 채널별로 집계하고 CAC와 JOIN""",
        answer_query="""
WITH customer_monthly AS (
    SELECT
        c.customer_id,
        c.acquisition_channel as channel,
        SUM(t.amount) as total_revenue,
        CASE
            WHEN COUNT(t.transaction_id) = 1 THEN 1
            ELSE (julianday(MAX(t.transaction_date)) - julianday(MIN(t.transaction_date))) / 30.0 + 1
        END as months_active
    FROM customers c
    JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.customer_id, c.acquisition_channel
),
channel_monthly AS (
    SELECT
        channel,
        ROUND(AVG(total_revenue / months_active), 2) as monthly_revenue_per_customer
    FROM customer_monthly
    GROUP BY channel
),
channel_cac AS (
    SELECT
        channel,
        ROUND(SUM(spend) * 1.0 / SUM(conversions), 2) as cac
    FROM campaigns
    GROUP BY channel
)
SELECT
    m.channel,
    m.monthly_revenue_per_customer,
    c.cac,
    ROUND(c.cac / m.monthly_revenue_per_customer, 1) as payback_months
FROM channel_monthly m
JOIN channel_cac c ON m.channel = c.channel
ORDER BY payback_months ASC
""",
        explanation="""
        **Payback Period**는 고객 획득 비용을 회수하는 데 걸리는 시간입니다.

        계산: Payback = CAC / 월평균 매출

        해석:
        - **6개월 미만**: 매우 좋음
        - **6~12개월**: 양호
        - **12개월 이상**: 현금 흐름 관리 필요

        Payback이 짧을수록 빠르게 재투자가 가능합니다.
        """,
        interview_tip="""
        **Q: Payback Period가 뭔가요? 왜 중요한가요?**

        "Payback Period는 고객 획득 비용(CAC)을 회수하는 데 걸리는 시간입니다.

        예를 들어 CAC가 6만원이고 고객이 월 2만원을 쓴다면,
        Payback은 3개월입니다.

        이게 중요한 이유는 **현금 흐름** 때문입니다.
        Payback이 12개월이면, 고객 획득 비용을 1년 동안 회수하지 못하는 거죠.
        그 기간 동안 회사는 현금이 묶여있게 됩니다.

        스타트업에서는 Payback을 6개월 이하로 유지하려고 합니다.
        그래야 마케팅 예산을 빠르게 재투자할 수 있거든요."
        """,
        difficulty=3
    ),
    Question(
        id="ltv_5",
        title="Q5. 채널별 마케팅 ROI 분석",
        description="""
        **상황:** 이사회에서 마케팅 투자 대비 수익률을 보고해야 합니다.
        단순히 "어떤 채널이 좋다"가 아니라, 정확한 ROI 수치가 필요합니다.

        **과제:** 채널별 마케팅 ROI를 계산하세요.

        **공식:** ROI = (LTV - CAC) / CAC × 100

        **테이블:**
        - `customers` (customer_id, acquisition_channel)
        - `transactions` (customer_id, amount)
        - `campaigns` (channel, spend, conversions)

        **요구사항:**
        - 채널별 총 매출, 총 비용, 총 고객 수
        - LTV, CAC, ROI 계산
        - 결과 컬럼: `channel`, `total_revenue`, `total_cost`, `customers`, `ltv`, `cac`, `roi_percent`
        - ROI가 높은 순으로 정렬
        """,
        hint="""ROI = (LTV - CAC) / CAC × 100
채널별 총 매출과 총 비용을 각각 구해야 합니다.
---
필요한 CTE:
1) channel_revenue: 채널별 총 매출, 고객 수
2) channel_cost: 채널별 총 비용, 획득 고객 수
---
WITH channel_revenue AS (
    SELECT c.acquisition_channel as channel,
           COUNT(DISTINCT c.customer_id) as customers,
           SUM(t.amount) as total_revenue
    FROM customers c JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.acquisition_channel
),
channel_cost AS (
    SELECT channel, SUM(spend) as total_cost, SUM(conversions) as acquired_customers
    FROM campaigns GROUP BY channel
)
SELECT r.channel, r.total_revenue, c.total_cost, r.customers,
       ROUND(r.total_revenue * 1.0 / r.customers, 2) as ltv,
       ROUND(c.total_cost * 1.0 / c.acquired_customers, 2) as cac,
       ROUND(((ltv - cac) / cac) * 100, 1) as roi_percent
FROM channel_revenue r JOIN channel_cost c ON r.channel = c.channel""",
        answer_query="""
WITH channel_revenue AS (
    SELECT
        c.acquisition_channel as channel,
        COUNT(DISTINCT c.customer_id) as customers,
        SUM(t.amount) as total_revenue
    FROM customers c
    JOIN transactions t ON c.customer_id = t.customer_id
    GROUP BY c.acquisition_channel
),
channel_cost AS (
    SELECT
        channel,
        SUM(spend) as total_cost,
        SUM(conversions) as acquired_customers
    FROM campaigns
    GROUP BY channel
)
SELECT
    r.channel,
    r.total_revenue,
    c.total_cost,
    r.customers,
    ROUND(r.total_revenue * 1.0 / r.customers, 2) as ltv,
    ROUND(c.total_cost * 1.0 / c.acquired_customers, 2) as cac,
    ROUND(((r.total_revenue * 1.0 / r.customers) - (c.total_cost * 1.0 / c.acquired_customers)) / (c.total_cost * 1.0 / c.acquired_customers) * 100, 1) as roi_percent
FROM channel_revenue r
JOIN channel_cost c ON r.channel = c.channel
ORDER BY roi_percent DESC
""",
        explanation="""
        **마케팅 ROI**는 마케팅 투자 대비 수익률입니다.

        ROI = (LTV - CAC) / CAC × 100

        해석:
        - **200% 이상**: 매우 효율적
        - **100~200%**: 양호
        - **0~100%**: 개선 필요
        - **0% 미만**: 적자

        ROI가 높은 채널에 예산을 집중하는 것이 기본 전략입니다.
        """,
        interview_tip="""
        **Q: 마케팅 ROI는 어떻게 계산하나요?**

        "마케팅 ROI는 (LTV - CAC) / CAC × 100으로 계산합니다.

        예를 들어 LTV가 10만원이고 CAC가 3만원이면:
        ROI = (10만 - 3만) / 3만 × 100 = 233%

        이는 1원을 투자해서 2.33원의 순이익을 얻는다는 의미입니다.

        ROI 분석 시 주의할 점:
        1. **시간 프레임**: LTV는 장기, CAC는 단기이므로 비교 기간을 맞춰야 함
        2. **귀속 모델**: 어떤 마케팅이 전환에 기여했는지 정의 필요
        3. **증분 효과**: 마케팅 없이도 오는 고객(Organic)을 구분해야 함

        단순 ROI보다 이런 요소들을 고려한 분석이 더 정확합니다."
        """,
        difficulty=3
    ),
]


def show_ltv_cac_module():
    """LTV & CAC 모듈 메인"""

    st.title("💰 LTV & CAC 분석")

    st.markdown("""
    > **LTV**(Customer Lifetime Value)와 **CAC**(Customer Acquisition Cost)는
    > 비즈니스 건전성을 판단하는 가장 중요한 지표입니다.
    """)

    # 개념 카드
    with st.expander("📚 핵심 개념 보기", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            ### LTV (Customer Lifetime Value)

            고객 한 명이 전체 기간 동안 창출하는 총 가치

            **계산 방법:**
            - Historical LTV = 고객별 총 매출의 평균
            - Predictive LTV = ARPU × 활동 기간 × 마진율

            **활용:**
            - 고객 가치 세그먼트 정의
            - 마케팅 예산 상한선 설정
            - VIP 프로그램 기준
            """)

        with col2:
            st.markdown("""
            ### CAC (Customer Acquisition Cost)

            신규 고객 한 명을 획득하는 데 드는 비용

            **계산 방법:**
            - CAC = 마케팅 비용 / 신규 고객 수

            **활용:**
            - 채널별 효율성 비교
            - 마케팅 예산 배분
            - Unit Economics 분석
            """)

        st.divider()

        st.markdown("""
        ### LTV:CAC 비율

        | 비율 | 해석 | 액션 |
        |------|------|------|
        | **3:1 이상** | 건전함 | 성장 투자 확대 |
        | **1:1 ~ 3:1** | 주의 필요 | 효율화 필요 |
        | **1:1 미만** | 적자 | 즉시 개선 필요 |
        | **10:1 이상** | 과소 투자 | 마케팅 확대 검토 |
        """)

    st.divider()

    # 문제 선택
    question_titles = [f"{q.title}" for q in QUESTIONS]
    selected_idx = st.selectbox(
        "문제 선택",
        range(len(QUESTIONS)),
        format_func=lambda x: question_titles[x]
    )

    st.divider()

    # 선택된 문제 표시
    selected_question = QUESTIONS[selected_idx]
    card = QuestionCard(selected_question, "ltv_cac")
    card.render()
