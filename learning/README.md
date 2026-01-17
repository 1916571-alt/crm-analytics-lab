# CRM Analytics 학습 모듈

SQL 기반 실습으로 CRM 핵심 지표와 분석 기법을 학습합니다.

## 시작하기

### 1. 데이터베이스 생성

```bash
python learning/setup_database.py
```

이 명령은 `learning/data/crm.db` 파일을 생성합니다.

### 2. 실습 진행

각 모듈의 `exercise.ipynb` 파일을 Jupyter Notebook으로 열어 실습합니다.

---

## 학습 모듈

| 모듈 | 주제 | 핵심 개념 | 난이도 |
|------|------|-----------|--------|
| **01** | [LTV & CAC](./01_LTV_CAC/) | 고객 생애 가치, 획득 비용, LTV:CAC 비율 | 기초 |
| **02** | [Funnel 분석](./02_Funnel/) | 퍼널, 전환율, 병목 지점, 드롭오프 | 기초 |
| **03** | [Cohort & Retention](./03_Cohort_Retention/) | 코호트, 리텐션 매트릭스, 이탈 분석 | 중급 |
| **04** | [RFM 세그먼테이션](./04_RFM/) | R/F/M 점수, 고객 세그먼트, 파레토 법칙 | 중급 |
| **05** | [A/B 테스트](./05_AB_Test/) | 실험 설계, 전환율, 통계적 유의성 | 중급 |

---

## 학습 방법

### 권장 순서

1. **01_LTV_CAC**: 가장 기본적인 비즈니스 지표부터 시작
2. **02_Funnel**: 사용자 여정 분석
3. **03_Cohort_Retention**: 시간에 따른 행동 패턴
4. **04_RFM**: 고객 세그먼테이션
5. **05_AB_Test**: 데이터 기반 의사결정

### 각 모듈 진행 방법

```
1. README.md 읽기 → 개념 이해
2. exercise.ipynb 열기 → 직접 SQL 작성
3. 막히면 힌트 확인 (가능한 안 보고!)
4. solution.sql 비교 → 정답 확인
5. 회고 작성 → 학습 내용 정리
```

---

## 데이터베이스 구조

### 테이블 목록

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|-----------|
| **customers** | 고객 정보 | customer_id, signup_date, acquisition_channel, acquisition_cost |
| **transactions** | 거래 내역 | transaction_id, customer_id, transaction_date, amount |
| **campaigns** | 마케팅 캠페인 | campaign_id, channel, spend, conversions |
| **events** | 이벤트 로그 | event_id, user_id, event_type, device, channel |

### 데이터 규모

- customers: 2,000명
- transactions: ~5,000건
- campaigns: 50개
- events: ~35,000건

---

## 면접 대비

각 모듈에서 다루는 면접 질문 예시:

### LTV & CAC
- "LTV를 어떻게 계산하셨나요?"
- "LTV:CAC 비율이 낮으면 어떻게 하시겠습니까?"

### Funnel
- "퍼널 분석을 어떻게 하셨나요?"
- "병목 지점을 어떻게 찾으셨나요?"

### Cohort
- "코호트 분석 경험이 있나요?"
- "리텐션 개선을 위해 무엇을 하셨나요?"

### RFM
- "고객 세그먼테이션 경험이 있나요?"
- "파레토 법칙이 실제로 적용되던가요?"

### A/B Test
- "A/B 테스트를 어떻게 설계하셨나요?"
- "통계적 유의성은 어떻게 판단하셨나요?"

---

## SQL 기술

이 실습에서 배우는 SQL 기술:

- **기본**: SELECT, WHERE, GROUP BY, ORDER BY
- **집계**: SUM, COUNT, AVG, MIN, MAX
- **조인**: INNER JOIN, LEFT JOIN
- **서브쿼리**: WITH (CTE), 스칼라 서브쿼리
- **윈도우 함수**: NTILE, LAG, SUM OVER, ROW_NUMBER
- **조건문**: CASE WHEN
- **날짜 함수**: strftime, julianday

---

## 팁

1. **직접 해보기**: 답을 바로 보지 말고 먼저 시도하세요
2. **오류 분석**: 틀린 부분을 분석하면 더 오래 기억됩니다
3. **회고 작성**: 배운 점과 어려웠던 점을 기록하세요
4. **반복 학습**: 시간을 두고 다시 풀어보세요
5. **면접 연습**: 결과를 말로 설명하는 연습을 하세요
