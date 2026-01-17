"""
모듈 6: My Dashboard - 학습 결과 시각화
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "learning" / "data" / "crm.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def show_dashboard():
    """학습 결과 대시보드"""

    st.title("📊 My Analytics Dashboard")

    st.markdown("""
    > 학습을 통해 산출한 CRM 핵심 지표를 한눈에 확인하세요.
    """)

    # 진행률
    col1, col2, col3, col4 = st.columns(4)

    total_questions = 30
    completed = len(st.session_state.get('completed_questions', {}))

    with col1:
        st.metric("완료 문제", f"{completed}/{total_questions}")

    with col2:
        progress_pct = round(completed / total_questions * 100)
        st.metric("진행률", f"{progress_pct}%")

    with col3:
        st.metric("학습 모듈", "5개")

    with col4:
        st.metric("총 문제 수", "30개")

    st.divider()

    # 데이터베이스 체크
    if not DB_PATH.exists():
        st.warning("데이터베이스가 없습니다. 아래 명령어를 먼저 실행하세요:")
        st.code("python learning/setup_database.py")
        return

    conn = get_db_connection()

    # 탭으로 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📈 핵심 지표", "🔄 퍼널", "📅 코호트", "🎯 RFM"])

    with tab1:
        show_key_metrics(conn)

    with tab2:
        show_funnel_chart(conn)

    with tab3:
        show_cohort_heatmap(conn)

    with tab4:
        show_rfm_segments(conn)

    conn.close()


def show_key_metrics(conn):
    """핵심 지표 카드"""

    st.subheader("💰 LTV & CAC 지표")

    # LTV 계산
    ltv_query = """
    WITH customer_revenue AS (
        SELECT customer_id, SUM(amount) as total_revenue
        FROM transactions
        GROUP BY customer_id
    )
    SELECT ROUND(AVG(total_revenue), 0) as avg_ltv
    FROM customer_revenue
    """
    avg_ltv = pd.read_sql_query(ltv_query, conn).iloc[0]['avg_ltv']

    # CAC 계산
    cac_query = """
    SELECT ROUND(SUM(spend) * 1.0 / SUM(conversions), 0) as avg_cac
    FROM campaigns
    """
    avg_cac = pd.read_sql_query(cac_query, conn).iloc[0]['avg_cac']

    # LTV:CAC 비율
    ltv_cac_ratio = round(avg_ltv / avg_cac, 1) if avg_cac > 0 else 0

    # 총 매출
    total_revenue_query = "SELECT SUM(amount) as total FROM transactions"
    total_revenue = pd.read_sql_query(total_revenue_query, conn).iloc[0]['total']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "평균 LTV",
            f"₩{avg_ltv:,.0f}",
            help="고객 생애 가치"
        )

    with col2:
        st.metric(
            "평균 CAC",
            f"₩{avg_cac:,.0f}",
            help="고객 획득 비용"
        )

    with col3:
        delta_color = "normal" if ltv_cac_ratio >= 3 else "inverse"
        st.metric(
            "LTV:CAC 비율",
            f"{ltv_cac_ratio}x",
            delta="Good" if ltv_cac_ratio >= 3 else "Warning",
            delta_color=delta_color,
            help="3x 이상이면 건전"
        )

    with col4:
        st.metric(
            "총 매출",
            f"₩{total_revenue/100000000:.1f}억",
            help="전체 거래 매출"
        )

    # 채널별 LTV:CAC
    st.subheader("채널별 LTV:CAC 비율")

    channel_query = """
    WITH channel_ltv AS (
        SELECT
            c.acquisition_channel as channel,
            ROUND(SUM(t.amount) * 1.0 / COUNT(DISTINCT c.customer_id), 0) as ltv
        FROM customers c
        JOIN transactions t ON c.customer_id = t.customer_id
        GROUP BY c.acquisition_channel
    ),
    channel_cac AS (
        SELECT
            channel,
            ROUND(SUM(spend) * 1.0 / SUM(conversions), 0) as cac
        FROM campaigns
        GROUP BY channel
    )
    SELECT
        l.channel,
        l.ltv,
        c.cac,
        ROUND(l.ltv * 1.0 / c.cac, 1) as ratio
    FROM channel_ltv l
    JOIN channel_cac c ON l.channel = c.channel
    ORDER BY ratio DESC
    """

    channel_df = pd.read_sql_query(channel_query, conn)

    fig = px.bar(
        channel_df,
        x='channel',
        y='ratio',
        color='ratio',
        color_continuous_scale='RdYlGn',
        title='채널별 LTV:CAC 비율'
    )
    fig.add_hline(y=3, line_dash="dash", line_color="red", annotation_text="기준선 (3x)")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, width="stretch")


def show_funnel_chart(conn):
    """퍼널 차트"""

    st.subheader("🔄 전환 퍼널")

    funnel_query = """
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
    ORDER BY step_order
    """

    funnel_df = pd.read_sql_query(funnel_query, conn)

    # 한글 레이블
    step_labels = {
        'page_view': '페이지 방문',
        'product_view': '상품 조회',
        'add_to_cart': '장바구니',
        'purchase': '구매 완료'
    }
    funnel_df['label'] = funnel_df['step'].map(step_labels)

    # 전환율 계산
    total = funnel_df.iloc[0]['users']
    funnel_df['rate'] = funnel_df['users'] / total * 100

    fig = go.Figure(go.Funnel(
        y=funnel_df['label'],
        x=funnel_df['users'],
        textposition="inside",
        textinfo="value+percent initial",
        marker=dict(
            color=['#3B82F6', '#60A5FA', '#93C5FD', '#10B981']
        )
    ))
    fig.update_layout(
        title="전환 퍼널",
        template="plotly_white"
    )
    st.plotly_chart(fig, width="stretch")

    # 이탈률 테이블
    st.subheader("단계별 이탈률")

    funnel_df['prev_users'] = funnel_df['users'].shift(1)
    funnel_df['dropoff'] = funnel_df['prev_users'] - funnel_df['users']
    funnel_df['dropoff_rate'] = (funnel_df['dropoff'] / funnel_df['prev_users'] * 100).round(1)

    display_df = funnel_df[['label', 'users', 'dropoff', 'dropoff_rate']].copy()
    display_df.columns = ['단계', '사용자 수', '이탈 수', '이탈률(%)']
    st.dataframe(display_df, width="stretch", hide_index=True)


def show_cohort_heatmap(conn):
    """코호트 히트맵"""

    st.subheader("📅 코호트 리텐션")

    cohort_query = """
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
    )
    SELECT
        am.cohort_month,
        am.month_diff,
        ROUND(am.active_customers * 100.0 / cs.total_customers, 1) as retention
    FROM activity_months am
    JOIN cohort_size cs ON am.cohort_month = cs.cohort_month
    WHERE am.month_diff BETWEEN 0 AND 5
    ORDER BY am.cohort_month, am.month_diff
    """

    cohort_df = pd.read_sql_query(cohort_query, conn)

    # 피봇 테이블 생성
    pivot_df = cohort_df.pivot(index='cohort_month', columns='month_diff', values='retention')
    pivot_df.columns = [f'M+{i}' for i in pivot_df.columns]

    fig = px.imshow(
        pivot_df,
        color_continuous_scale='Blues',
        aspect='auto',
        title='코호트별 리텐션 히트맵 (%)'
    )
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, width="stretch")

    # 평균 리텐션
    avg_retention = cohort_df.groupby('month_diff')['retention'].mean().round(1)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("M+1 평균 리텐션", f"{avg_retention.get(1, 0)}%")
    with col2:
        st.metric("M+3 평균 리텐션", f"{avg_retention.get(3, 0)}%")
    with col3:
        st.metric("M+5 평균 리텐션", f"{avg_retention.get(5, 0)}%")


def show_rfm_segments(conn):
    """RFM 세그먼트"""

    st.subheader("🎯 RFM 세그먼트 분포")

    rfm_query = """
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
        ROUND(AVG(monetary), 0) as avg_monetary,
        ROUND(SUM(monetary), 0) as total_monetary
    FROM segmented
    GROUP BY segment
    ORDER BY total_monetary DESC
    """

    rfm_df = pd.read_sql_query(rfm_query, conn)

    col1, col2 = st.columns(2)

    with col1:
        fig = px.pie(
            rfm_df,
            names='segment',
            values='customer_count',
            title='세그먼트별 고객 수',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.pie(
            rfm_df,
            names='segment',
            values='total_monetary',
            title='세그먼트별 매출 비중',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, width="stretch")

    # 세그먼트 상세
    st.subheader("세그먼트 상세")

    # 스타일 적용
    display_df = rfm_df.copy()
    display_df.columns = ['세그먼트', '고객 수', '평균 구매액', '총 매출']
    display_df['평균 구매액'] = display_df['평균 구매액'].apply(lambda x: f"₩{x:,.0f}")
    display_df['총 매출'] = display_df['총 매출'].apply(lambda x: f"₩{x:,.0f}")

    st.dataframe(display_df, width="stretch", hide_index=True)

    # 세그먼트별 전략
    st.subheader("세그먼트별 권장 전략")

    strategies = {
        'Champions': ('🏆', 'VIP 프로그램, 얼리 액세스, 추천 인센티브'),
        'Loyal': ('💎', '크로스셀링, 로열티 리워드, 구독 전환'),
        'At Risk': ('⚠️', '윈백 캠페인, 특별 할인, 피드백 수집'),
        'Lost': ('👋', '저비용 리타겟팅, 설문조사, 포기 검토'),
        'Others': ('👤', '일반 마케팅, 세그먼트 이동 유도')
    }

    for segment in rfm_df['segment']:
        if segment in strategies:
            icon, strategy = strategies[segment]
            st.markdown(f"**{icon} {segment}**: {strategy}")
