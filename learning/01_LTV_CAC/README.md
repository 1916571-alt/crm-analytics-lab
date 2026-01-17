# 01. LTV & CAC 분석

## 학습 목표

이 모듈을 완료하면 다음을 할 수 있습니다:

1. **LTV (Customer Lifetime Value)** 를 SQL로 계산할 수 있다
2. **CAC (Customer Acquisition Cost)** 를 SQL로 계산할 수 있다
3. **LTV:CAC 비율**로 비즈니스 건전성을 평가할 수 있다
4. 채널별, 세그먼트별 LTV/CAC를 비교 분석할 수 있다

---

## 핵심 개념

### LTV (Customer Lifetime Value)

> 고객이 우리와의 관계 전체 기간 동안 창출할 **예상 총 매출**

**왜 중요한가?**
- 마케팅 예산의 상한선 결정 (LTV > CAC 여야 수익)
- 고객 세그먼트 우선순위 결정
- 투자자 소통의 핵심 지표

**계산 방법**
```
단순 LTV = 평균 주문 금액 (AOV) × 평균 구매 빈도 × 평균 고객 수명
```

### CAC (Customer Acquisition Cost)

> 고객 1명을 획득하는 데 드는 **평균 비용**

**계산 방법**
```
CAC = 총 마케팅 비용 / 신규 고객 수
```

### LTV:CAC 비율

| 비율 | 의미 | 액션 |
|------|------|------|
| < 1x | 적자 | 즉시 마케팅 효율 개선 |
| 1-3x | 주의 | CAC 절감 또는 LTV 증대 |
| 3-5x | 양호 | 건전한 비즈니스 |
| > 5x | 우수 | 마케팅 투자 확대 여력 |

---

## 실습 순서

1. `exercise.ipynb` 열기
2. 각 미션의 SQL을 직접 작성
3. 막히면 힌트 참고 (가능한 안 보고!)
4. 완료 후 `solution.sql`과 비교
5. 회고: 어떤 점이 어려웠는지 정리

---

## 테이블 구조

```sql
-- 고객 테이블
customers (
    customer_id,      -- 고객 ID
    signup_date,      -- 가입일
    acquisition_channel,  -- 획득 채널 (organic, google_ads, facebook, ...)
    acquisition_cost, -- 획득 비용
    is_churned        -- 이탈 여부 (0/1)
)

-- 거래 테이블
transactions (
    transaction_id,   -- 거래 ID
    customer_id,      -- 고객 ID (FK)
    transaction_date, -- 거래일
    amount,           -- 거래 금액
    product_category  -- 상품 카테고리
)

-- 캠페인 테이블
campaigns (
    campaign_id,      -- 캠페인 ID
    channel,          -- 채널
    spend,            -- 지출 금액
    conversions,      -- 전환 수
    revenue           -- 매출
)
```

---

## 면접 대비 포인트

**자주 묻는 질문:**
1. "LTV를 어떻게 계산하셨나요?"
2. "LTV:CAC 비율이 낮으면 어떻게 하시겠습니까?"
3. "채널별 CAC를 비교할 때 주의할 점은?"

**좋은 답변 예시:**
> "LTV는 AOV × 구매빈도 × 고객수명으로 계산했습니다.
> 단, 코호트별로 다르게 계산하여 시간에 따른 변화도 추적했습니다.
> LTV:CAC가 3:1 미만인 채널은 예산을 줄이고,
> 우수 채널에 재배분하는 전략을 제안했습니다."
