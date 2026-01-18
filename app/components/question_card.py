"""
문제 카드 컴포넌트
"""

import streamlit as st
import pandas as pd
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Callable
from components.progress_manager import save_progress, get_progress
from components.result_checker import check_result, CheckStatus

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

        # 완료 상태 확인
        is_already_completed = self.key in st.session_state.get('completed_questions', {})
        completed_badge = " ✅" if is_already_completed else ""

        # 제목
        st.markdown(f"### {q.title} {difficulty_stars}{completed_badge}")

        # 문제 설명
        st.markdown(f"""
        <div style="background-color: #F3F4F6; color: #1F2937; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
            <strong>📋 문제</strong><br>
            {q.description}
        </div>
        """, unsafe_allow_html=True)

        # 단계별 힌트
        self._render_step_hints(q.hint)

        # SQL 에디터
        st.markdown("**✏️ SQL 작성**")

        # 저장된 쿼리 불러오기 (세션 또는 DB에서)
        saved_query = ""
        if f"query_{self.key}" in st.session_state:
            saved_query = st.session_state.get(f"query_{self.key}", "")
        elif self.key in st.session_state.get('user_queries', {}):
            saved_query = st.session_state.user_queries[self.key]

        query = st.text_area(
            "SQL 입력",
            value=saved_query,
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

            # 결과 기반 채점
            user_result = st.session_state.get(f"result_{self.key}")
            check_result_obj = check_result(user_result, answer_df)

            # 채점 결과 표시
            if check_result_obj.status == CheckStatus.CORRECT:
                st.success(f"🎉 {check_result_obj.message}")
                is_correct = True
                # 완료 표시 (세션 + DB 저장)
                st.session_state.completed_questions[self.key] = True
                save_progress(self.key, is_completed=True, query=query)

            elif check_result_obj.status == CheckStatus.PARTIAL:
                st.warning(f"⚠️ {check_result_obj.message}")
                # 부분 점수 진행바
                st.progress(check_result_obj.score / 100)
                # 상세 피드백
                with st.expander("📋 상세 피드백", expanded=True):
                    for detail in check_result_obj.details:
                        st.markdown(f"- {detail}")
                # 오답 저장
                save_progress(self.key, is_completed=False, query=query)

            elif check_result_obj.status == CheckStatus.WRONG:
                st.error(f"❌ {check_result_obj.message}")
                # 상세 피드백
                if check_result_obj.details:
                    with st.expander("📋 상세 피드백", expanded=True):
                        for detail in check_result_obj.details:
                            st.markdown(f"- {detail}")
                # 오답 저장
                save_progress(self.key, is_completed=False, query=query)

            else:  # ERROR
                st.info(f"ℹ️ {check_result_obj.message}")

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

    def _render_step_hints(self, hint: str):
        """
        단계별 힌트 렌더링

        힌트 형식:
        - "---" 구분자로 단계 분리
        - 구분자가 없으면 단일 힌트로 표시

        단계별 제목:
        - 1단계: 접근 방향
        - 2단계: 필요한 함수/문법
        - 3단계: 쿼리 뼈대
        """
        # 힌트 단계 분리
        steps = self._parse_hint_steps(hint)
        total_steps = len(steps)

        # 단계별 제목
        step_titles = [
            "🎯 1단계: 접근 방향",
            "🔧 2단계: 필요한 함수/문법",
            "📝 3단계: 쿼리 뼈대"
        ]

        # 현재 공개된 힌트 단계 (세션 상태)
        hint_key = f"hint_step_{self.key}"
        if hint_key not in st.session_state:
            st.session_state[hint_key] = 0  # 0 = 힌트 미공개

        current_step = st.session_state[hint_key]

        # 힌트 컨테이너
        with st.container():
            # 힌트 버튼
            col1, col2, col3 = st.columns([1, 1, 3])

            with col1:
                if current_step < total_steps:
                    next_step_label = f"💡 힌트 {current_step + 1}/{total_steps}"
                    if st.button(next_step_label, key=f"hint_btn_{self.key}"):
                        st.session_state[hint_key] = current_step + 1
                        st.rerun()
                else:
                    st.caption(f"💡 힌트 {total_steps}/{total_steps} (모두 공개)")

            with col2:
                if current_step > 0:
                    if st.button("🔒 힌트 숨기기", key=f"hint_hide_{self.key}"):
                        st.session_state[hint_key] = 0
                        st.rerun()

            # 공개된 힌트 표시
            if current_step > 0:
                for i in range(current_step):
                    step_title = step_titles[i] if i < len(step_titles) else f"💡 힌트 {i + 1}"
                    step_content = steps[i] if i < len(steps) else ""

                    # 단계별 색상
                    colors = ["#FEF3C7", "#DBEAFE", "#E0E7FF"]  # 노랑, 파랑, 보라
                    border_colors = ["#F59E0B", "#3B82F6", "#6366F1"]

                    bg_color = colors[i % len(colors)]
                    border_color = border_colors[i % len(border_colors)]

                    st.markdown(f"""
                    <div style="background-color: {bg_color}; color: #1F2937; padding: 0.75rem 1rem;
                                border-radius: 0.5rem; margin: 0.5rem 0; border-left: 4px solid {border_color};">
                        <strong>{step_title}</strong><br>
                        <span style="white-space: pre-wrap;">{step_content}</span>
                    </div>
                    """, unsafe_allow_html=True)

    def _parse_hint_steps(self, hint: str) -> list[str]:
        """
        힌트 문자열을 단계별로 분리

        구분자: "---" 또는 "## Step" 또는 "**1단계**" 등
        """
        # "---" 구분자로 분리
        if "---" in hint:
            steps = [s.strip() for s in hint.split("---") if s.strip()]
            return steps

        # "## " 헤더로 분리
        if "## " in hint:
            import re
            parts = re.split(r'\n## ', hint)
            steps = [p.strip() for p in parts if p.strip()]
            return steps

        # 구분자 없으면 단일 힌트
        return [hint.strip()]

    def _execute_query(self, query: str) -> tuple[pd.DataFrame | None, str | None]:
        """SQL 쿼리 실행"""
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df, None
        except Exception as e:
            return None, str(e)

