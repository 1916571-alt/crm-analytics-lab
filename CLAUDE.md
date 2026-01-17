# CRM Analytics Lab - 프로젝트 컨텍스트

## 프로젝트 개요

**SQL로 배우는 CRM 분석 학습 플랫폼**

Streamlit 기반의 인터랙티브 학습 플랫폼으로, 사용자가 직접 SQL 쿼리를 작성하여 CRM 핵심 지표를 산출하고 배우는 시스템입니다.

### 학습 목표
- 모바일 앱/O2O 플랫폼 CRM 실무 역량 강화
- 실무 SQL 쿼리 작성 능력 향상

---

## 학습 모듈 구성

### 총 30개 문제

| 모듈 | 문제 수 | 난이도 | 핵심 개념 |
|------|--------|--------|----------|
| LTV & CAC | 5문제 | 기초~중급 | LTV, CAC, LTV:CAC 비율, Payback Period, ROI |
| Funnel 분석 | 5문제 | 기초~중급 | 전환율, 이탈률, 병목 지점, 디바이스별 분석 |
| Cohort 분석 | 5문제 | 중급~고급 | 코호트 생성, M+N 리텐션, 리텐션 매트릭스 |
| RFM 세그먼트 | 5문제 | 중급~고급 | R/F/M 계산, NTILE, 세그먼트 분류, 파레토 분석 |
| A/B 테스트 | 10문제 | 중급~고급 | Z-test, p-value, 표본 크기, 세그먼트별 분석, RPU |

### 문제 구성 요소

각 문제는 다음 요소로 구성:
- **상황**: 비즈니스 맥락 (왜 이 분석이 필요한지)
- **과제**: 구체적인 요구사항
- **힌트**: SQL 작성 가이드
- **정답 쿼리**: 모범 답안
- **해설**: 개념 설명
- **면접 TIP**: "Q: [질문]" 형태의 개념 설명 (면접 대비)

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 웹 프레임워크 | Streamlit |
| 데이터베이스 | SQLite |
| 시각화 | Plotly |
| 언어 | Python 3.10+ |

---

## 프로젝트 구조

```
crm-analytics-lab/
├── app/                      # Streamlit 앱
│   ├── app.py                # 메인 앱
│   ├── components/           # 공통 컴포넌트
│   │   ├── question_card.py  # Question 데이터클래스, QuestionCard 컴포넌트
│   │   ├── sql_editor.py     # SQL 에디터
│   │   └── result_viewer.py  # 결과 뷰어/차트
│   └── modules/              # 학습 모듈
│       ├── ltv_cac.py        # LTV & CAC (5문제)
│       ├── funnel.py         # Funnel 분석 (5문제)
│       ├── cohort.py         # Cohort 분석 (5문제)
│       ├── rfm.py            # RFM 세그먼트 (5문제)
│       ├── ab_test.py        # A/B 테스트 (10문제)
│       └── dashboard.py      # 결과 대시보드
├── learning/                 # 학습 데이터
│   ├── data/
│   │   └── crm.db            # SQLite 데이터베이스
│   ├── setup_database.py     # DB 생성 스크립트
│   └── 0X_*/                 # 모듈별 TIP 문서
├── requirements.txt
├── README.md
└── CLAUDE.md
```

---

## 실행 명령어

```bash
# 데이터베이스 생성 (처음 한 번)
python learning/setup_database.py

# Streamlit 앱 실행
streamlit run app/app.py
```

---

## 데이터베이스 스키마

### customers
| 컬럼 | 타입 | 설명 |
|------|------|------|
| customer_id | INTEGER | 고객 ID (PK) |
| signup_date | DATE | 가입일 |
| acquisition_channel | TEXT | 획득 채널 (organic, google_ads 등) |

### transactions
| 컬럼 | 타입 | 설명 |
|------|------|------|
| transaction_id | INTEGER | 거래 ID (PK) |
| customer_id | INTEGER | 고객 ID (FK) |
| amount | REAL | 거래 금액 |
| transaction_date | DATE | 거래일 |

### events
| 컬럼 | 타입 | 설명 |
|------|------|------|
| event_id | INTEGER | 이벤트 ID (PK) |
| user_id | INTEGER | 사용자 ID |
| event_type | TEXT | 이벤트 유형 (page_view, purchase 등) |
| device | TEXT | 디바이스 (mobile, desktop) |
| channel | TEXT | 유입 채널 |
| event_date | DATETIME | 이벤트 시간 |

### campaigns
| 컬럼 | 타입 | 설명 |
|------|------|------|
| campaign_id | INTEGER | 캠페인 ID (PK) |
| channel | TEXT | 채널명 |
| spend | REAL | 지출액 |
| conversions | INTEGER | 전환 수 |

---

## 코딩 컨벤션

### Question 데이터클래스

```python
@dataclass
class Question:
    id: str              # 고유 ID (예: "ltv_1")
    title: str           # 제목 (예: "Q1. 전체 고객의 평균 LTV 계산")
    description: str     # 문제 설명 (상황 + 과제 + 요구사항)
    hint: str            # 힌트 (SQL 예시 포함)
    answer_query: str    # 정답 SQL 쿼리
    explanation: str     # 해설
    interview_tip: str   # 면접 TIP (Q: 질문 / 답변 형식)
    difficulty: int      # 난이도 (1-5)
```

### 면접 TIP 형식

```
**Q: [면접관 질문]**

"[개념 설명]

예를 들어...

이것이 중요한 이유는..."
```

---

## 현재 상태

- [x] 데이터베이스 구축
- [x] Streamlit 앱 기본 구조
- [x] 공통 컴포넌트 (QuestionCard, SQLEditor, ResultViewer)
- [x] LTV & CAC 모듈 (5문제)
- [x] Funnel 분석 모듈 (5문제)
- [x] Cohort 분석 모듈 (5문제)
- [x] RFM 세그먼트 모듈 (5문제)
- [x] A/B 테스트 모듈 (10문제)
- [x] 결과 대시보드

---

## 향후 계획

1. 추가 문제 확장 (Retention Curve, Churn Prediction 등)
2. 포트폴리오 정리 및 공개
3. 면접 실전 연습
