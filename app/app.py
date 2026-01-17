"""
CRM Analytics Lab - SQL 학습 플랫폼
실무 CRM 지표를 SQL로 직접 산출하며 배우는 인터랙티브 학습 플랫폼
"""

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

# 페이지 설정
st.set_page_config(
    page_title="CRM Analytics Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일
st.markdown("""
<style>
    /* 메인 컬러 */
    :root {
        --primary: #3B82F6;
        --success: #10B981;
        --warning: #F59E0B;
        --error: #EF4444;
    }

    /* 사이드바 스타일 */
    .css-1d391kg {
        padding-top: 1rem;
    }

    /* 카드 스타일 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 1rem;
    }

    /* SQL 에디터 스타일 */
    .stTextArea textarea {
        font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        font-size: 14px;
    }

    /* 힌트 박스 */
    .hint-box {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }

    /* 정답 박스 */
    .answer-box {
        background-color: #D1FAE5;
        border-left: 4px solid #10B981;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }

    /* 면접 TIP 박스 */
    .tip-box {
        background-color: #EDE9FE;
        border-left: 4px solid #8B5CF6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 데이터베이스 경로
DB_PATH = Path(__file__).parent.parent / "learning" / "data" / "crm.db"

def get_db_connection():
    """데이터베이스 연결"""
    return sqlite3.connect(DB_PATH)

def execute_query(query: str) -> tuple[pd.DataFrame | None, str | None]:
    """SQL 쿼리 실행"""
    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)

def init_session_state():
    """세션 상태 초기화"""
    if 'completed_questions' not in st.session_state:
        st.session_state.completed_questions = {}
    if 'user_queries' not in st.session_state:
        st.session_state.user_queries = {}

def main():
    init_session_state()

    # 사이드바
    with st.sidebar:
        st.image("https://em-content.zobj.net/source/apple/391/bar-chart_1f4ca.png", width=60)
        st.title("CRM Analytics Lab")
        st.caption("SQL로 배우는 CRM 분석")

        st.divider()

        # 모듈 선택
        st.subheader("📚 학습 모듈")

        module = st.radio(
            "모듈 선택",
            options=[
                "🏠 홈",
                "💰 LTV & CAC",
                "🔄 Funnel 분석",
                "📅 Cohort 분석",
                "🎯 RFM 세그먼트",
                "🧪 A/B 테스트",
                "📊 My Dashboard"
            ],
            label_visibility="collapsed"
        )

        st.divider()

        # 진행률
        total_questions = 30  # 총 문제 수
        completed = len(st.session_state.completed_questions)
        progress = completed / total_questions

        st.subheader("📈 학습 진행률")
        st.progress(progress)
        st.caption(f"{completed}/{total_questions} 문제 완료")

        st.divider()

        # 데이터베이스 상태
        st.subheader("🗄️ 데이터베이스")
        if DB_PATH.exists():
            st.success("연결됨", icon="✅")

            # 테이블 목록
            conn = get_db_connection()
            tables = pd.read_sql_query(
                "SELECT name FROM sqlite_master WHERE type='table'",
                conn
            )
            conn.close()

            with st.expander("테이블 목록"):
                for table in tables['name']:
                    st.code(table)
        else:
            st.error("DB 없음", icon="❌")
            st.caption("python learning/setup_database.py 실행")

    # 메인 콘텐츠
    if module == "🏠 홈":
        show_home()
    elif module == "💰 LTV & CAC":
        from modules.ltv_cac import show_ltv_cac_module
        show_ltv_cac_module()
    elif module == "🔄 Funnel 분석":
        from modules.funnel import show_funnel_module
        show_funnel_module()
    elif module == "📅 Cohort 분석":
        from modules.cohort import show_cohort_module
        show_cohort_module()
    elif module == "🎯 RFM 세그먼트":
        from modules.rfm import show_rfm_module
        show_rfm_module()
    elif module == "🧪 A/B 테스트":
        from modules.ab_test import show_ab_test_module
        show_ab_test_module()
    elif module == "📊 My Dashboard":
        from modules.dashboard import show_dashboard
        show_dashboard()

def show_home():
    """홈 화면"""
    st.title("🎯 CRM Analytics Lab")
    st.markdown("### SQL로 배우는 실무 CRM 분석")

    st.markdown("""
    > **직접 SQL을 작성**하여 CRM 핵심 지표를 산출하고,
    > 데이터 기반 의사결정 역량을 키우세요.
    """)

    st.divider()

    # 학습 모듈 카드
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        ### 💰 LTV & CAC
        **고객 생애 가치와 획득 비용**

        - 고객 LTV 계산
        - 채널별 CAC 분석
        - LTV:CAC 비율 해석
        - 마케팅 ROI 평가

        `5문제` `난이도: 기초`
        """)

    with col2:
        st.markdown("""
        ### 🔄 Funnel 분석
        **전환 퍼널과 병목 분석**

        - 단계별 전환율
        - 이탈률 계산
        - 병목 지점 식별
        - 개선 우선순위

        `5문제` `난이도: 기초`
        """)

    with col3:
        st.markdown("""
        ### 📅 Cohort 분석
        **코호트 리텐션 분석**

        - 월별 코호트 생성
        - 리텐션 매트릭스
        - Churn Rate 계산
        - 생존 분석

        `5문제` `난이도: 중급`
        """)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        ### 🎯 RFM 세그먼트
        **고객 세그먼테이션**

        - R/F/M 점수 계산
        - 5분위 분류
        - 세그먼트 정의
        - 타겟 마케팅

        `5문제` `난이도: 중급`
        """)

    with col5:
        st.markdown("""
        ### 🧪 A/B 테스트
        **실험 설계와 분석**

        - 전환율 비교
        - Z-score 계산
        - p-value 해석
        - 세그먼트별 분석

        `10문제` `난이도: 고급`
        """)

    with col6:
        st.markdown("""
        ### 📊 My Dashboard
        **학습 결과 시각화**

        - 산출한 지표 모아보기
        - 진행률 트래킹
        - 차트 시각화
        - 포트폴리오 정리

        `대시보드`
        """)

    st.divider()

    # 학습 방법
    st.markdown("### 📖 학습 방법")

    st.markdown("""
    ```
    1. 📋 문제 읽기 → 요구사항 이해
    2. 🤔 생각하기 → 어떤 SQL이 필요할지 구상
    3. ✏️ SQL 작성 → 직접 쿼리 작성
    4. ▶️ 실행하기 → 결과 확인
    5. ✅ 정답 비교 → 내 쿼리와 비교
    6. 📝 해설 읽기 → 개념 정리 + 면접 TIP
    ```
    """)

    st.divider()

    # 데이터베이스 미리보기
    st.markdown("### 🗄️ 데이터베이스 미리보기")

    if DB_PATH.exists():
        tab1, tab2, tab3, tab4 = st.tabs(["customers", "transactions", "events", "campaigns"])

        conn = get_db_connection()

        with tab1:
            df = pd.read_sql_query("SELECT * FROM customers LIMIT 5", conn)
            st.dataframe(df, width="stretch")
            st.caption("고객 정보 테이블 (2,000명)")

        with tab2:
            df = pd.read_sql_query("SELECT * FROM transactions LIMIT 5", conn)
            st.dataframe(df, width="stretch")
            st.caption("거래 내역 테이블 (~5,000건)")

        with tab3:
            df = pd.read_sql_query("SELECT * FROM events LIMIT 5", conn)
            st.dataframe(df, width="stretch")
            st.caption("이벤트 로그 테이블 (~35,000건)")

        with tab4:
            df = pd.read_sql_query("SELECT * FROM campaigns LIMIT 5", conn)
            st.dataframe(df, width="stretch")
            st.caption("마케팅 캠페인 테이블 (50개)")

        conn.close()
    else:
        st.warning("데이터베이스가 없습니다. 아래 명령어를 실행하세요:")
        st.code("python learning/setup_database.py")

if __name__ == "__main__":
    main()
