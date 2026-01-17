"""
결과 뷰어 컴포넌트
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Literal

class ResultViewer:
    """쿼리 결과 시각화"""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def show_table(self, title: str = "결과"):
        """테이블 표시"""
        st.subheader(f"📋 {title}")
        st.dataframe(self.df, width="stretch")

    def show_bar_chart(
        self,
        x: str,
        y: str,
        title: str = "",
        color: str | None = None,
        orientation: Literal["v", "h"] = "v"
    ):
        """바 차트"""
        fig = px.bar(
            self.df,
            x=x,
            y=y,
            title=title,
            color=color,
            orientation=orientation,
            template="plotly_white"
        )
        fig.update_layout(
            font_family="Pretendard, sans-serif",
            title_font_size=16,
            showlegend=color is not None
        )
        st.plotly_chart(fig, width="stretch")

    def show_line_chart(
        self,
        x: str,
        y: str,
        title: str = "",
        color: str | None = None
    ):
        """라인 차트"""
        fig = px.line(
            self.df,
            x=x,
            y=y,
            title=title,
            color=color,
            markers=True,
            template="plotly_white"
        )
        fig.update_layout(
            font_family="Pretendard, sans-serif",
            title_font_size=16
        )
        st.plotly_chart(fig, width="stretch")

    def show_pie_chart(
        self,
        names: str,
        values: str,
        title: str = ""
    ):
        """파이 차트"""
        fig = px.pie(
            self.df,
            names=names,
            values=values,
            title=title,
            template="plotly_white"
        )
        fig.update_layout(
            font_family="Pretendard, sans-serif",
            title_font_size=16
        )
        st.plotly_chart(fig, width="stretch")

    def show_funnel(
        self,
        stage_col: str,
        value_col: str,
        title: str = ""
    ):
        """퍼널 차트"""
        fig = go.Figure(go.Funnel(
            y=self.df[stage_col],
            x=self.df[value_col],
            textposition="inside",
            textinfo="value+percent previous",
            marker=dict(
                color=["#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE", "#DBEAFE"][:len(self.df)]
            )
        ))
        fig.update_layout(
            title=title,
            font_family="Pretendard, sans-serif",
            title_font_size=16,
            template="plotly_white"
        )
        st.plotly_chart(fig, width="stretch")

    def show_heatmap(
        self,
        x: str,
        y: str,
        z: str,
        title: str = ""
    ):
        """히트맵"""
        pivot_df = self.df.pivot(index=y, columns=x, values=z)

        fig = px.imshow(
            pivot_df,
            title=title,
            color_continuous_scale="Blues",
            aspect="auto",
            template="plotly_white"
        )
        fig.update_layout(
            font_family="Pretendard, sans-serif",
            title_font_size=16
        )
        st.plotly_chart(fig, width="stretch")

    def show_metrics(self, metrics: list[dict]):
        """
        메트릭 카드 표시

        Args:
            metrics: [{"label": "LTV", "value": 97000, "delta": "+5%"}, ...]
        """
        cols = st.columns(len(metrics))

        for col, metric in zip(cols, metrics):
            with col:
                st.metric(
                    label=metric.get("label", ""),
                    value=metric.get("value", ""),
                    delta=metric.get("delta"),
                    delta_color=metric.get("delta_color", "normal")
                )


def compare_results(user_df: pd.DataFrame, answer_df: pd.DataFrame) -> bool:
    """
    사용자 결과와 정답 비교

    Args:
        user_df: 사용자 쿼리 결과
        answer_df: 정답 쿼리 결과

    Returns:
        bool: 일치 여부
    """
    if user_df is None or answer_df is None:
        return False

    # 컬럼 수와 행 수 비교
    if user_df.shape != answer_df.shape:
        return False

    # 컬럼명 비교 (순서 무관)
    if set(user_df.columns) != set(answer_df.columns):
        return False

    # 값 비교 (컬럼 순서 맞춤)
    user_sorted = user_df[sorted(user_df.columns)].sort_values(
        by=list(sorted(user_df.columns))
    ).reset_index(drop=True)

    answer_sorted = answer_df[sorted(answer_df.columns)].sort_values(
        by=list(sorted(answer_df.columns))
    ).reset_index(drop=True)

    # 숫자 컬럼은 반올림 후 비교
    for col in user_sorted.columns:
        if user_sorted[col].dtype in ['float64', 'float32']:
            user_sorted[col] = user_sorted[col].round(2)
            answer_sorted[col] = answer_sorted[col].round(2)

    try:
        return user_sorted.equals(answer_sorted)
    except Exception:
        return False
