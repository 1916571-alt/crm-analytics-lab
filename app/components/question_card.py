"""
문제 카드 컴포넌트
"""

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Callable

DB_PATH = Path(__file__).parent.parent.parent / "learning" / "data" / "crm.db"

@dataclass
class Question:
    """문제 데이터 클래스"""
    id: str
    title: str
    description: str
    hint: str
    answer_query: str
    explanation: str
    interview_tip: str
    difficulty: int  # 1-5


class QuestionCard:
    """
    문제 카드 - 문제 → 힌트 → SQL 작성 → 실행 → 정답 비교 → 해설
    """

    def __init__(self, question: Question, module_key: str):
        self.question = question
        self.module_key = module_key
        self.key = f"{module_key}_{question.id}"

    def render(self) -> bool:
        """
        문제 카드 렌더링

        Returns:
            bool: 정답 여부
        """
        q = self.question

        # 난이도 표시
        difficulty_stars = "⭐" * q.difficulty

        # 제목
        st.markdown(f"### {q.title} {difficulty_stars}")

        # 문제 설명
        st.markdown(f"""
        <div style="background-color: #F3F4F6; color: #1F2937; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <strong>📋 문제</strong><br>
            {q.description}
        </div>
        """, unsafe_allow_html=True)

        # 힌트 (접기/펼치기)
        with st.expander("💡 힌트 보기", expanded=False):
            st.markdown(q.hint)

        # SQL 에디터
        st.markdown("**✏️ SQL 작성**")

        query = st.text_area(
            "SQL 입력",
            value=st.session_state.get(f"query_{self.key}", ""),
            height=180,
            key=f"editor_{self.key}",
            label_visibility="collapsed",
            placeholder="SELECT ..."
        )

        # 쿼리 저장
        st.session_state[f"query_{self.key}"] = query

        # 버튼 행
        col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

        with col1:
            run_clicked = st.button("▶️ 실행", key=f"run_{self.key}", type="primary")

        with col2:
            check_clicked = st.button("✅ 정답 확인", key=f"check_{self.key}")

        with col3:
            clear_clicked = st.button("🔄 초기화", key=f"clear_{self.key}")

        # 초기화
        if clear_clicked:
            st.session_state[f"query_{self.key}"] = ""
            st.session_state[f"result_{self.key}"] = None
            st.session_state[f"checked_{self.key}"] = False
            st.rerun()

        # 실행
        is_correct = False

        if run_clicked and query.strip():
            result_df, error = self._execute_query(query)
            st.session_state[f"result_{self.key}"] = result_df
            st.session_state[f"error_{self.key}"] = error

        # 결과 표시
        if f"result_{self.key}" in st.session_state:
            result_df = st.session_state.get(f"result_{self.key}")
            error = st.session_state.get(f"error_{self.key}")

            if error:
                st.error(f"❌ 오류: {error}")
            elif result_df is not None:
                st.markdown("**📊 실행 결과**")
                st.dataframe(result_df, width="stretch")
                st.caption(f"{len(result_df)}개 행 반환")

        # 정답 확인
        if check_clicked:
            st.session_state[f"checked_{self.key}"] = True

        if st.session_state.get(f"checked_{self.key}", False):
            st.divider()

            # 정답 쿼리 실행
            answer_df, _ = self._execute_query(q.answer_query)

            # 정답 비교
            user_result = st.session_state.get(f"result_{self.key}")

            if user_result is not None and answer_df is not None:
                is_correct = self._compare_results(user_result, answer_df)

                if is_correct:
                    st.success("🎉 정답입니다!")
                    # 완료 표시
                    st.session_state.completed_questions[self.key] = True
                else:
                    st.warning("❌ 결과가 다릅니다. 다시 시도해보세요.")

            # 정답 쿼리
            with st.expander("📝 정답 쿼리", expanded=True):
                st.code(q.answer_query, language="sql")

                if answer_df is not None:
                    st.markdown("**정답 결과:**")
                    st.dataframe(answer_df, width="stretch")

            # 해설
            st.markdown(f"""
            <div style="background-color: #D1FAE5; color: #1F2937; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; border-left: 4px solid #10B981;">
                <strong>📖 해설</strong><br>
                {q.explanation}
            </div>
            """, unsafe_allow_html=True)

            # 면접 TIP
            st.markdown(f"""
            <div style="background-color: #EDE9FE; color: #1F2937; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; border-left: 4px solid #8B5CF6;">
                <strong>💼 면접 TIP</strong><br>
                {q.interview_tip}
            </div>
            """, unsafe_allow_html=True)

        return is_correct

    def _execute_query(self, query: str) -> tuple[pd.DataFrame | None, str | None]:
        """SQL 쿼리 실행"""
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df, None
        except Exception as e:
            return None, str(e)

    def _compare_results(self, user_df: pd.DataFrame, answer_df: pd.DataFrame) -> bool:
        """결과 비교"""
        if user_df is None or answer_df is None:
            return False

        # 행 수 비교
        if len(user_df) != len(answer_df):
            return False

        # 컬럼 수 비교
        if len(user_df.columns) != len(answer_df.columns):
            return False

        # 값 비교 (숫자는 반올림)
        try:
            user_sorted = user_df.copy()
            answer_sorted = answer_df.copy()

            # 숫자 컬럼 반올림
            for col in user_sorted.select_dtypes(include=['float64', 'float32']).columns:
                user_sorted[col] = user_sorted[col].round(2)

            for col in answer_sorted.select_dtypes(include=['float64', 'float32']).columns:
                answer_sorted[col] = answer_sorted[col].round(2)

            # 값만 비교 (컬럼명 무시)
            user_values = user_sorted.values.tolist()
            answer_values = answer_sorted.values.tolist()

            # 정렬 후 비교
            user_values.sort(key=str)
            answer_values.sort(key=str)

            return user_values == answer_values
        except Exception:
            return False
