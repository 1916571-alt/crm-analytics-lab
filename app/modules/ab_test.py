"""
모듈 5: A/B 테스트 분석 (고급)
"""

import streamlit as st
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from components.question_card import QuestionCard, Question


QUESTIONS = [
    Question(
        id="ab_1",
        title="Q1. 그룹별 전환율 계산",
        description="""
        **상황:** Product팀에서 새로운 UI를 테스트하고 있습니다.
        기존 UI(Control)와 새 UI(Treatment)의 전환율을 비교해달라는 요청입니다.

        **과제:** A/B 테스트의 Control과 Treatment 그룹별 전환율을 계산하세요.

        **시나리오:**
        - events 테이블의 device 컬럼을 실험 그룹으로 활용
        - desktop = Control (기존 UI)
        - mobile = Treatment (새 UI)
        - 목표: purchase 전환율 비교

        **요구사항:**
        - 그룹별 전체 사용자 수 (page_view 기준)
        - 그룹별 전환 사용자 수 (purchase 기준)
        - 전환율 (%)
        - 결과 컬럼: variant, users, conversions, conversion_rate
        """,
        hint="""
        **힌트:**
        1. device를 variant로 변환 (desktop=control, mobile=treatment)
        2. page_view 이벤트로 전체 사용자 수 계산
        3. purchase 이벤트로 전환 사용자 수 계산

        ```sql
        SELECT
            CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
            COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as users,
            ...
        ```
        """,
        answer_query="""
SELECT
    CASE device
        WHEN 'desktop' THEN 'control'
        ELSE 'treatment'
    END as variant,
    COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as users,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as conversions,
    ROUND(
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 100.0 /
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END),
        2
    ) as conversion_rate
FROM events
WHERE event_type IN ('page_view', 'purchase')
GROUP BY
    CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
""",
        explanation="""
        **기본 A/B 분석**의 첫 단계는 그룹별 전환율 계산입니다.

        CASE WHEN으로 조건부 집계:
        - 전체 사용자: page_view 이벤트 발생 사용자
        - 전환 사용자: purchase 이벤트 발생 사용자

        전환율 = 전환 사용자 / 전체 사용자 × 100
        """,
        interview_tip="""
        **Q: A/B 테스트란 무엇인가요?**

        A/B 테스트는 두 가지 버전(A와 B)을 무작위로 사용자에게 보여주고, 어떤 버전이 더 좋은 성과를 내는지 비교하는 실험 방법입니다.

        핵심 구성요소:
        - **Control (A)**: 기존 버전 (변화 없음)
        - **Treatment (B)**: 새로운 버전 (변화 적용)
        - **무작위 배정**: 편향 없이 사용자를 그룹에 배정
        - **성과 지표**: 전환율, 클릭률, 매출 등

        A/B 테스트가 중요한 이유:
        - **데이터 기반 의사결정**: 직관이 아닌 증거에 기반
        - **리스크 최소화**: 전체 적용 전 소규모 테스트
        - **인과관계 확인**: 상관관계가 아닌 인과관계 검증
        """,
        difficulty=1
    ),
    Question(
        id="ab_2",
        title="Q2. Uplift 계산",
        description="""
        **상황:** 경영진에게 실험 결과를 보고해야 합니다.
        "새 UI가 얼마나 더 좋은가요?"라는 질문에 명확히 답해야 합니다.

        **과제:** Treatment의 전환율이 Control 대비 몇 % 개선되었는지 계산하세요.

        **Uplift** = (Treatment 전환율 - Control 전환율) / Control 전환율 × 100

        **요구사항:**
        - Control 전환율
        - Treatment 전환율
        - 절대적 차이 (difference_pp: percentage point)
        - 상대적 개선 (uplift_percent)
        """,
        hint="""
        **힌트:**
        1. 먼저 그룹별 전환율을 계산하는 CTE
        2. 두 그룹의 값을 한 행에서 비교

        ```sql
        WITH group_rates AS (
            SELECT variant, conversion_rate FROM ...
        )
        SELECT
            (SELECT conversion_rate FROM group_rates WHERE variant = 'treatment') -
            (SELECT conversion_rate FROM group_rates WHERE variant = 'control') as difference
        ```
        """,
        answer_query="""
WITH group_stats AS (
    SELECT
        CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as users,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as conversions,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 100.0 /
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as conversion_rate
    FROM events
    WHERE event_type IN ('page_view', 'purchase')
    GROUP BY CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
)
SELECT
    (SELECT conversion_rate FROM group_stats WHERE variant = 'control') as control_rate,
    (SELECT conversion_rate FROM group_stats WHERE variant = 'treatment') as treatment_rate,
    ROUND(
        (SELECT conversion_rate FROM group_stats WHERE variant = 'treatment') -
        (SELECT conversion_rate FROM group_stats WHERE variant = 'control'),
        2
    ) as difference_pp,
    ROUND(
        ((SELECT conversion_rate FROM group_stats WHERE variant = 'treatment') -
         (SELECT conversion_rate FROM group_stats WHERE variant = 'control')) * 100.0 /
        (SELECT conversion_rate FROM group_stats WHERE variant = 'control'),
        1
    ) as uplift_percent
""",
        explanation="""
        **Uplift**는 Treatment가 Control 대비 얼마나 개선되었는지 나타냅니다.

        - **절대적 차이 (pp)**: 전환율 차이 (예: 2.5% - 2.1% = 0.4%p)
        - **상대적 개선 (%)**: 비율 개선 (예: 0.4 / 2.1 × 100 = 19%)

        상대적 개선이 실무에서 더 많이 사용됩니다.
        "전환율이 19% 개선되었다"
        """,
        interview_tip="""
        **Q: Uplift(상승률)란 무엇이고, 절대적 차이와 어떻게 다른가요?**

        Uplift는 Treatment가 Control 대비 얼마나 개선되었는지를 비율로 나타낸 것입니다.

        두 가지 표현 방식:
        - **절대적 차이 (Percentage Point, pp)**: 2.5% - 2.1% = 0.4%p
        - **상대적 개선 (Uplift %)**: 0.4 / 2.1 x 100 = 19%

        어떤 것을 써야 하나요?
        - **비즈니스 보고**: 상대적 개선이 더 직관적 ("전환율이 19% 개선")
        - **임팩트 계산**: 절대적 차이가 필요 (방문자 100만 x 0.4%p = 4,000건 추가 전환)

        주의: 기준 전환율이 낮으면 상대적 개선은 커 보이지만 절대적 영향은 작을 수 있음
        """,
        difficulty=2
    ),
    Question(
        id="ab_3",
        title="Q3. Pooled 전환율과 Standard Error 계산",
        description="""
        **상황:** 전환율 차이가 우연인지 실제 효과인지 판단해야 합니다.
        통계적 유의성 검정을 위한 기초 계산이 필요합니다.

        **과제:** Z-검정을 위한 Pooled 전환율과 Standard Error를 계산하세요.

        **공식:**
        - p_pool = (x1 + x2) / (n1 + n2)
        - SE = sqrt(p_pool x (1 - p_pool) x (1/n1 + 1/n2))

        **요구사항:**
        - n1, n2: 각 그룹 사용자 수
        - x1, x2: 각 그룹 전환 수
        - p_pool: 통합 전환율
        - standard_error: 표준 오차
        """,
        hint="""
        **힌트:**
        1. 그룹별 n, x 계산
        2. p_pool = (x1 + x2) / (n1 + n2)
        3. SE 계산 (SQRT 함수 사용)

        ```sql
        SQRT(p_pool * (1 - p_pool) * (1.0/n1 + 1.0/n2))
        ```
        """,
        answer_query="""
WITH group_stats AS (
    SELECT
        CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as n,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as x
    FROM events
    WHERE event_type IN ('page_view', 'purchase')
    GROUP BY CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
),
stats AS (
    SELECT
        MAX(CASE WHEN variant = 'control' THEN n END) as n1,
        MAX(CASE WHEN variant = 'control' THEN x END) as x1,
        MAX(CASE WHEN variant = 'treatment' THEN n END) as n2,
        MAX(CASE WHEN variant = 'treatment' THEN x END) as x2
    FROM group_stats
)
SELECT
    n1,
    x1,
    n2,
    x2,
    ROUND((x1 + x2) * 1.0 / (n1 + n2), 6) as p_pool,
    ROUND(
        SQRT(
            ((x1 + x2) * 1.0 / (n1 + n2)) *
            (1 - (x1 + x2) * 1.0 / (n1 + n2)) *
            (1.0 / n1 + 1.0 / n2)
        ),
        6
    ) as standard_error
FROM stats
""",
        explanation="""
        **Pooled 전환율**은 두 그룹을 합쳐서 계산한 전환율입니다.
        귀무가설(두 그룹이 같다) 하에서의 예상 전환율입니다.

        **Standard Error(표준 오차)**는 전환율 차이의 불확실성을 나타냅니다.
        SE가 작을수록 측정이 정확합니다.

        이 두 값이 Z-score 계산에 사용됩니다.
        """,
        interview_tip="""
        **Q: A/B 테스트에서 Standard Error(표준 오차)란 무엇인가요?**

        Standard Error는 관찰된 전환율 차이가 가질 수 있는 불확실성(변동성)을 측정한 값입니다.

        직관적 이해:
        - SE가 크다 = 측정이 불확실하다 (샘플이 적거나 분산이 크다)
        - SE가 작다 = 측정이 정확하다 (샘플이 충분하다)

        SE에 영향을 미치는 요인:
        - **샘플 크기**: 클수록 SE 감소
        - **기준 전환율**: 50%에 가까울수록 SE 증가
        - **그룹 간 크기 차이**: 균형 잡힐수록 SE 감소

        Z-score = (전환율 차이) / SE 이므로, SE가 작아야 작은 차이도 유의하게 감지 가능
        """,
        difficulty=2
    ),
    Question(
        id="ab_4",
        title="Q4. Z-score 계산",
        description="""
        **상황:** 경영진에게 "이 결과가 통계적으로 유의한가요?"라는 질문을 받았습니다.
        Z-검정을 통해 명확한 답을 제시해야 합니다.

        **과제:** Two-Proportion Z-Test의 Z-score를 계산하세요.

        **공식:**
        Z = (p2 - p1) / SE

        여기서:
        - p1: Control 전환율
        - p2: Treatment 전환율
        - SE: Standard Error (이전 문제에서 계산)

        **요구사항:**
        - 모든 중간 계산값 포함
        - Z-score 계산
        - Z > 1.96이면 유의 (95% 신뢰수준)
        """,
        hint="""
        **힌트:**
        이전 문제의 결과를 확장하여
        Z = (p2 - p1) / SE 계산

        ```sql
        (p2 - p1) / standard_error as z_score
        ```
        """,
        answer_query="""
WITH group_stats AS (
    SELECT
        CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as n,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as x,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 1.0 /
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as p
    FROM events
    WHERE event_type IN ('page_view', 'purchase')
    GROUP BY CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
),
stats AS (
    SELECT
        MAX(CASE WHEN variant = 'control' THEN n END) as n1,
        MAX(CASE WHEN variant = 'control' THEN x END) as x1,
        MAX(CASE WHEN variant = 'control' THEN p END) as p1,
        MAX(CASE WHEN variant = 'treatment' THEN n END) as n2,
        MAX(CASE WHEN variant = 'treatment' THEN x END) as x2,
        MAX(CASE WHEN variant = 'treatment' THEN p END) as p2
    FROM group_stats
),
with_pooled AS (
    SELECT
        *,
        (x1 + x2) * 1.0 / (n1 + n2) as p_pool
    FROM stats
),
with_se AS (
    SELECT
        *,
        SQRT(p_pool * (1 - p_pool) * (1.0/n1 + 1.0/n2)) as se
    FROM with_pooled
)
SELECT
    ROUND(p1 * 100, 2) as control_rate_pct,
    ROUND(p2 * 100, 2) as treatment_rate_pct,
    ROUND(p_pool, 6) as pooled_rate,
    ROUND(se, 6) as standard_error,
    ROUND((p2 - p1) / se, 4) as z_score,
    CASE WHEN ABS((p2 - p1) / se) > 1.96 THEN 'Significant' ELSE 'Not Significant' END as result
FROM with_se
""",
        explanation="""
        **Z-score**는 관찰된 차이가 표준 오차의 몇 배인지를 나타냅니다.

        해석:
        - |Z| > 1.96 → 95% 신뢰수준에서 유의
        - |Z| > 2.58 → 99% 신뢰수준에서 유의

        Z-score가 클수록 두 그룹 간 차이가 확실합니다.
        """,
        interview_tip="""
        **Q: 통계적 유의성(Statistical Significance)이란 무엇인가요?**

        통계적 유의성은 "관찰된 차이가 우연에 의한 것이 아니다"라고 말할 수 있는 확신의 정도입니다.

        핵심 개념:
        - **귀무가설(H0)**: 두 그룹에 차이가 없다 (Treatment 효과 없음)
        - **대립가설(H1)**: 두 그룹에 차이가 있다 (Treatment 효과 있음)
        - **Z-score**: 관찰된 차이가 우연으로 발생하기 얼마나 어려운지

        판단 기준 (95% 신뢰수준):
        - |Z| > 1.96: 유의함 (우연일 확률 5% 미만)
        - |Z| <= 1.96: 유의하지 않음 (우연일 수 있음)

        주의: "유의하지 않음" = "효과가 없다"가 아니라 "판단할 수 없다"
        """,
        difficulty=3
    ),
    Question(
        id="ab_5",
        title="Q5. 필요 샘플 사이즈 계산",
        description="""
        **상황:** 새로운 A/B 테스트를 시작하기 전에 실험 기간을 정해야 합니다.
        "얼마나 오래 실험해야 하나요?"라는 질문에 답하려면 필요 샘플 수를 알아야 합니다.

        **과제:** 20% 상대적 개선을 감지하기 위한 필요 샘플 사이즈를 계산하세요.

        **공식:**
        n = 2 x ((Z_a + Z_b)^2 x p x (1-p)) / (MDE)^2

        **파라미터:**
        - Z_a = 1.96 (95% 신뢰수준)
        - Z_b = 0.84 (80% 검정력)
        - p = 현재 전환율 (Control 기준)
        - MDE = p x 0.2 (20% 상대적 개선)

        **요구사항:**
        - 현재 Control 전환율
        - MDE (절대값)
        - 필요 샘플 사이즈 (그룹당)
        """,
        hint="""
        **힌트:**
        1. Control 전환율 계산
        2. MDE = 전환율 × 0.2
        3. 공식 대입

        SQLite에서는 POWER 함수 대신 곱셈 사용
        ```sql
        2 * ((1.96 + 0.84) * (1.96 + 0.84) * p * (1-p)) / (mde * mde)
        ```
        """,
        answer_query="""
WITH control_rate AS (
    SELECT
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 1.0 /
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as p
    FROM events
    WHERE device = 'desktop'
      AND event_type IN ('page_view', 'purchase')
)
SELECT
    ROUND(p * 100, 2) as control_rate_pct,
    ROUND(p * 0.2 * 100, 3) as mde_pct,
    ROUND(
        2 * (
            (1.96 + 0.84) * (1.96 + 0.84) * p * (1 - p)
        ) / (
            (p * 0.2) * (p * 0.2)
        ),
        0
    ) as required_sample_per_group,
    ROUND(
        2 * 2 * (
            (1.96 + 0.84) * (1.96 + 0.84) * p * (1 - p)
        ) / (
            (p * 0.2) * (p * 0.2)
        ),
        0
    ) as total_required_sample
FROM control_rate
""",
        explanation="""
        **샘플 사이즈 계산**은 실험 설계의 핵심입니다.

        영향을 미치는 요소:
        - **기준 전환율(p)**: 낮을수록 더 많은 샘플 필요
        - **MDE**: 작은 차이를 감지하려면 더 많은 샘플 필요
        - **신뢰수준(α)**: 높을수록 더 많은 샘플 필요
        - **검정력(1-β)**: 높을수록 더 많은 샘플 필요

        실험 전에 반드시 계산해야 합니다.
        """,
        interview_tip="""
        **Q: A/B 테스트에서 필요 샘플 사이즈는 어떻게 결정하나요?**

        필요 샘플 사이즈는 실험 설계의 핵심이며, 실험 시작 전에 반드시 계산해야 합니다.

        영향을 미치는 4가지 요소:
        - **기준 전환율(p)**: 낮을수록 더 많은 샘플 필요 (2% vs 20%)
        - **MDE(Minimum Detectable Effect)**: 감지하려는 최소 차이, 작을수록 더 많은 샘플 필요
        - **신뢰수준(1-alpha)**: 보통 95%, 높을수록 더 많은 샘플 필요
        - **검정력(1-beta, Power)**: 보통 80%, 높을수록 더 많은 샘플 필요

        실무 적용:
        - 필요 샘플 / 일일 트래픽 = 필요 실험 기간
        - 주말 효과, 계절성 고려하여 기간 조정
        - 샘플이 부족하면 MDE를 높이거나 검정력을 낮추는 트레이드오프
        """,
        difficulty=3
    ),
    Question(
        id="ab_6",
        title="Q6. 세그먼트별 실험 효과 분석",
        description="""
        **상황:** 전체 결과만 보면 Treatment가 좋아 보이지만, 채널별로 다를 수 있습니다.
        "모든 채널에서 효과가 있나요?"라는 질문에 답해야 합니다.

        **과제:** 채널별로 실험 효과가 다른지 분석하세요.

        **요구사항:**
        - 채널 x 실험그룹별 전환율
        - 채널별 Uplift
        - 결과 컬럼: channel, control_rate, treatment_rate, uplift_pct
        """,
        hint="""
        **힌트:**
        채널과 디바이스(실험그룹)로 그룹화한 후
        PIVOT 형태로 변환

        ```sql
        MAX(CASE WHEN variant = 'control' THEN rate END) as control_rate,
        MAX(CASE WHEN variant = 'treatment' THEN rate END) as treatment_rate
        ```
        """,
        answer_query="""
WITH segment_stats AS (
    SELECT
        channel,
        CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as users,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as conversions,
        ROUND(
            COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 100.0 /
            NULLIF(COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END), 0),
            2
        ) as rate
    FROM events
    WHERE event_type IN ('page_view', 'purchase')
    GROUP BY channel, CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
)
SELECT
    channel,
    MAX(CASE WHEN variant = 'control' THEN rate END) as control_rate,
    MAX(CASE WHEN variant = 'treatment' THEN rate END) as treatment_rate,
    ROUND(
        (MAX(CASE WHEN variant = 'treatment' THEN rate END) -
         MAX(CASE WHEN variant = 'control' THEN rate END)) * 100.0 /
        NULLIF(MAX(CASE WHEN variant = 'control' THEN rate END), 0),
        1
    ) as uplift_pct
FROM segment_stats
GROUP BY channel
ORDER BY uplift_pct DESC
""",
        explanation="""
        **세그먼트별 분석**으로 숨겨진 인사이트를 발견합니다.

        주의: **Simpson's Paradox**
        - 전체에서는 Treatment가 좋아 보이지만
        - 모든 세그먼트에서는 Control이 더 좋을 수 있음

        반드시 세그먼트별 분석을 함께 수행해야 합니다.
        """,
        interview_tip="""
        **Q: A/B 테스트에서 세그먼트별 분석이 왜 중요한가요?**

        세그먼트별 분석은 전체 결과에 숨겨진 패턴을 발견하고, 잘못된 의사결정을 방지합니다.

        중요한 이유:
        - **Simpson's Paradox 방지**: 전체에서는 Treatment가 좋아 보이지만, 모든 세그먼트에서 Control이 더 좋을 수 있음
        - **이질적 효과(Heterogeneous Treatment Effect) 발견**: 일부 세그먼트에서만 효과가 있을 수 있음
        - **최적 적용 범위 결정**: 모든 사용자가 아닌 특정 세그먼트에만 적용

        일반적인 분석 세그먼트:
        - 채널 (Organic vs Paid)
        - 고객 유형 (신규 vs 기존)
        - 디바이스 (Mobile vs Desktop)
        - 지역/국가
        """,
        difficulty=3
    ),
    Question(
        id="ab_7",
        title="Q7. 일별 전환율 추이 분석",
        description="""
        **상황:** 실험 결과가 안정적인지 확인해야 합니다.
        "결과가 시간이 지나도 유지되나요?"라는 질문에 답해야 합니다.

        **과제:** 실험 기간 동안 일별 전환율 추이를 분석하세요.

        **목적:**
        - 결과의 안정성 확인
        - Novelty Effect 감지
        - 외부 요인 영향 확인

        **요구사항:**
        - 일별, 그룹별 전환율
        - 결과 컬럼: date, control_rate, treatment_rate, difference
        """,
        hint="""
        **힌트:**
        날짜와 실험그룹으로 그룹화한 후 PIVOT

        ```sql
        GROUP BY date(event_date), variant
        ```
        """,
        answer_query="""
WITH daily_stats AS (
    SELECT
        date(event_date) as date,
        CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as users,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as conversions,
        ROUND(
            COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 100.0 /
            NULLIF(COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END), 0),
            2
        ) as rate
    FROM events
    WHERE event_type IN ('page_view', 'purchase')
    GROUP BY date(event_date), CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
)
SELECT
    date,
    MAX(CASE WHEN variant = 'control' THEN rate END) as control_rate,
    MAX(CASE WHEN variant = 'treatment' THEN rate END) as treatment_rate,
    ROUND(
        MAX(CASE WHEN variant = 'treatment' THEN rate END) -
        MAX(CASE WHEN variant = 'control' THEN rate END),
        2
    ) as difference
FROM daily_stats
GROUP BY date
ORDER BY date
LIMIT 14
""",
        explanation="""
        **일별 추이 분석**으로 결과의 신뢰성을 검증합니다.

        확인 포인트:
        1. **Novelty Effect**: 초기에만 효과가 크고 감소하는 패턴
        2. **외부 요인**: 특정 날짜에 급격한 변동
        3. **안정성**: 일별 차이가 일관되게 유지되는지

        차이가 날마다 크게 변동하면 결과를 신뢰하기 어렵습니다.
        """,
        interview_tip="""
        **Q: A/B 테스트에서 Novelty Effect(신기함 효과)란 무엇인가요?**

        Novelty Effect는 사용자가 새로운 것에 일시적으로 더 많이 반응하는 현상입니다. 시간이 지나면 효과가 감소합니다.

        발생 원인:
        - 새로운 UI에 대한 호기심
        - 변화 자체에 대한 관심
        - 학습 효과 (새 UI 적응 후 효과 변화)

        감지 방법:
        - 일별 전환율 추이 분석
        - 초기 며칠과 이후 기간 비교
        - 신규 vs 기존 사용자 별도 분석

        대응 방법:
        - 충분히 긴 실험 기간 (최소 2주 권장)
        - 초기 데이터 제외 후 재분석
        - 장기 리텐션 지표도 함께 측정
        """,
        difficulty=3
    ),
    Question(
        id="ab_8",
        title="Q8. 신규/기존 고객별 효과 분석",
        description="""
        **상황:** 새 UI가 모든 고객에게 효과적인지 확인해야 합니다.
        기존 고객은 변화에 저항할 수 있으므로 별도 분석이 필요합니다.

        **과제:** 신규 고객과 기존 고객에게 실험 효과가 다른지 분석하세요.

        **정의:**
        - 신규 고객: 실험 기간 중 첫 구매
        - 기존 고객: 이전 구매 이력 있음

        **요구사항:**
        - customers와 transactions를 JOIN하여 고객 유형 판별
        - 고객 유형별 실험 효과
        """,
        hint="""
        **힌트:**
        1. 고객별 첫 구매일 확인
        2. 실험 기간(2024-06) 내 첫 구매면 신규
        3. 그 전에 구매 이력이 있으면 기존

        ```sql
        CASE
            WHEN MIN(transaction_date) >= '2024-06-01' THEN 'new'
            ELSE 'returning'
        END as customer_type
        ```
        """,
        answer_query="""
WITH customer_type AS (
    SELECT
        customer_id,
        CASE
            WHEN MIN(transaction_date) >= '2024-06-01' THEN 'new'
            ELSE 'returning'
        END as cust_type
    FROM transactions
    GROUP BY customer_id
),
event_with_type AS (
    SELECT
        e.*,
        COALESCE(ct.cust_type, 'new') as customer_type
    FROM events e
    LEFT JOIN customer_type ct ON e.user_id = ct.customer_id
    WHERE e.event_type IN ('page_view', 'purchase')
),
segment_stats AS (
    SELECT
        customer_type,
        CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as users,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as conversions,
        ROUND(
            COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 100.0 /
            NULLIF(COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END), 0),
            2
        ) as rate
    FROM event_with_type
    GROUP BY customer_type, CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
)
SELECT
    customer_type,
    MAX(CASE WHEN variant = 'control' THEN rate END) as control_rate,
    MAX(CASE WHEN variant = 'treatment' THEN rate END) as treatment_rate,
    ROUND(
        (MAX(CASE WHEN variant = 'treatment' THEN rate END) -
         MAX(CASE WHEN variant = 'control' THEN rate END)) * 100.0 /
        NULLIF(MAX(CASE WHEN variant = 'control' THEN rate END), 0),
        1
    ) as uplift_pct
FROM segment_stats
GROUP BY customer_type
""",
        explanation="""
        **고객 유형별 분석**은 중요한 세그먼트 분석입니다.

        일반적인 패턴:
        - 신규 고객: 새 경험에 더 개방적
        - 기존 고객: 기존 경험에 익숙, 변화에 저항

        Treatment가 신규에게만 효과적이라면,
        점진적 롤아웃이 필요할 수 있습니다.
        """,
        interview_tip="""
        **Q: 신규 vs 기존 고객 분석이 A/B 테스트에서 중요한 이유는 무엇인가요?**

        신규/기존 고객 분석은 실험 결과의 적용 범위를 결정하는 데 핵심적입니다.

        일반적인 패턴:
        - **신규 고객**: 새 경험에 개방적, 기존 UI에 대한 학습이 없음
        - **기존 고객**: 기존 UI에 익숙, 변화에 저항 (Change Aversion)

        의사결정 시나리오:
        - 둘 다 긍정적 -> 전체 적용
        - 신규만 긍정적 -> 신규에게만 적용, 기존은 점진적 전환
        - 기존만 긍정적 -> 데이터 재검토 필요 (드문 케이스)
        - 둘 다 부정적 -> 기각

        점진적 롤아웃 전략:
        1. 신규 고객에게 먼저 적용
        2. 시간이 지나면 그들이 "기존 고객"이 됨
        3. 자연스럽게 새 UI 사용자 비중 증가
        """,
        difficulty=4
    ),
    Question(
        id="ab_9",
        title="Q9. 전환 가치 분석 (Revenue per User)",
        description="""
        **상황:** 전환율만 보면 오해할 수 있습니다. "매출은 얼마나 늘어나나요?"라는
        질문에 답하려면 객단가까지 고려해야 합니다.

        **과제:** 전환율뿐 아니라 사용자당 매출(RPU)도 비교하세요.

        **목적:**
        - 전환율은 높지만 객단가가 낮을 수 있음
        - Revenue 기준 총 효과 측정

        **요구사항:**
        - 그룹별 전환율
        - 그룹별 평균 객단가 (구매자 기준)
        - 그룹별 RPU (전체 사용자 기준)
        """,
        hint="""
        **힌트:**
        1. events와 transactions를 JOIN
        2. 전환율, 객단가, RPU 각각 계산

        RPU = 총 매출 / 전체 사용자 수
        """,
        answer_query="""
WITH user_revenue AS (
    SELECT
        e.user_id,
        e.device,
        MAX(CASE WHEN e.event_type = 'page_view' THEN 1 ELSE 0 END) as visited,
        MAX(CASE WHEN e.event_type = 'purchase' THEN 1 ELSE 0 END) as converted,
        COALESCE(SUM(t.amount), 0) as revenue
    FROM events e
    LEFT JOIN transactions t ON e.user_id = t.customer_id
        AND date(e.event_date) = date(t.transaction_date)
    WHERE e.event_type IN ('page_view', 'purchase')
    GROUP BY e.user_id, e.device
)
SELECT
    CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
    COUNT(DISTINCT CASE WHEN visited = 1 THEN user_id END) as total_users,
    COUNT(DISTINCT CASE WHEN converted = 1 THEN user_id END) as converters,
    ROUND(
        COUNT(DISTINCT CASE WHEN converted = 1 THEN user_id END) * 100.0 /
        COUNT(DISTINCT CASE WHEN visited = 1 THEN user_id END),
        2
    ) as conversion_rate,
    ROUND(SUM(revenue) * 1.0 / NULLIF(COUNT(DISTINCT CASE WHEN converted = 1 THEN user_id END), 0), 0) as avg_order_value,
    ROUND(SUM(revenue) * 1.0 / COUNT(DISTINCT CASE WHEN visited = 1 THEN user_id END), 0) as revenue_per_user
FROM user_revenue
GROUP BY CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
""",
        explanation="""
        **Revenue per User (RPU)**는 실험의 총 비즈니스 임팩트를 측정합니다.

        RPU = 전환율 × 평균 객단가

        가능한 시나리오:
        - 전환율↑ AOV↓ → RPU 변화 없음
        - 전환율↓ AOV↑ → RPU 증가 가능

        전환율만 보면 놓칠 수 있는 인사이트입니다.
        """,
        interview_tip="""
        **Q: A/B 테스트에서 전환율 외에 어떤 지표를 함께 봐야 하나요?**

        전환율만 보면 비즈니스 임팩트를 오해할 수 있습니다. 매출 관련 지표를 함께 분석해야 합니다.

        핵심 지표:
        - **전환율(CVR)**: 구매한 사용자 비율
        - **평균 객단가(AOV)**: 구매자 당 평균 금액
        - **사용자당 매출(RPU)**: 전체 사용자 당 평균 매출 = CVR x AOV

        왜 RPU가 중요한가:
        - 전환율 +20%, 객단가 -15% -> RPU +2% (효과가 적음)
        - 전환율 -5%, 객단가 +30% -> RPU +23% (오히려 좋음)

        결론: 전환율 최적화가 아니라 매출 최적화가 목표라면 RPU를 북극성 지표로 사용
        """,
        difficulty=4
    ),
    Question(
        id="ab_10",
        title="Q10. 종합 실험 리포트 생성",
        description="""
        **상황:** 경영진 회의에서 실험 결과를 발표해야 합니다.
        핵심 결과와 권고사항을 명확하게 전달하는 리포트가 필요합니다.

        **과제:** 실험 결과를 종합하는 최종 리포트를 생성하세요.

        **포함 내용:**
        - 실험 개요 (기간, 샘플 수)
        - 전환율 비교
        - 통계적 유의성
        - 세그먼트별 요약
        - 권고 사항
        """,
        hint="""
        **힌트:**
        여러 CTE를 조합하여 종합 리포트 생성

        ```sql
        WITH
            experiment_overview AS (...),
            conversion_stats AS (...),
            statistical_test AS (...),
            segment_summary AS (...)
        SELECT * FROM ...
        ```
        """,
        answer_query="""
WITH experiment_overview AS (
    SELECT
        MIN(date(event_date)) as start_date,
        MAX(date(event_date)) as end_date,
        COUNT(DISTINCT user_id) as total_users,
        COUNT(DISTINCT CASE WHEN device = 'desktop' THEN user_id END) as control_users,
        COUNT(DISTINCT CASE WHEN device != 'desktop' THEN user_id END) as treatment_users
    FROM events
    WHERE event_type = 'page_view'
),
group_stats AS (
    SELECT
        CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END as variant,
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as n,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) as x,
        COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) * 1.0 /
        COUNT(DISTINCT CASE WHEN event_type = 'page_view' THEN user_id END) as p
    FROM events
    WHERE event_type IN ('page_view', 'purchase')
    GROUP BY CASE device WHEN 'desktop' THEN 'control' ELSE 'treatment' END
),
stats AS (
    SELECT
        MAX(CASE WHEN variant = 'control' THEN n END) as n1,
        MAX(CASE WHEN variant = 'control' THEN x END) as x1,
        MAX(CASE WHEN variant = 'control' THEN p END) as p1,
        MAX(CASE WHEN variant = 'treatment' THEN n END) as n2,
        MAX(CASE WHEN variant = 'treatment' THEN x END) as x2,
        MAX(CASE WHEN variant = 'treatment' THEN p END) as p2
    FROM group_stats
),
z_test AS (
    SELECT
        *,
        (x1 + x2) * 1.0 / (n1 + n2) as p_pool,
        SQRT(((x1 + x2) * 1.0 / (n1 + n2)) * (1 - (x1 + x2) * 1.0 / (n1 + n2)) * (1.0/n1 + 1.0/n2)) as se,
        (p2 - p1) / SQRT(((x1 + x2) * 1.0 / (n1 + n2)) * (1 - (x1 + x2) * 1.0 / (n1 + n2)) * (1.0/n1 + 1.0/n2)) as z_score
    FROM stats
)
SELECT
    '=== A/B Test Report ===' as section,
    '' as metric,
    '' as value
UNION ALL
SELECT 'Overview', 'Experiment Period', eo.start_date || ' ~ ' || eo.end_date
FROM experiment_overview eo
UNION ALL
SELECT 'Overview', 'Total Users', CAST(eo.total_users AS TEXT)
FROM experiment_overview eo
UNION ALL
SELECT 'Results', 'Control Conversion Rate', ROUND(z.p1 * 100, 2) || '%'
FROM z_test z
UNION ALL
SELECT 'Results', 'Treatment Conversion Rate', ROUND(z.p2 * 100, 2) || '%'
FROM z_test z
UNION ALL
SELECT 'Results', 'Uplift', ROUND((z.p2 - z.p1) * 100 / z.p1, 1) || '%'
FROM z_test z
UNION ALL
SELECT 'Statistics', 'Z-Score', ROUND(z.z_score, 4)
FROM z_test z
UNION ALL
SELECT 'Statistics', 'Significant (95%)', CASE WHEN ABS(z.z_score) > 1.96 THEN 'YES' ELSE 'NO' END
FROM z_test z
UNION ALL
SELECT 'Recommendation', 'Action',
    CASE
        WHEN ABS(z.z_score) > 1.96 AND z.p2 > z.p1 THEN 'APPLY Treatment'
        WHEN ABS(z.z_score) > 1.96 AND z.p2 < z.p1 THEN 'KEEP Control'
        ELSE 'EXTEND Experiment'
    END
FROM z_test z
""",
        explanation="""
        **종합 리포트**는 의사결정자에게 명확한 결론을 전달합니다.

        포함 요소:
        1. **개요**: 실험 기간, 샘플 수
        2. **결과**: 전환율, Uplift
        3. **통계**: Z-score, 유의성
        4. **권고**: Apply / Keep / Extend

        SQL로 자동화하면 반복적인 리포팅이 효율화됩니다.
        """,
        interview_tip="""
        **Q: A/B 테스트 결과를 어떻게 보고하나요?**

        A/B 테스트 리포트는 의사결정자가 빠르게 판단할 수 있도록 구조화되어야 합니다.

        필수 포함 요소:
        1. **Executive Summary**: 1-2문장으로 결론 (적용/기각/연장)
        2. **실험 개요**: 기간, 샘플 수, 테스트 내용
        3. **핵심 결과**: 전환율, Uplift, 신뢰구간
        4. **통계적 유의성**: Z-score/p-value, 유의 여부
        5. **세그먼트 분석**: 주요 세그먼트별 결과
        6. **비즈니스 임팩트**: 예상 매출/비용 영향
        7. **권고사항**: 구체적인 다음 단계

        보고 원칙:
        - 결론을 먼저, 세부사항은 나중에
        - 숫자보다 인사이트에 집중
        - 불확실성과 한계점도 명시
        """,
        difficulty=4
    ),
]


def show_ab_test_module():
    """A/B 테스트 분석 모듈"""

    st.title("🧪 A/B 테스트 분석")

    st.markdown("""
    > **A/B 테스트**는 데이터 기반 의사결정의 핵심 도구입니다.
    > 통계적 유의성을 이해하고 올바르게 해석하는 것이 중요합니다.
    """)

    with st.expander("📚 핵심 개념 보기", expanded=False):
        st.markdown("""
        ### A/B 테스트 프로세스

        ```
        1. 가설 수립 → 2. 실험 설계 → 3. 실행 → 4. 분석 → 5. 의사결정
        ```

        ### 통계적 유의성

        | 지표 | 의미 | 기준 |
        |------|------|------|
        | p-value | 우연일 확률 | < 0.05 |
        | Z-score | 표준화된 차이 | > 1.96 |
        | 신뢰구간 | 효과의 범위 | 0 미포함 |

        ### 의사결정 매트릭스

        | 유의성 | 효과 방향 | 결정 |
        |--------|----------|------|
        | 유의 | Treatment 우세 | **적용** |
        | 유의 | Control 우세 | **기각** |
        | 비유의 | - | **연장/종료** |
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
    card = QuestionCard(selected_question, "ab_test")
    card.render()
