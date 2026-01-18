"""
CRM Analytics Lab - SQL 학습 플랫폼
실무 CRM 지표를 SQL로 직접 산출하며 배우는 인터랙티브 학습 플랫폼
"""

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path
from components.progress_manager import init_progress_table, load_all_progress, get_completed_count

# 페이지 설정
st.set_page_config(
    page_title="CRM Analytics Lab",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일 - 전면 개선
st.markdown("""
<style>
    /* ===== 기본 설정 ===== */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --primary: #4F46E5;
        --primary-light: #818CF8;
        --primary-dark: #3730A3;
        --success: #059669;
        --success-light: #D1FAE5;
        --warning: #D97706;
        --warning-light: #FEF3C7;
        --error: #DC2626;
        --error-light: #FEE2E2;
        --purple: #7C3AED;
        --purple-light: #EDE9FE;
        --gray-50: #F9FAFB;
        --gray-100: #F3F4F6;
        --gray-200: #E5E7EB;
        --gray-300: #D1D5DB;
        --gray-600: #4B5563;
        --gray-700: #374151;
        --gray-800: #1F2937;
        --gray-900: #111827;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }

    /* ===== 전체 폰트 설정 ===== */
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* ===== 라이트 모드 강제 적용 ===== */
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    .main,
    .stApp,
    [data-testid="stApp"] {
        background-color: #FFFFFF !important;
        color-scheme: light !important;
    }

    [data-testid="stAppViewContainer"] > section > div {
        background-color: #FFFFFF !important;
    }

    /* 다크 모드 미디어 쿼리 무시 */
    @media (prefers-color-scheme: dark) {
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        .main,
        .stApp,
        [data-testid="stApp"] {
            background-color: #FFFFFF !important;
            color-scheme: light !important;
        }

        [data-testid="stSelectbox"],
        [data-testid="stSelectbox"] *,
        .stSelectbox,
        .stSelectbox * {
            background-color: white !important;
            color: #374151 !important;
        }

        [data-baseweb="select"],
        [data-baseweb="select"] * {
            background-color: white !important;
        }

        [role="listbox"],
        [role="listbox"] *,
        [role="option"],
        [role="option"] * {
            background-color: white !important;
            color: #374151 !important;
        }
    }

    /* ===== 전역 텍스트 색상 (검은색 강제) ===== */
    * {
        --text-color: #374151;
    }

    p, span, li, label, div, a {
        color: #374151 !important;
    }

    h1, h2, h3, h4, h5, h6 {
        color: #111827 !important;
    }

    /* ===== 다크 배경 요소 예외 (흰 텍스트) ===== */

    /* 히어로 섹션 */
    .hero-section h1,
    .hero-section p,
    .hero-section span,
    .hero-section div {
        color: white !important;
    }

    .hero-section p {
        color: #E0E7FF !important;
    }

    /* SQL 에디터 (다크 배경) */
    .stTextArea textarea,
    textarea {
        color: #F3F4F6 !important;
    }

    /* 코드 블록 (다크 배경) */
    .stCodeBlock code,
    .stCodeBlock pre,
    .stCodeBlock span,
    .stCodeBlock div,
    [data-testid="stCodeBlock"] code,
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] span,
    [data-testid="stCodeBlock"] div,
    pre code,
    pre code span {
        color: #F3F4F6 !important;
    }

    /* 버튼 */
    button, .stButton > button {
        color: inherit !important;
    }

    .stButton > button[kind="primary"] {
        color: white !important;
    }

    /* Primary 버튼 (다크 배경) */
    .stButton > button[kind="primary"] span,
    .stButton > button[kind="primary"] div,
    .stButton > button[kind="primary"] p {
        color: white !important;
    }

    /* ===== 메인 콘텐츠 영역 ===== */
    .main .block-container {
        padding: 2rem 3rem 3rem 3rem !important;
        max-width: 1200px !important;
        background-color: #FFFFFF !important;
    }

    /* ===== 타이포그래피 (메인 영역) ===== */
    .main h1, [data-testid="stAppViewContainer"] h1 {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
        letter-spacing: -0.02em !important;
        margin-bottom: 0.5rem !important;
    }

    .main h2, [data-testid="stAppViewContainer"] h2 {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: #1F2937 !important;
        letter-spacing: -0.01em !important;
    }

    .main h3, [data-testid="stAppViewContainer"] h3 {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #1F2937 !important;
    }

    .main p, .main li, .main span,
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] li {
        font-size: 1rem !important;
        line-height: 1.7 !important;
        color: #374151 !important;
    }

    /* 메인 영역 Markdown 텍스트 */
    .main [data-testid="stMarkdownContainer"] p,
    .main [data-testid="stMarkdownContainer"] li,
    .main [data-testid="stMarkdownContainer"] span {
        color: #374151 !important;
    }

    /* 메인 영역 라벨 텍스트 */
    .main label,
    .main [data-testid="stWidgetLabel"] {
        color: #374151 !important;
    }

    /* 캡션 텍스트 */
    .main [data-testid="stCaptionContainer"],
    .main .stCaption {
        color: #6B7280 !important;
    }

    /* ===== 사이드바 스타일 (밝은 배경) ===== */
    [data-testid="stSidebar"] {
        background-color: #F8FAFC !important;
        border-right: 1px solid #E5E7EB !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #111827 !important;
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
    [data-testid="stSidebar"] [data-testid="stCaption"],
    [data-testid="stSidebar"] .stCaption {
        color: #374151 !important;
    }

    /* 사이드바 모든 텍스트 */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
        color: #374151 !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: #E5E7EB !important;
        margin: 1.5rem 0 !important;
    }

    /* 사이드바 라디오 버튼 */
    [data-testid="stSidebar"] .stRadio > label {
        color: #374151 !important;
        font-weight: 500 !important;
    }

    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
        color: #374151 !important;
        font-size: 0.95rem !important;
        padding: 0.5rem 0.75rem !important;
        border-radius: 0.5rem !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p:hover {
        background: #E5E7EB !important;
    }

    /* 사이드바 Success/Error 메시지 */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: #F3F4F6 !important;
    }

    [data-testid="stSidebar"] [data-testid="stAlert"] p,
    [data-testid="stSidebar"] [data-testid="stAlert"] span {
        color: #374151 !important;
    }

    /* 사이드바 Expander */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: #F3F4F6 !important;
        color: #374151 !important;
        border: 1px solid #E5E7EB !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-top: none !important;
    }

    [data-testid="stSidebar"] .streamlit-expanderContent p,
    [data-testid="stSidebar"] .streamlit-expanderContent code {
        color: #374151 !important;
    }

    /* 사이드바 코드 */
    [data-testid="stSidebar"] code {
        background-color: #E5E7EB !important;
        color: #374151 !important;
    }

    /* 사이드바 Progress bar */
    [data-testid="stSidebar"] .stProgress > div > div {
        background: linear-gradient(90deg, #4F46E5 0%, #7C3AED 100%) !important;
    }

    [data-testid="stSidebar"] .stProgress {
        background-color: #E5E7EB !important;
    }

    /* ===== 버튼 스타일 ===== */
    .stButton > button {
        font-family: 'Noto Sans KR', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0.6rem 1.25rem !important;
        border-radius: 0.5rem !important;
        border: none !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
        color: white !important;
    }

    .stButton > button[kind="secondary"] {
        background: white !important;
        color: var(--gray-700) !important;
        border: 1px solid var(--gray-300) !important;
    }

    /* ===== SQL 에디터 (다크 배경) ===== */
    .stTextArea textarea {
        font-family: 'JetBrains Mono', 'Monaco', 'Menlo', monospace !important;
        font-size: 0.9rem !important;
        line-height: 1.6 !important;
        background-color: var(--gray-900) !important;
        color: #F3F4F6 !important;
        border: 2px solid var(--gray-700) !important;
        border-radius: 0.75rem !important;
        padding: 1rem !important;
        caret-color: #F3F4F6 !important;
    }

    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.2) !important;
    }

    .stTextArea textarea::placeholder {
        color: #9CA3AF !important;
    }

    /* SQL 에디터 레이블 (다크 배경 위) */
    .stTextArea label,
    .stTextArea [data-testid="stWidgetLabel"] {
        color: #374151 !important;
    }

    /* ===== 데이터프레임 ===== */
    .main .stDataFrame {
        border: 1px solid #E5E7EB !important;
        border-radius: 0.75rem !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
        background-color: white !important;
    }

    .main .stDataFrame [data-testid="stDataFrameResizable"] {
        border-radius: 0.75rem !important;
        background-color: white !important;
    }

    /* 데이터프레임 헤더와 셀 */
    .main .stDataFrame th {
        background-color: #F9FAFB !important;
        color: #374151 !important;
    }

    .main .stDataFrame td {
        background-color: white !important;
        color: #374151 !important;
    }

    /* ===== 탭 스타일 ===== */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem !important;
        background-color: #F3F4F6 !important;
        padding: 0.25rem !important;
        border-radius: 0.75rem !important;
    }

    .stTabs [data-baseweb="tab"] {
        font-family: 'Noto Sans KR', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        padding: 0.5rem 1rem !important;
        border-radius: 0.5rem !important;
        color: #374151 !important;
        background-color: transparent !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #111827 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: white !important;
        color: #4F46E5 !important;
        box-shadow: var(--shadow-sm) !important;
    }

    .stTabs [data-baseweb="tab-panel"] {
        background-color: white !important;
    }

    .stTabs [data-baseweb="tab-panel"] p,
    .stTabs [data-baseweb="tab-panel"] span,
    .stTabs [data-baseweb="tab-panel"] li {
        color: #374151 !important;
    }

    /* ===== Expander (메인 영역) ===== */
    .main .streamlit-expanderHeader {
        font-family: 'Noto Sans KR', sans-serif !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        color: #1F2937 !important;
        background-color: #F9FAFB !important;
        border-radius: 0.75rem !important;
        padding: 1rem !important;
        border: 1px solid #E5E7EB !important;
    }

    .main .streamlit-expanderContent {
        border: 1px solid #E5E7EB !important;
        border-top: none !important;
        border-radius: 0 0 0.75rem 0.75rem !important;
        padding: 1rem !important;
        background-color: white !important;
    }

    .main .streamlit-expanderContent p,
    .main .streamlit-expanderContent li,
    .main .streamlit-expanderContent span {
        color: #374151 !important;
    }

    /* ===== 알림 박스 (메인 영역) ===== */
    .main .stAlert {
        border-radius: 0.75rem !important;
        border: none !important;
        padding: 1rem 1.25rem !important;
    }

    .main [data-testid="stAlert"] > div {
        font-size: 0.95rem !important;
    }

    .main [data-testid="stAlert"] p {
        color: inherit !important;
    }

    /* ===== 셀렉트박스 전체 (강제 라이트 모드) ===== */
    [data-testid="stSelectbox"],
    .stSelectbox {
        background-color: transparent !important;
    }

    /* 셀렉트박스 컨테이너 */
    [data-testid="stSelectbox"] > div,
    .stSelectbox > div {
        background-color: white !important;
    }

    /* 셀렉트박스 입력 영역 */
    [data-testid="stSelectbox"] [data-baseweb="select"],
    .stSelectbox [data-baseweb="select"] {
        background-color: white !important;
        border-radius: 0.5rem !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div {
        background-color: white !important;
        border: 2px solid #E5E7EB !important;
        border-radius: 0.5rem !important;
        font-weight: 500 !important;
    }

    [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
    .stSelectbox [data-baseweb="select"] > div:focus-within {
        border-color: #4F46E5 !important;
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
    }

    /* 셀렉트박스 내부 모든 텍스트 - 검정색 (흰 배경) */
    [data-testid="stSelectbox"] span,
    [data-testid="stSelectbox"] div,
    [data-testid="stSelectbox"] p,
    [data-testid="stSelectbox"] input,
    .stSelectbox span,
    .stSelectbox div,
    .stSelectbox p {
        color: #374151 !important;
    }

    /* 셀렉트박스 선택된 값 표시 영역 */
    [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        color: #374151 !important;
    }

    /* 셀렉트박스 아이콘 */
    [data-testid="stSelectbox"] svg,
    .stSelectbox svg {
        fill: #6B7280 !important;
    }

    /* ===== 셀렉트박스 드롭다운 메뉴 (강제 라이트) ===== */
    [data-baseweb="popover"],
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    [role="listbox"],
    ul[role="listbox"],
    div[data-baseweb="popover"] {
        background-color: white !important;
        border: 1px solid #E5E7EB !important;
    }

    /* 드롭다운 옵션들 */
    [data-baseweb="popover"] li,
    [data-baseweb="menu"] li,
    [role="option"],
    li[role="option"] {
        color: #374151 !important;
        background-color: white !important;
    }

    [data-baseweb="popover"] li:hover,
    [data-baseweb="menu"] li:hover,
    [role="option"]:hover,
    li[role="option"]:hover {
        background-color: #F3F4F6 !important;
        color: #111827 !important;
    }

    [role="option"][aria-selected="true"],
    li[role="option"][aria-selected="true"] {
        background-color: #EEF2FF !important;
        color: #4F46E5 !important;
    }

    /* 드롭다운 내부 텍스트 */
    [role="listbox"] span,
    [role="listbox"] p,
    [role="listbox"] div,
    [role="option"] span,
    [role="option"] p,
    [role="option"] div {
        color: inherit !important;
    }

    /* ===== 인라인 코드 (밝은 배경) ===== */
    .main code:not(pre code) {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        background-color: #F3F4F6 !important;
        color: #3730A3 !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 0.25rem !important;
    }

    /* ===== 코드 블록 (다크 배경 - 흰 텍스트) ===== */
    .main .stCodeBlock,
    [data-testid="stCodeBlock"] {
        border-radius: 0.75rem !important;
        overflow: hidden !important;
    }

    .main .stCodeBlock code,
    .main .stCodeBlock pre,
    .main .stCodeBlock pre code,
    [data-testid="stCodeBlock"] code,
    [data-testid="stCodeBlock"] pre,
    [data-testid="stCodeBlock"] pre code,
    pre code {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: #1F2937 !important;
        color: #F3F4F6 !important;
    }

    /* 코드 블록 내부 모든 텍스트 - 밝은 색 */
    .main .stCodeBlock *,
    [data-testid="stCodeBlock"] * {
        color: #F3F4F6 !important;
    }

    /* 코드 블록 복사 버튼 */
    .main .stCodeBlock button,
    [data-testid="stCodeBlock"] button {
        color: #9CA3AF !important;
    }

    .main .stCodeBlock button:hover,
    [data-testid="stCodeBlock"] button:hover {
        color: #F3F4F6 !important;
    }

    /* ===== Divider ===== */
    hr {
        border: none !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, var(--gray-200), transparent) !important;
        margin: 2rem 0 !important;
    }

    /* ===== 메트릭 카드 ===== */
    .main [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
    }

    .main [data-testid="stMetricLabel"] {
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #4B5563 !important;
    }

    .main [data-testid="stMetricDelta"] {
        color: #059669 !important;
    }

    /* ===== 커스텀 카드 클래스 ===== */
    .custom-card {
        background: white;
        border: 1px solid var(--gray-200);
        border-radius: 1rem;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: var(--shadow);
        transition: all 0.2s ease;
    }

    .custom-card:hover {
        box-shadow: var(--shadow-md);
        border-color: var(--gray-300);
    }

    .module-card {
        background: linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%);
        border: 1px solid var(--gray-200);
        border-radius: 1rem;
        padding: 1.75rem;
        height: 100%;
        transition: all 0.3s ease;
    }

    .module-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-light);
    }

    .module-card h3 {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: var(--gray-900) !important;
        margin-bottom: 0.75rem !important;
    }

    .module-card p {
        font-size: 0.9rem !important;
        color: var(--gray-600) !important;
        line-height: 1.6 !important;
    }

    .module-card ul {
        margin: 0.75rem 0;
        padding-left: 1.25rem;
    }

    .module-card li {
        font-size: 0.9rem !important;
        color: var(--gray-600) !important;
        margin-bottom: 0.25rem;
    }

    .module-card .badge {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        margin-right: 0.5rem;
        margin-top: 0.75rem;
    }

    .badge-blue {
        background-color: #DBEAFE;
        color: #1D4ED8;
    }

    .badge-purple {
        background-color: #EDE9FE;
        color: #6D28D9;
    }

    .badge-green {
        background-color: #D1FAE5;
        color: #047857;
    }

    .badge-orange {
        background-color: #FED7AA;
        color: #C2410C;
    }

    /* ===== 문제 박스 ===== */
    .question-box {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
        border: 1px solid #BFDBFE;
        border-radius: 1rem;
        padding: 1.5rem;
        margin: 1rem 0;
    }

    .question-box .label {
        display: inline-block;
        font-size: 0.75rem;
        font-weight: 700;
        color: var(--primary);
        background: #DBEAFE;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        margin-bottom: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .question-box .content {
        font-size: 1rem;
        line-height: 1.8;
        color: var(--gray-800);
    }

    /* ===== 힌트 박스 ===== */
    .hint-box {
        background: linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 100%);
        border-left: 4px solid var(--warning);
        border-radius: 0 0.75rem 0.75rem 0;
        padding: 1rem 1.25rem;
        margin: 0.75rem 0;
    }

    .hint-box-blue {
        background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
        border-left-color: #3B82F6;
    }

    .hint-box-purple {
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        border-left-color: #7C3AED;
    }

    .hint-box .label {
        font-size: 0.85rem;
        font-weight: 700;
        color: var(--gray-800);
        margin-bottom: 0.5rem;
    }

    .hint-box .content {
        font-size: 0.95rem;
        line-height: 1.7;
        color: var(--gray-700);
        white-space: pre-wrap;
    }

    /* ===== 해설 박스 ===== */
    .explanation-box {
        background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
        border-left: 4px solid var(--success);
        border-radius: 0 0.75rem 0.75rem 0;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
    }

    .explanation-box .label {
        font-size: 0.85rem;
        font-weight: 700;
        color: #047857;
        margin-bottom: 0.5rem;
    }

    .explanation-box .content {
        font-size: 0.95rem;
        line-height: 1.8;
        color: var(--gray-700);
    }

    /* ===== 면접 TIP 박스 ===== */
    .tip-box {
        background: linear-gradient(135deg, #F5F3FF 0%, #EDE9FE 100%);
        border-left: 4px solid var(--purple);
        border-radius: 0 0.75rem 0.75rem 0;
        padding: 1.25rem 1.5rem;
        margin: 1rem 0;
    }

    .tip-box .label {
        font-size: 0.85rem;
        font-weight: 700;
        color: #5B21B6;
        margin-bottom: 0.5rem;
    }

    .tip-box .content {
        font-size: 0.95rem;
        line-height: 1.8;
        color: var(--gray-700);
    }

    /* ===== 섹션 타이틀 ===== */
    .section-title {
        font-size: 0.8rem;
        font-weight: 700;
        color: var(--gray-500);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 1rem;
    }

    /* ===== 히어로 섹션 ===== */
    .hero-section {
        background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%);
        color: white;
        border-radius: 1.5rem;
        padding: 2.5rem;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
    }

    .hero-section h1 {
        color: white !important;
        font-size: 2.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    .hero-section p {
        color: #E0E7FF !important;
        font-size: 1.1rem !important;
    }

    /* ===== 스탯 카드 ===== */
    .stat-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid var(--gray-200);
        box-shadow: var(--shadow);
    }

    .stat-card .number {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary);
        line-height: 1;
    }

    .stat-card .label {
        font-size: 0.9rem;
        color: var(--gray-600);
        margin-top: 0.5rem;
    }

    /* ===== 학습 단계 ===== */
    .step-item {
        display: flex;
        align-items: flex-start;
        padding: 1rem;
        background: var(--gray-50);
        border-radius: 0.75rem;
        margin-bottom: 0.75rem;
        border: 1px solid var(--gray-200);
    }

    .step-number {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        background: var(--primary);
        color: white;
        font-weight: 700;
        border-radius: 50%;
        margin-right: 1rem;
        flex-shrink: 0;
    }

    .step-content {
        flex: 1;
    }

    .step-content .title {
        font-weight: 600;
        color: var(--gray-800);
        margin-bottom: 0.25rem;
    }

    .step-content .desc {
        font-size: 0.9rem;
        color: var(--gray-600);
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
    """세션 상태 초기화 및 저장된 진행 데이터 로드"""
    # DB 테이블 초기화 (없으면 생성)
    if DB_PATH.exists():
        init_progress_table()

    # 첫 로드 시에만 DB에서 진행 데이터 불러오기
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
        st.session_state.completed_questions = {}
        st.session_state.user_queries = {}

        # DB에서 진행 데이터 로드
        if DB_PATH.exists():
            progress_data = load_all_progress()
            for qid, progress in progress_data.items():
                if progress.is_completed:
                    st.session_state.completed_questions[qid] = True
                if progress.last_query:
                    st.session_state.user_queries[qid] = progress.last_query

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
                "📖 개념 학습",
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
    elif module == "📖 개념 학습":
        from modules.concepts import show_concepts_module
        show_concepts_module()
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
    # 히어로 섹션
    st.markdown("""
    <div class="hero-section">
        <h1>CRM Analytics Lab</h1>
        <p>SQL로 배우는 실무 CRM 분석 · 직접 쿼리를 작성하며 데이터 기반 의사결정 역량을 키우세요</p>
    </div>
    """, unsafe_allow_html=True)

    # 스탯 카드
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="stat-card">
            <div class="number">30</div>
            <div class="label">실습 문제</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-card">
            <div class="number">5</div>
            <div class="label">학습 모듈</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-card">
            <div class="number">4</div>
            <div class="label">테이블</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        completed = len(st.session_state.get('completed_questions', {}))
        st.markdown(f"""
        <div class="stat-card">
            <div class="number">{completed}</div>
            <div class="label">완료한 문제</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.info("**처음이신가요?** 왼쪽 메뉴에서 `📖 개념 학습`을 먼저 확인하세요. AARRR 프레임워크, 지표 관계도 등 실습 전 알아야 할 핵심 개념을 정리했습니다.")

    st.divider()

    # 학습 모듈 카드
    st.markdown("### 학습 모듈")
    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="module-card">
            <h3>💰 LTV & CAC</h3>
            <p><strong>고객 생애 가치와 획득 비용</strong></p>
            <ul>
                <li>고객 LTV 계산</li>
                <li>채널별 CAC 분석</li>
                <li>LTV:CAC 비율 해석</li>
                <li>마케팅 ROI 평가</li>
            </ul>
            <span class="badge badge-blue">5문제</span>
            <span class="badge badge-green">기초</span>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="module-card">
            <h3>🔄 Funnel 분석</h3>
            <p><strong>전환 퍼널과 병목 분석</strong></p>
            <ul>
                <li>단계별 전환율</li>
                <li>이탈률 계산</li>
                <li>병목 지점 식별</li>
                <li>개선 우선순위</li>
            </ul>
            <span class="badge badge-blue">5문제</span>
            <span class="badge badge-green">기초</span>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="module-card">
            <h3>📅 Cohort 분석</h3>
            <p><strong>코호트 리텐션 분석</strong></p>
            <ul>
                <li>월별 코호트 생성</li>
                <li>리텐션 매트릭스</li>
                <li>Churn Rate 계산</li>
                <li>생존 분석</li>
            </ul>
            <span class="badge badge-blue">5문제</span>
            <span class="badge badge-purple">중급</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("""
        <div class="module-card">
            <h3>🎯 RFM 세그먼트</h3>
            <p><strong>고객 세그먼테이션</strong></p>
            <ul>
                <li>R/F/M 점수 계산</li>
                <li>5분위 분류</li>
                <li>세그먼트 정의</li>
                <li>타겟 마케팅</li>
            </ul>
            <span class="badge badge-blue">5문제</span>
            <span class="badge badge-purple">중급</span>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        st.markdown("""
        <div class="module-card">
            <h3>🧪 A/B 테스트</h3>
            <p><strong>실험 설계와 분석</strong></p>
            <ul>
                <li>전환율 비교</li>
                <li>Z-score 계산</li>
                <li>p-value 해석</li>
                <li>세그먼트별 분석</li>
            </ul>
            <span class="badge badge-blue">10문제</span>
            <span class="badge badge-orange">고급</span>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        st.markdown("""
        <div class="module-card">
            <h3>📊 My Dashboard</h3>
            <p><strong>학습 결과 시각화</strong></p>
            <ul>
                <li>산출한 지표 모아보기</li>
                <li>진행률 트래킹</li>
                <li>차트 시각화</li>
                <li>포트폴리오 정리</li>
            </ul>
            <span class="badge badge-purple">대시보드</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 학습 방법
    st.markdown("### 학습 방법")
    st.markdown("<br>", unsafe_allow_html=True)

    steps = [
        ("1", "문제 읽기", "요구사항과 비즈니스 맥락 이해"),
        ("2", "생각하기", "어떤 SQL이 필요할지 구상"),
        ("3", "SQL 작성", "직접 쿼리 작성"),
        ("4", "실행하기", "결과 확인 및 디버깅"),
        ("5", "정답 비교", "내 쿼리와 정답 비교"),
        ("6", "해설 읽기", "개념 정리 + 면접 TIP 확인"),
    ]

    col1, col2 = st.columns(2)
    for i, (num, title, desc) in enumerate(steps):
        with col1 if i < 3 else col2:
            st.markdown(f"""
            <div class="step-item">
                <div class="step-number">{num}</div>
                <div class="step-content">
                    <div class="title">{title}</div>
                    <div class="desc">{desc}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
