"""
결과 기반 채점 시스템

SQL 쿼리 결과를 비교하여 정답 여부와 부분 점수를 판정합니다.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CheckStatus(Enum):
    """채점 결과 상태"""
    CORRECT = "correct"           # 완전 정답
    PARTIAL = "partial"           # 부분 정답
    WRONG = "wrong"               # 오답
    ERROR = "error"               # 실행 오류


@dataclass
class CheckResult:
    """채점 결과"""
    status: CheckStatus
    score: int                    # 0-100 점수
    message: str                  # 메인 메시지
    details: list[str]            # 상세 피드백 목록

    @property
    def is_correct(self) -> bool:
        return self.status == CheckStatus.CORRECT

    @property
    def is_partial(self) -> bool:
        return self.status == CheckStatus.PARTIAL


class ResultChecker:
    """
    결과 기반 채점기

    채점 기준:
    - 행 수 일치: 30점
    - 컬럼 수 일치: 20점
    - 값 일치: 50점

    옵션:
    - ignore_column_names: 컬럼명 무시 (기본값: True)
    - ignore_order: 행 순서 무시 (기본값: True)
    - float_precision: 소수점 비교 정밀도 (기본값: 2)
    """

    def __init__(
        self,
        ignore_column_names: bool = True,
        ignore_order: bool = True,
        float_precision: int = 2
    ):
        self.ignore_column_names = ignore_column_names
        self.ignore_order = ignore_order
        self.float_precision = float_precision

    def check(
        self,
        user_result: Optional[pd.DataFrame],
        answer_result: Optional[pd.DataFrame]
    ) -> CheckResult:
        """
        사용자 결과와 정답 결과 비교

        Args:
            user_result: 사용자 쿼리 실행 결과
            answer_result: 정답 쿼리 실행 결과

        Returns:
            CheckResult: 채점 결과
        """
        details = []
        score = 0

        # 결과가 없는 경우
        if user_result is None:
            return CheckResult(
                status=CheckStatus.ERROR,
                score=0,
                message="쿼리를 실행해주세요.",
                details=["실행 버튼을 눌러 쿼리 결과를 확인하세요."]
            )

        if answer_result is None:
            return CheckResult(
                status=CheckStatus.ERROR,
                score=0,
                message="정답 쿼리 실행 오류",
                details=["시스템 오류입니다. 관리자에게 문의하세요."]
            )

        # 빈 결과 처리
        if len(user_result) == 0 and len(answer_result) == 0:
            return CheckResult(
                status=CheckStatus.CORRECT,
                score=100,
                message="정답입니다!",
                details=["빈 결과가 정답입니다."]
            )

        if len(user_result) == 0:
            return CheckResult(
                status=CheckStatus.WRONG,
                score=0,
                message="결과가 없습니다.",
                details=[f"정답은 {len(answer_result)}개 행을 반환합니다."]
            )

        # 1. 행 수 비교 (30점)
        row_score, row_detail = self._check_row_count(user_result, answer_result)
        score += row_score
        if row_detail:
            details.append(row_detail)

        # 2. 컬럼 수 비교 (20점)
        col_score, col_detail = self._check_column_count(user_result, answer_result)
        score += col_score
        if col_detail:
            details.append(col_detail)

        # 3. 값 비교 (50점)
        value_score, value_details = self._check_values(user_result, answer_result)
        score += value_score
        details.extend(value_details)

        # 최종 판정
        if score == 100:
            return CheckResult(
                status=CheckStatus.CORRECT,
                score=100,
                message="정답입니다!",
                details=["모든 검증을 통과했습니다."]
            )
        elif score >= 50:
            return CheckResult(
                status=CheckStatus.PARTIAL,
                score=score,
                message=f"부분 정답 ({score}점)",
                details=details
            )
        else:
            return CheckResult(
                status=CheckStatus.WRONG,
                score=score,
                message="오답입니다.",
                details=details
            )

    def _check_row_count(
        self,
        user_df: pd.DataFrame,
        answer_df: pd.DataFrame
    ) -> tuple[int, str]:
        """행 수 비교 (30점 만점)"""
        user_rows = len(user_df)
        answer_rows = len(answer_df)

        if user_rows == answer_rows:
            return 30, ""

        diff = abs(user_rows - answer_rows)
        diff_pct = diff / answer_rows * 100

        # 차이에 따른 부분 점수
        if diff_pct <= 10:
            partial_score = 20
        elif diff_pct <= 30:
            partial_score = 10
        else:
            partial_score = 0

        direction = "많습니다" if user_rows > answer_rows else "적습니다"
        detail = f"행 수가 {direction}. (내 결과: {user_rows}행, 정답: {answer_rows}행)"

        return partial_score, detail

    def _check_column_count(
        self,
        user_df: pd.DataFrame,
        answer_df: pd.DataFrame
    ) -> tuple[int, str]:
        """컬럼 수 비교 (20점 만점)"""
        user_cols = len(user_df.columns)
        answer_cols = len(answer_df.columns)

        if user_cols == answer_cols:
            return 20, ""

        direction = "많습니다" if user_cols > answer_cols else "적습니다"
        detail = f"컬럼 수가 {direction}. (내 결과: {user_cols}개, 정답: {answer_cols}개)"

        # 컬럼 수가 다르면 0점
        return 0, detail

    def _check_values(
        self,
        user_df: pd.DataFrame,
        answer_df: pd.DataFrame
    ) -> tuple[int, list[str]]:
        """값 비교 (50점 만점)"""
        details = []

        # 컬럼 수가 다르면 값 비교 불가
        if len(user_df.columns) != len(answer_df.columns):
            return 0, ["컬럼 수가 달라 값 비교가 불가능합니다."]

        # 행 수가 다르면 값 비교 제한
        if len(user_df) != len(answer_df):
            return 0, ["행 수가 달라 값 비교가 불가능합니다."]

        try:
            # DataFrame 정규화
            user_normalized = self._normalize_df(user_df)
            answer_normalized = self._normalize_df(answer_df)

            # 정렬 옵션
            if self.ignore_order:
                user_sorted = self._sort_df(user_normalized)
                answer_sorted = self._sort_df(answer_normalized)
            else:
                user_sorted = user_normalized
                answer_sorted = answer_normalized

            # 값 비교
            user_values = user_sorted.values.tolist()
            answer_values = answer_sorted.values.tolist()

            if user_values == answer_values:
                return 50, []

            # 부분 일치 분석
            match_count = 0
            total_rows = len(answer_values)

            for user_row in user_values:
                if user_row in answer_values:
                    match_count += 1

            match_pct = match_count / total_rows * 100

            if match_pct >= 80:
                partial_score = 40
                details.append(f"대부분의 값이 일치합니다. ({match_pct:.0f}% 일치)")
            elif match_pct >= 50:
                partial_score = 25
                details.append(f"일부 값이 일치합니다. ({match_pct:.0f}% 일치)")
            elif match_pct > 0:
                partial_score = 10
                details.append(f"값이 많이 다릅니다. ({match_pct:.0f}% 일치)")
            else:
                partial_score = 0
                details.append("값이 일치하지 않습니다.")

            # 값 차이 분석 힌트
            value_hint = self._analyze_value_difference(user_sorted, answer_sorted)
            if value_hint:
                details.append(value_hint)

            return partial_score, details

        except Exception as e:
            return 0, [f"값 비교 중 오류: {str(e)}"]

    def _normalize_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame 정규화"""
        result = df.copy()

        # 컬럼명 정규화 (ignore_column_names 옵션)
        if self.ignore_column_names:
            result.columns = [f"col_{i}" for i in range(len(result.columns))]

        # 숫자 반올림
        for col in result.select_dtypes(include=['float64', 'float32']).columns:
            result[col] = result[col].round(self.float_precision)

        # 문자열 정규화
        for col in result.select_dtypes(include=['object']).columns:
            result[col] = result[col].astype(str).str.strip().str.lower()

        return result

    def _sort_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """DataFrame 정렬 (비교용)"""
        try:
            # 모든 컬럼을 문자열로 변환 후 정렬
            sort_key = df.astype(str).apply(lambda x: '|'.join(x), axis=1)
            return df.iloc[sort_key.argsort()].reset_index(drop=True)
        except Exception:
            return df

    def _analyze_value_difference(
        self,
        user_df: pd.DataFrame,
        answer_df: pd.DataFrame
    ) -> str:
        """값 차이 분석 힌트 생성"""
        try:
            # 첫 번째 행 비교
            if len(user_df) > 0 and len(answer_df) > 0:
                user_first = user_df.iloc[0].values
                answer_first = answer_df.iloc[0].values

                # 숫자 컬럼에서 차이 분석
                for i, (u, a) in enumerate(zip(user_first, answer_first)):
                    if isinstance(u, (int, float)) and isinstance(a, (int, float)):
                        if u != 0 and a != 0:
                            ratio = u / a
                            if 0.9 <= ratio <= 1.1:
                                continue  # 10% 이내면 무시
                            elif ratio > 1:
                                return f"일부 숫자 값이 {ratio:.1f}배 큽니다. 집계 기준을 확인하세요."
                            else:
                                return f"일부 숫자 값이 {1/ratio:.1f}배 작습니다. 필터 조건을 확인하세요."
        except Exception:
            pass

        return ""


# 기본 채점기 인스턴스
default_checker = ResultChecker()


def check_result(
    user_result: Optional[pd.DataFrame],
    answer_result: Optional[pd.DataFrame]
) -> CheckResult:
    """기본 채점기로 결과 비교"""
    return default_checker.check(user_result, answer_result)
