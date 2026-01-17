# CRM Analytics Lab

**SQL로 배우는 실무 CRM 분석 학습 플랫폼**

## 개요

이커머스/O2O 플랫폼에서 사용하는 핵심 CRM 지표를 직접 SQL로 산출하며 배우는 인터랙티브 학습 플랫폼입니다.

- **30개 실습 문제** (LTV, Funnel, Cohort, RFM, A/B Test)
- **Streamlit 기반** 웹 인터페이스
- **실제 SQL 작성 & 실행**
- **면접 대비 개념 설명** 포함

## 실행 방법

```bash
# 1. 데이터베이스 생성
python learning/setup_database.py

# 2. Streamlit 앱 실행
streamlit run app/app.py
```

http://localhost:8501 에서 확인

## 학습 모듈

| 모듈 | 문제 수 | 핵심 내용 |
|------|--------|----------|
| **LTV & CAC** | 5문제 | 고객 생애 가치, 획득 비용, LTV:CAC 비율, Payback Period |
| **Funnel 분석** | 5문제 | 전환율, 이탈률, 병목 지점, 디바이스별 비교 |
| **Cohort 분석** | 5문제 | 월별 코호트, 리텐션 매트릭스, M+N 리텐션 |
| **RFM 세그먼트** | 5문제 | R/F/M 스코어링, NTILE, 세그먼트 분류, 파레토 분석 |
| **A/B 테스트** | 10문제 | Z-test, p-value, 표본 크기, 세그먼트 분석, RPU |

## 학습 흐름

```
1. 문제 읽기 → 비즈니스 상황 이해
2. SQL 작성 → 직접 쿼리 작성
3. 실행 → 결과 확인
4. 정답 비교 → 해설 확인
5. 면접 TIP → 개념 정리
```

## 기술 스택

- **Python 3.10+**
- **Streamlit** - 웹 인터페이스
- **SQLite** - 데이터베이스
- **Plotly** - 시각화

## 프로젝트 구조

```
crm-analytics-lab/
├── app/
│   ├── app.py                 # Streamlit 메인 앱
│   ├── components/            # 공통 컴포넌트
│   │   ├── question_card.py   # 문제 카드
│   │   ├── sql_editor.py      # SQL 에디터
│   │   └── result_viewer.py   # 결과 뷰어
│   └── modules/               # 학습 모듈
│       ├── ltv_cac.py         # LTV & CAC
│       ├── funnel.py          # Funnel 분석
│       ├── cohort.py          # Cohort 분석
│       ├── rfm.py             # RFM 세그먼트
│       ├── ab_test.py         # A/B 테스트
│       └── dashboard.py       # 결과 대시보드
├── learning/
│   ├── data/
│   │   └── crm.db             # SQLite 데이터베이스
│   └── setup_database.py      # DB 생성 스크립트
├── requirements.txt
├── README.md
└── CLAUDE.md
```

## 데이터베이스 테이블

| 테이블 | 설명 | 레코드 수 |
|--------|------|----------|
| `customers` | 고객 정보 | 2,000명 |
| `transactions` | 거래 내역 | ~5,000건 |
| `events` | 이벤트 로그 | ~35,000건 |
| `campaigns` | 마케팅 캠페인 | 50개 |

## 학습 목표

- 모바일 앱/O2O 플랫폼 CRM 데이터 분석 역량 강화
- 실무 SQL 쿼리 작성 능력 향상
- 면접 대비 개념 정리

## 라이선스

MIT License
