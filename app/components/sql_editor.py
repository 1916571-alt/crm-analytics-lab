"""
SQL 에디터 컴포넌트
"""

import streamlit as st
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "learning" / "data" / "crm.db"

class SQLEditor:
    """SQL 에디터 및 실행기"""

    def __init__(self, key: str, default_query: str = "", height: int = 200):
        self.key = key
        self.default_query = default_query
        self.height = height

    def render(self) -> tuple[str, pd.DataFrame | None, str | None]:
        """
        SQL 에디터 렌더링

        Returns:
            tuple: (입력된 쿼리, 결과 DataFrame, 에러 메시지)
        """
        # 섹션 제목
        st.markdown("""
        <div style="margin-bottom: 0.75rem;">
            <span style="font-size: 0.8rem; font-weight: 700; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em;">SQL EDITOR</span>
        </div>
        """, unsafe_allow_html=True)

        # SQL 입력
        query = st.text_area(
            "SQL 쿼리 입력",
            value=self.default_query,
            height=self.height,
            key=f"sql_editor_{self.key}",
            placeholder="SELECT * FROM customers LIMIT 10",
            label_visibility="collapsed"
        )

        # 버튼 행
        col1, col2, col3 = st.columns([1, 1, 3])

        with col1:
            run_clicked = st.button("실행", key=f"run_{self.key}", type="primary")

        with col2:
            clear_clicked = st.button("초기화", key=f"clear_{self.key}")

        # 초기화 버튼 클릭 시
        if clear_clicked:
            st.session_state[f"sql_editor_{self.key}"] = self.default_query
            st.rerun()

        # 실행 버튼 클릭 시
        result_df = None
        error = None

        if run_clicked and query.strip():
            result_df, error = self._execute_query(query)

            # 결과를 세션에 저장
            st.session_state[f"result_{self.key}"] = result_df
            st.session_state[f"error_{self.key}"] = error
            st.session_state[f"last_query_{self.key}"] = query

        # 이전 결과 표시
        elif f"result_{self.key}" in st.session_state:
            result_df = st.session_state.get(f"result_{self.key}")
            error = st.session_state.get(f"error_{self.key}")

        return query, result_df, error

    def _execute_query(self, query: str) -> tuple[pd.DataFrame | None, str | None]:
        """SQL 쿼리 실행"""
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df, None
        except Exception as e:
            return None, str(e)


def render_sql_editor(
    key: str,
    default_query: str = "",
    height: int = 200,
    show_result: bool = True
) -> tuple[str, pd.DataFrame | None]:
    """
    간편한 SQL 에디터 함수

    Args:
        key: 고유 키
        default_query: 기본 쿼리
        height: 에디터 높이
        show_result: 결과 표시 여부

    Returns:
        tuple: (쿼리, 결과 DataFrame)
    """
    editor = SQLEditor(key, default_query, height)
    query, result_df, error = editor.render()

    if show_result:
        if error:
            st.error(f"오류: {error}")
        elif result_df is not None:
            st.markdown("""
            <div style="margin-top: 1rem; margin-bottom: 0.5rem;">
                <span style="font-size: 0.8rem; font-weight: 700; color: #059669; text-transform: uppercase; letter-spacing: 0.05em;">RESULT</span>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(result_df, use_container_width=True)
            st.caption(f"{len(result_df)}개 행 반환")

    return query, result_df
