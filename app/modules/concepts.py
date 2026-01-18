"""
CRM 분석 개념 학습 모듈
- AARRR 프레임워크
- Customer Lifecycle
- 지표 간 관계도
- 실무 의사결정 프로세스
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


def show_concepts_module():
    """개념 학습 메인 페이지"""

    # 모듈 헤더
    st.markdown("""
    <div style="margin-bottom: 2rem;">
        <h1 style="margin-bottom: 0.5rem !important;">📖 CRM 분석 개념 학습</h1>
        <p style="font-size: 1.1rem !important; color: #6B7280 !important;">
            실습 전 필수 개념 · 비즈니스 맥락을 이해하고 올바른 질문 던지기
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 탭 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "AARRR 프레임워크",
        "Customer Lifecycle",
        "지표 관계도",
        "의사결정 프로세스",
        "모듈별 개념"
    ])

    with tab1:
        show_aarrr_framework()

    with tab2:
        show_customer_lifecycle()

    with tab3:
        show_metrics_relationship()

    with tab4:
        show_decision_process()

    with tab5:
        show_module_concepts()


def create_aarrr_funnel():
    """AARRR 퍼널 차트 생성"""
    fig = go.Figure(go.Funnel(
        y=["Acquisition (획득)", "Activation (활성화)", "Retention (유지)",
           "Revenue (수익화)", "Referral (추천)"],
        x=[10000, 4000, 2000, 800, 200],
        textposition="inside",
        textinfo="value+percent initial",
        opacity=0.85,
        marker={
            "color": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6"],
            "line": {"width": [2, 2, 2, 2, 2], "color": ["white"]*5}
        },
        connector={"line": {"color": "#E5E7EB", "width": 2}}
    ))

    fig.update_layout(
        title={
            "text": "AARRR Funnel - 고객 여정 단계별 전환",
            "font": {"size": 18}
        },
        font={"size": 14},
        height=450,
        margin=dict(t=60, l=20, r=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_lifecycle_sankey():
    """Customer Lifecycle Sankey 다이어그램"""
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=20,
            thickness=25,
            line=dict(color="white", width=1),
            label=["잠재고객", "신규고객", "활성고객", "충성고객", "휴면고객", "이탈고객"],
            color=["#94A3B8", "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EF4444"],
            x=[0.0, 0.25, 0.5, 0.75, 0.6, 0.85],
            y=[0.5, 0.5, 0.4, 0.3, 0.7, 0.8]
        ),
        link=dict(
            source=[0, 1, 1, 2, 2, 3, 4, 3],
            target=[1, 2, 4, 3, 4, 2, 5, 4],
            value=[1000, 600, 200, 400, 100, 100, 150, 50],
            color=["rgba(59,130,246,0.4)", "rgba(16,185,129,0.4)", "rgba(245,158,11,0.4)",
                   "rgba(139,92,246,0.4)", "rgba(245,158,11,0.4)", "rgba(16,185,129,0.4)",
                   "rgba(239,68,68,0.4)", "rgba(245,158,11,0.4)"]
        )
    ))

    fig.update_layout(
        title={
            "text": "Customer Lifecycle Flow - 고객 상태 전이",
            "font": {"size": 18}
        },
        font={"size": 13},
        height=400,
        margin=dict(t=60, l=20, r=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_metrics_treemap():
    """지표 관계 Treemap"""
    labels = ["CRM 지표",
              "Revenue", "LTV", "고객수",
              "RFM", "CAC", "Funnel",
              "Recency", "Frequency", "Monetary", "Retention", "전환율", "A/B Test"]
    parents = ["",
               "CRM 지표", "Revenue", "Revenue",
               "LTV", "고객수", "고객수",
               "RFM", "RFM", "RFM", "Funnel", "Funnel", "전환율"]
    values = [100, 50, 25, 25, 15, 12, 13, 5, 5, 5, 6, 5, 2]
    colors = ["#1E293B",
              "#3B82F6", "#60A5FA", "#60A5FA",
              "#10B981", "#F59E0B", "#F59E0B",
              "#34D399", "#34D399", "#34D399", "#FBBF24", "#FBBF24", "#A78BFA"]

    fig = go.Figure(go.Treemap(
        labels=labels,
        parents=parents,
        values=values,
        marker=dict(colors=colors, line=dict(width=2, color="white")),
        textinfo="label",
        textfont=dict(size=14)
    ))

    fig.update_layout(
        title={
            "text": "CRM 지표 계층 구조",
            "font": {"size": 18}
        },
        height=400,
        margin=dict(t=60, l=10, r=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_metrics_network():
    """지표 관계 네트워크 그래프"""
    import math

    # 노드 위치 (원형 배치 + 중앙)
    nodes = {
        "Revenue": (0.5, 0.9),
        "LTV": (0.25, 0.7),
        "고객수": (0.75, 0.7),
        "RFM": (0.15, 0.45),
        "CAC": (0.85, 0.45),
        "Retention": (0.3, 0.2),
        "Funnel": (0.7, 0.2),
        "A/B Test": (0.5, 0.05)
    }

    # 엣지 정의
    edges = [
        ("LTV", "Revenue"), ("고객수", "Revenue"),
        ("RFM", "LTV"), ("CAC", "고객수"),
        ("Retention", "RFM"), ("Funnel", "CAC"),
        ("Funnel", "Retention"), ("A/B Test", "Funnel")
    ]

    # 색상 매핑
    colors = {
        "Revenue": "#EF4444",
        "LTV": "#3B82F6",
        "고객수": "#3B82F6",
        "RFM": "#10B981",
        "CAC": "#F59E0B",
        "Retention": "#8B5CF6",
        "Funnel": "#F59E0B",
        "A/B Test": "#6366F1"
    }

    fig = go.Figure()

    # 엣지 그리기
    for src, dst in edges:
        x0, y0 = nodes[src]
        x1, y1 = nodes[dst]
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode="lines",
            line=dict(width=2, color="#CBD5E1"),
            hoverinfo="none",
            showlegend=False
        ))

        # 화살표 (삼각형)
        angle = math.atan2(y1-y0, x1-x0)
        arrow_size = 0.03
        mid_x = x0 + (x1-x0)*0.7
        mid_y = y0 + (y1-y0)*0.7

        fig.add_trace(go.Scatter(
            x=[mid_x - arrow_size*math.cos(angle-0.5), mid_x, mid_x - arrow_size*math.cos(angle+0.5)],
            y=[mid_y - arrow_size*math.sin(angle-0.5), mid_y, mid_y - arrow_size*math.sin(angle+0.5)],
            fill="toself",
            fillcolor="#CBD5E1",
            line=dict(color="#CBD5E1"),
            hoverinfo="none",
            showlegend=False
        ))

    # 노드 그리기
    for name, (x, y) in nodes.items():
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode="markers+text",
            marker=dict(size=50, color=colors[name], line=dict(width=3, color="white")),
            text=[name],
            textposition="middle center",
            textfont=dict(size=11, color="white", family="Arial Black"),
            hoverinfo="text",
            hovertext=f"<b>{name}</b>",
            showlegend=False
        ))

    fig.update_layout(
        title={
            "text": "CRM 지표 관계 네트워크",
            "font": {"size": 18}
        },
        height=500,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.05]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.05, 1.0]),
        margin=dict(t=60, l=20, r=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def create_decision_flow():
    """의사결정 프로세스 플로우 차트"""
    fig = go.Figure()

    steps = [
        ("문제 정의", "리텐션 하락 감지", "#3B82F6", 0),
        ("데이터 탐색", "Cohort/Funnel 분석", "#10B981", 1),
        ("가설 수립", "모바일 D7 리텐션 저조", "#F59E0B", 2),
        ("실험 설계", "온보딩 UX A/B Test", "#EF4444", 3),
        ("결과 분석", "통계적 유의성 검증", "#8B5CF6", 4),
        ("의사결정", "B안 전체 배포", "#6366F1", 5)
    ]

    for title, desc, color, idx in steps:
        y_pos = 5 - idx

        # 박스
        fig.add_shape(
            type="rect",
            x0=0.1, x1=0.9,
            y0=y_pos-0.35, y1=y_pos+0.35,
            fillcolor=color,
            line=dict(color="white", width=2),
            layer="below"
        )

        # 텍스트
        fig.add_annotation(
            x=0.5, y=y_pos+0.1,
            text=f"<b>{idx+1}. {title}</b>",
            showarrow=False,
            font=dict(size=14, color="white")
        )
        fig.add_annotation(
            x=0.5, y=y_pos-0.15,
            text=desc,
            showarrow=False,
            font=dict(size=11, color="rgba(255,255,255,0.85)")
        )

        # 화살표 (마지막 제외)
        if idx < 5:
            fig.add_annotation(
                x=0.5, y=y_pos-0.55,
                text="▼",
                showarrow=False,
                font=dict(size=20, color="#94A3B8")
            )

    fig.update_layout(
        title={
            "text": "데이터 기반 의사결정 프로세스",
            "font": {"size": 18}
        },
        height=600,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0, 1]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 5.8]),
        margin=dict(t=60, l=20, r=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def show_aarrr_framework():
    """AARRR 프레임워크 설명"""

    st.markdown("## AARRR 프레임워크 (Pirate Metrics)")

    st.markdown("""
    **AARRR**은 스타트업과 그로스 팀에서 가장 널리 사용되는 지표 프레임워크입니다.
    Dave McClure(500 Startups)가 제안했으며, 고객 여정의 5단계를 측정합니다.
    """)

    st.divider()

    # 퍼널 차트
    st.plotly_chart(create_aarrr_funnel(), use_container_width=True)

    st.divider()

    # 각 단계 카드 스타일
    st.markdown("### 각 단계 상세")

    # 스타일 정의
    card_style = """
    <style>
    .aarrr-card {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border-left: 5px solid;
    }
    .aarrr-card h4 {
        margin: 0 0 0.8rem 0;
        font-size: 1.1rem;
    }
    .aarrr-card p {
        margin: 0.3rem 0;
        font-size: 0.9rem;
    }
    .card-acquisition { background: linear-gradient(135deg, rgba(59,130,246,0.15) 0%, rgba(59,130,246,0.05) 100%); border-color: #3B82F6; }
    .card-activation { background: linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(16,185,129,0.05) 100%); border-color: #10B981; }
    .card-retention { background: linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(245,158,11,0.05) 100%); border-color: #F59E0B; }
    .card-revenue { background: linear-gradient(135deg, rgba(239,68,68,0.15) 0%, rgba(239,68,68,0.05) 100%); border-color: #EF4444; }
    .card-referral { background: linear-gradient(135deg, rgba(139,92,246,0.15) 0%, rgba(139,92,246,0.05) 100%); border-color: #8B5CF6; }
    .metric-badge {
        display: inline-block;
        background: rgba(0,0,0,0.1);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        margin-right: 4px;
    }
    </style>
    """
    st.markdown(card_style, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="aarrr-card card-acquisition">
            <h4>1. Acquisition (획득)</h4>
            <p><strong>질문:</strong> 어떻게 고객이 우리를 알게 되는가?</p>
            <p><strong>지표:</strong> <span class="metric-badge">Traffic</span><span class="metric-badge">CAC</span><span class="metric-badge">채널별 전환율</span></p>
            <p><strong>학습:</strong> LTV & CAC 모듈</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="aarrr-card card-retention">
            <h4>3. Retention (유지)</h4>
            <p><strong>질문:</strong> 다시 돌아오는가?</p>
            <p><strong>지표:</strong> <span class="metric-badge">D1/D7/D30</span><span class="metric-badge">Churn Rate</span><span class="metric-badge">Cohort</span></p>
            <p><strong>학습:</strong> Cohort 분석 모듈</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="aarrr-card card-referral">
            <h4>5. Referral (추천)</h4>
            <p><strong>질문:</strong> 다른 사람에게 알리는가?</p>
            <p><strong>지표:</strong> <span class="metric-badge">NPS</span><span class="metric-badge">K-factor</span><span class="metric-badge">추천 전환율</span></p>
            <p><strong>학습:</strong> 고급 분석 (확장 예정)</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="aarrr-card card-activation">
            <h4>2. Activation (활성화)</h4>
            <p><strong>질문:</strong> 첫 경험이 좋았는가?</p>
            <p><strong>지표:</strong> <span class="metric-badge">First Action</span><span class="metric-badge">Onboarding 완료율</span></p>
            <p><strong>학습:</strong> Funnel 분석 모듈</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="aarrr-card card-revenue">
            <h4>4. Revenue (수익화)</h4>
            <p><strong>질문:</strong> 돈을 내는가?</p>
            <p><strong>지표:</strong> <span class="metric-badge">ARPU</span><span class="metric-badge">LTV</span><span class="metric-badge">Conversion</span></p>
            <p><strong>학습:</strong> LTV & CAC, RFM 모듈</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    st.info("""
    **면접 TIP**: "AARRR 프레임워크에 대해 설명해주세요"

    "AARRR은 고객 여정을 Acquisition, Activation, Retention, Revenue, Referral 5단계로 나누어
    각 단계의 성과를 측정하는 프레임워크입니다.

    핵심은 **'어느 단계가 병목인지 진단'**하는 것입니다.
    유입은 많은데 첫 구매 전환이 낮다면 Activation 문제이고,
    첫 구매는 하는데 재구매가 없다면 Retention 문제입니다."
    """)


def show_customer_lifecycle():
    """Customer Lifecycle 설명"""

    st.markdown("## Customer Lifecycle (고객 생애주기)")

    st.markdown("""
    고객 생애주기는 고객이 브랜드와 맺는 관계의 전체 여정을 의미합니다.
    각 단계에 맞는 **마케팅 전략**과 **분석 지표**가 다릅니다.
    """)

    st.divider()

    # Sankey 다이어그램
    st.plotly_chart(create_lifecycle_sankey(), use_container_width=True)

    st.divider()

    # 단계별 전략 카드
    st.markdown("### 단계별 전략")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
                    padding: 1.5rem; border-radius: 12px; color: white; height: 280px;">
            <h4 style="margin:0 0 1rem 0;">획득 단계</h4>
            <p style="font-size: 0.85rem; opacity: 0.9;"><strong>목표:</strong> 잠재 → 신규</p>
            <hr style="border-color: rgba(255,255,255,0.3); margin: 0.8rem 0;">
            <p style="font-size: 0.85rem;"><strong>전략:</strong></p>
            <ul style="font-size: 0.8rem; padding-left: 1.2rem; margin: 0.5rem 0;">
                <li>광고 캠페인</li>
                <li>SEO/콘텐츠</li>
                <li>프로모션</li>
            </ul>
            <p style="font-size: 0.85rem; margin-top: 0.8rem;"><strong>KPI:</strong> CAC, 전환율</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                    padding: 1.5rem; border-radius: 12px; color: white; height: 280px;">
            <h4 style="margin:0 0 1rem 0;">성장 단계</h4>
            <p style="font-size: 0.85rem; opacity: 0.9;"><strong>목표:</strong> 신규 → 충성</p>
            <hr style="border-color: rgba(255,255,255,0.3); margin: 0.8rem 0;">
            <p style="font-size: 0.85rem;"><strong>전략:</strong></p>
            <ul style="font-size: 0.8rem; padding-left: 1.2rem; margin: 0.5rem 0;">
                <li>개인화 추천</li>
                <li>교차 판매</li>
                <li>로열티 프로그램</li>
            </ul>
            <p style="font-size: 0.85rem; margin-top: 0.8rem;"><strong>KPI:</strong> RFM Score, ARPU</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
                    padding: 1.5rem; border-radius: 12px; color: white; height: 280px;">
            <h4 style="margin:0 0 1rem 0;">유지 단계</h4>
            <p style="font-size: 0.85rem; opacity: 0.9;"><strong>목표:</strong> 이탈 방지</p>
            <hr style="border-color: rgba(255,255,255,0.3); margin: 0.8rem 0;">
            <p style="font-size: 0.85rem;"><strong>전략:</strong></p>
            <ul style="font-size: 0.8rem; padding-left: 1.2rem; margin: 0.5rem 0;">
                <li>이탈 예측 모델</li>
                <li>윈백 캠페인</li>
                <li>VIP 케어</li>
            </ul>
            <p style="font-size: 0.85rem; margin-top: 0.8rem;"><strong>KPI:</strong> Churn Rate, LTV</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # RFM 연결 테이블
    st.markdown("### RFM 세그먼트와의 연결")

    rfm_data = {
        "생애주기": ["신규 고객", "활성 고객", "충성 고객", "휴면 고객", "이탈 고객"],
        "RFM 특성": ["R↑ F↓ M↓", "R↑ F↑ M↑", "R↑ F↑ M↑↑", "R↓ F↓ M?", "R↓↓ F↓ M?"],
        "세그먼트": ["New Customer", "Active/Champion", "VIP/Loyal", "At Risk", "Churned"],
        "전략": ["첫 구매 유도", "유지, 업셀링", "특별 혜택", "재활성화", "윈백/포기"]
    }
    st.dataframe(rfm_data, use_container_width=True, hide_index=True)

    st.info("""
    **면접 TIP**: "고객 생애주기 관리는 어떻게 하시나요?"

    "고객을 획득-성장-유지 단계로 나누고, 각 단계에 맞는 KPI와 마케팅 전략을 설계합니다.
    핵심은 **'단계 전이율'**을 추적하는 것입니다.
    RFM 분석을 통해 각 고객이 어느 단계에 있는지 정량적으로 분류하고,
    단계별로 다른 CRM 액션을 자동화합니다."
    """)


def show_metrics_relationship():
    """지표 간 관계도"""

    st.markdown("## CRM 핵심 지표 관계도")

    st.markdown("""
    CRM 지표들은 서로 **밀접하게 연결**되어 있습니다.
    한 지표의 변화가 다른 지표에 어떤 영향을 미치는지 이해하는 것이 중요합니다.
    """)

    st.divider()

    # 두 가지 시각화
    viz_tab1, viz_tab2 = st.tabs(["네트워크 뷰", "계층 구조 뷰"])

    with viz_tab1:
        st.plotly_chart(create_metrics_network(), use_container_width=True)

    with viz_tab2:
        st.plotly_chart(create_metrics_treemap(), use_container_width=True)

    st.divider()

    # 핵심 공식 - 시각적 카드
    st.markdown("### 핵심 공식")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
                    padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem;">
            <h4 style="margin:0 0 0.5rem 0;">LTV (고객 생애 가치)</h4>
            <div style="background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.9rem;">
                LTV = ARPU x 평균 고객 수명<br>
                &nbsp;&nbsp;&nbsp;&nbsp;= ARPU x (1 / Churn Rate)
            </div>
            <p style="font-size: 0.85rem; margin-top: 0.8rem; opacity: 0.9;">
                한 고객이 전체 관계 기간 동안 가져다주는 총 가치
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: linear-gradient(135deg, #10B981 0%, #059669 100%);
                    padding: 1.5rem; border-radius: 12px; color: white;">
            <h4 style="margin:0 0 0.5rem 0;">LTV:CAC 비율</h4>
            <div style="background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.9rem;">
                LTV:CAC Ratio = LTV / CAC
            </div>
            <p style="font-size: 0.85rem; margin-top: 0.8rem; opacity: 0.9;">
                < 3:1 주의 | 3:1~5:1 건강 | > 5:1 과소투자?
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
                    padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1rem;">
            <h4 style="margin:0 0 0.5rem 0;">CAC (고객 획득 비용)</h4>
            <div style="background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.9rem;">
                CAC = 총 마케팅 비용 / 신규 고객 수
            </div>
            <p style="font-size: 0.85rem; margin-top: 0.8rem; opacity: 0.9;">
                고객 1명을 획득하는 데 드는 비용
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style="background: linear-gradient(135deg, #8B5CF6 0%, #7C3AED 100%);
                    padding: 1.5rem; border-radius: 12px; color: white;">
            <h4 style="margin:0 0 0.5rem 0;">Payback Period</h4>
            <div style="background: rgba(255,255,255,0.15); padding: 1rem; border-radius: 8px; font-family: monospace; font-size: 0.9rem;">
                Payback = CAC / (ARPU x Margin)
            </div>
            <p style="font-size: 0.85rem; margin-top: 0.8rem; opacity: 0.9;">
                CAC를 회수하는 데 걸리는 기간
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 연쇄 효과 시각화
    st.markdown("### 지표 개선의 연쇄 효과")

    effect_data = {
        "개선 영역": ["Funnel 전환율 ↑", "Retention ↑", "객단가(M) ↑", "구매빈도(F) ↑", "CAC ↓"],
        "직접 효과": ["더 많은 고객 획득", "고객 수명 증가", "거래당 매출 증가", "연간 구매 횟수 증가", "획득 효율 개선"],
        "연쇄 효과": ["CAC ↓, 총 고객 수 ↑", "LTV ↑, Churn ↓", "ARPU ↑, LTV ↑", "ARPU ↑, LTV ↑", "LTV:CAC ↑, ROI ↑"]
    }
    st.dataframe(effect_data, use_container_width=True, hide_index=True)

    st.success("""
    **핵심 인사이트**: 가장 레버리지가 큰 지표는 **Retention**입니다.

    - Retention 5% 개선 → 이익 25~95% 증가 (Bain & Company)
    - 신규 고객 획득 비용은 기존 고객 유지 비용의 5~25배
    - 따라서 CRM의 핵심은 **"좋은 고객을 오래 유지하는 것"**
    """)


def show_decision_process():
    """데이터 기반 의사결정 프로세스"""

    st.markdown("## 데이터 기반 의사결정 프로세스")

    st.markdown("""
    CRM 분석의 궁극적 목표는 **더 나은 의사결정**입니다.
    숫자를 계산하는 것이 아니라, 그 숫자로 **무엇을 할지** 결정하는 것이 핵심입니다.
    """)

    st.divider()

    # 프로세스 플로우 차트
    st.plotly_chart(create_decision_flow(), use_container_width=True)

    st.divider()

    # 실전 케이스
    st.markdown("### 실전 케이스 스터디")

    case_tab1, case_tab2, case_tab3 = st.tabs([
        "Case 1: LTV 하락",
        "Case 2: Funnel 이탈",
        "Case 3: VIP 이탈"
    ])

    with case_tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            #### 상황
            월간 리포트에서 LTV가 전월 대비 **15% 하락**

            #### 분석 접근
            1. LTV = ARPU x 고객수명 → 어느 쪽?
            2. ARPU 분해: 객단가 x 구매빈도
            3. 세그먼트별: 어떤 고객군?
            4. 시계열: 언제부터? 무슨 이벤트?
            """)
        with col2:
            st.markdown("""
            #### 가설 예시
            - 할인 프로모션 → 저가치 고객 유입
            - 경쟁사 출시 → 기존 고객 이탈
            - 품질 이슈 → 재구매율 하락

            #### SQL 분석
            ```sql
            SELECT acquisition_channel,
                   AVG(total_amount) as avg_ltv
            FROM customers c
            JOIN (SELECT customer_id,
                         SUM(amount) as total_amount
                  FROM transactions
                  GROUP BY customer_id) t
            ON c.customer_id = t.customer_id
            GROUP BY acquisition_channel
            ```
            """)

    with case_tab2:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            #### 상황
            장바구니 → 결제 전환율이 **50% → 30%** 하락

            #### 분석 접근
            1. 시점: 정확히 언제? 배포 연관?
            2. 세그먼트: 모바일/PC? 신규/기존?
            3. 에러 로그: 결제 실패 증가?
            4. 외부 요인: 경쟁사?
            """)
        with col2:
            st.markdown("""
            #### 가설 예시
            - 결제 UI 변경 → 혼란
            - PG사 장애 → 특정 결제 실패
            - 배송비 변경 → 이탈 증가

            #### A/B Test 설계
            - **Control**: 현재 결제 페이지
            - **Treatment**: 버튼 강조 + 진행 표시
            - **Metric**: 장바구니→결제 전환율
            - **기간**: 2주
            """)

    with case_tab3:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            #### 상황
            VIP(상위 5%) 최근 구매일 **60일 → 90일** 증가

            #### 분석 접근
            1. 개별 분석: 누가 이탈 위험?
            2. 패턴: 이탈 전 공통 행동?
            3. 외부: 경쟁사 프로모션?
            4. 내부: CS 이슈? 제품 문제?
            """)
        with col2:
            st.markdown("""
            #### 액션 플랜
            - **즉시**: VIP 전용 윈백 캠페인
            - **단기**: 이탈 예측 모델 구축
            - **중기**: VIP 로열티 강화

            #### 측정 지표
            - 윈백 캠페인 응답률
            - 재구매 전환율
            - 재구매 후 3개월 리텐션
            """)

    st.divider()

    st.info("""
    **면접 TIP**: "데이터 분석 결과를 어떻게 의사결정에 연결하시나요?"

    "저는 **'숫자 → 인사이트 → 액션 → 측정'**의 4단계 프레임워크를 사용합니다.

    1. **숫자**: 지표가 떨어졌다 (What)
    2. **인사이트**: 왜 떨어졌는지 원인 분석 (Why)
    3. **액션**: 어떤 조치를 취할지 결정 (How)
    4. **측정**: 조치의 효과를 A/B 테스트로 검증 (Impact)"
    """)


def show_module_concepts():
    """모듈별 개념 설명"""

    st.markdown("## 모듈별 핵심 개념")

    st.markdown("""
    각 학습 모듈에서 다루는 개념을 미리 이해하고 실습에 들어가세요.
    """)

    st.divider()

    # 학습 로드맵 시각화
    st.markdown("### 학습 로드맵")

    roadmap_fig = go.Figure()

    modules = [
        ("LTV & CAC", "기초", "#3B82F6", 1),
        ("Funnel 분석", "기초", "#10B981", 2),
        ("Cohort 분석", "중급", "#F59E0B", 3),
        ("RFM 세그먼트", "중급", "#EF4444", 4),
        ("A/B 테스트", "고급", "#8B5CF6", 5)
    ]

    for name, level, color, idx in modules:
        roadmap_fig.add_trace(go.Scatter(
            x=[idx], y=[1],
            mode="markers+text",
            marker=dict(size=60, color=color, line=dict(width=3, color="white")),
            text=[f"{name}<br>({level})"],
            textposition="bottom center",
            textfont=dict(size=11),
            hoverinfo="text",
            hovertext=f"<b>{name}</b><br>난이도: {level}",
            showlegend=False
        ))

        if idx < 5:
            roadmap_fig.add_annotation(
                x=idx+0.5, y=1,
                text="→",
                showarrow=False,
                font=dict(size=24, color="#94A3B8")
            )

    roadmap_fig.update_layout(
        height=200,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.3, 5.7]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.5, 1.5]),
        margin=dict(t=20, l=20, r=20, b=60),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    st.plotly_chart(roadmap_fig, use_container_width=True)

    st.divider()

    # 모듈별 상세 - 탭으로 구성
    module_tabs = st.tabs([
        "LTV & CAC",
        "Funnel 분석",
        "Cohort 분석",
        "RFM 세그먼트",
        "A/B 테스트"
    ])

    with module_tabs[0]:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            ### 왜 배우는가?

            마케팅의 가장 기본적인 질문:

            > **"이 고객을 획득하는 게 이득인가?"**

            - CAC > LTV → 획득할수록 손해
            - CAC < LTV → 획득할수록 이익

            ### 실무 적용
            - 채널별 CAC 비교 → 효율 채널에 예산 집중
            - 코호트별 LTV 추적 → 고객 품질 모니터링
            - LTV:CAC 기준 설정 → 마케팅 효율 가이드라인
            """)
        with col2:
            st.markdown("### 핵심 개념")
            st.dataframe({
                "개념": ["LTV", "CAC", "LTV:CAC", "Payback"],
                "정의": ["고객 1명의 전체 기여 가치", "고객 1명 획득 비용", "투자 대비 수익 비율", "CAC 회수 기간"],
                "공식": ["총매출 / 고객수", "마케팅비용 / 신규고객수", "LTV / CAC", "CAC / 월 ARPU"]
            }, use_container_width=True, hide_index=True)

    with module_tabs[1]:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            ### 왜 배우는가?

            > **"어디서 고객을 잃고 있는가?"**

            100명이 유입되어 3명만 구매한다면,
            97명은 어디서 이탈했는가?

            ### 퍼널 예시 (이커머스)
            ```
            방문 (100%)
            → 상품조회 (60%)
            → 장바구니 (20%)
            → 결제시작 (10%)
            → 구매완료 (5%)
            ```
            """)
        with col2:
            st.markdown("### 핵심 개념")
            st.dataframe({
                "개념": ["전환율", "이탈률", "병목", "전체 전환율"],
                "정의": ["다음 단계로 넘어간 비율", "현재 단계에서 빠진 비율", "이탈이 가장 큰 단계", "처음 → 끝 비율"],
                "공식": ["다음단계 / 현재단계", "1 - 전환율", "max(이탈률)", "최종단계 / 첫단계"]
            }, use_container_width=True, hide_index=True)

    with module_tabs[2]:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            ### 왜 배우는가?

            > **"고객이 시간이 지나도 계속 쓰는가?"**

            전체 리텐션은 속을 수 있다.
            1월 가입자와 6월 가입자의 행동은 다르다.

            ### 리텐션 매트릭스 예시
            ```
                    M+0    M+1    M+2    M+3
            Jan    100%    45%    30%    25%
            Feb    100%    50%    35%    28%
            Mar    100%    55%    40%    -
            ```
            """)
        with col2:
            st.markdown("### 핵심 개념")
            st.dataframe({
                "개념": ["코호트", "M+N 리텐션", "리텐션 매트릭스", "Churn Rate"],
                "정의": ["동일 특성 그룹", "N개월 후 잔존율", "코호트 x 기간 표", "이탈률"],
                "설명": ["같은 달 가입 등", "가입 후 N개월에 활동한 비율", "시간에 따른 변화 시각화", "1 - 리텐션율"]
            }, use_container_width=True, hide_index=True)

    with module_tabs[3]:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            ### 왜 배우는가?

            > **"어떤 고객에게 어떤 메시지를 보내야 하는가?"**

            모든 고객에게 같은 메시지 = 낮은 효율 + 고객 피로도

            ### RFM 세그먼트 예시
            | 세그먼트 | 특징 | 전략 |
            |---------|------|------|
            | Champion | 최근+자주+많이 | VIP 케어 |
            | At Risk | 이전엔 좋았는데 | 윈백 캠페인 |
            | Churned | 오래전 이탈 | 재활성화 |
            """)
        with col2:
            st.markdown("### 핵심 개념")
            st.dataframe({
                "개념": ["Recency", "Frequency", "Monetary", "NTILE"],
                "정의": ["최근 구매일", "구매 빈도", "구매 금액", "N분위 분류"],
                "의미": ["최근일수록 재구매 가능성↑", "자주 살수록 충성도↑", "많이 쓸수록 가치↑", "상대적 순위로 점수화"]
            }, use_container_width=True, hide_index=True)

    with module_tabs[4]:
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("""
            ### 왜 배우는가?

            > **"이 변화가 정말 효과가 있는가?"**

            "느낌상 좋아 보인다" ≠ "실제로 효과가 있다"

            ### A/B 테스트 프로세스
            ```
            가설 수립 → 지표 정의 → 표본 크기 계산
            → 실험 실행 → 결과 분석 → 의사결정
            ```

            ### 주의사항
            - Peeking Problem
            - Multiple Testing
            - Novelty Effect
            """)
        with col2:
            st.markdown("### 핵심 개념")
            st.dataframe({
                "개념": ["Control (A)", "Treatment (B)", "Z-score", "p-value", "표본 크기"],
                "정의": ["기존 버전", "새 버전", "표준화된 차이", "우연일 확률", "필요한 샘플 수"],
                "설명": ["비교 기준", "테스트 대상", "(차이) / (표준오차)", "< 0.05면 유의미", "통계적 파워 확보"]
            }, use_container_width=True, hide_index=True)

    st.divider()

    st.success("""
    **학습 순서 추천**: 각 모듈은 이전 모듈의 개념을 확장합니다. 순서대로 학습하는 것을 권장합니다.

    **LTV & CAC** (기초) → **Funnel 분석** (기초) → **Cohort 분석** (중급) → **RFM 세그먼트** (중급) → **A/B 테스트** (고급)
    """)
