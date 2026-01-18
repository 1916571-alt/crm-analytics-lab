"""
학습 진행 저장 관리자

사용자의 학습 진행 상태를 SQLite에 영구 저장합니다.
- 문제별 완료 여부
- 시도 횟수
- 마지막 제출 쿼리
- 완료 시간
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional

DB_PATH = Path(__file__).parent.parent.parent / "learning" / "data" / "crm.db"


@dataclass
class QuestionProgress:
    """문제별 진행 상태"""
    question_id: str
    is_completed: bool = False
    attempts: int = 0
    last_query: str = ""
    solved_at: Optional[str] = None


def init_progress_table():
    """user_progress 테이블 생성 (없으면 생성)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_progress (
            question_id TEXT PRIMARY KEY,
            is_completed INTEGER DEFAULT 0,
            attempts INTEGER DEFAULT 0,
            last_query TEXT DEFAULT '',
            solved_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_progress(question_id: str, is_completed: bool, query: str):
    """
    문제 진행 상태 저장

    Args:
        question_id: 문제 고유 ID
        is_completed: 정답 여부
        query: 제출한 쿼리
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 기존 데이터 확인
    cursor.execute(
        "SELECT attempts, is_completed FROM user_progress WHERE question_id = ?",
        (question_id,)
    )
    row = cursor.fetchone()

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if row:
        # 기존 데이터 업데이트
        attempts = row[0] + 1
        was_completed = row[1]

        # 이미 완료된 문제는 완료 상태 유지
        final_completed = 1 if (is_completed or was_completed) else 0
        solved_at = now if is_completed and not was_completed else None

        if solved_at:
            cursor.execute("""
                UPDATE user_progress
                SET is_completed = ?, attempts = ?, last_query = ?,
                    solved_at = ?, updated_at = ?
                WHERE question_id = ?
            """, (final_completed, attempts, query, solved_at, now, question_id))
        else:
            cursor.execute("""
                UPDATE user_progress
                SET is_completed = ?, attempts = ?, last_query = ?, updated_at = ?
                WHERE question_id = ?
            """, (final_completed, attempts, query, now, question_id))
    else:
        # 새 데이터 삽입
        solved_at = now if is_completed else None
        cursor.execute("""
            INSERT INTO user_progress
            (question_id, is_completed, attempts, last_query, solved_at, created_at, updated_at)
            VALUES (?, ?, 1, ?, ?, ?, ?)
        """, (question_id, 1 if is_completed else 0, query, solved_at, now, now))

    conn.commit()
    conn.close()


def load_all_progress() -> dict[str, QuestionProgress]:
    """
    모든 진행 상태 로드

    Returns:
        dict: {question_id: QuestionProgress} 형태
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT question_id, is_completed, attempts, last_query, solved_at
        FROM user_progress
    """)

    rows = cursor.fetchall()
    conn.close()

    progress_dict = {}
    for row in rows:
        progress_dict[row[0]] = QuestionProgress(
            question_id=row[0],
            is_completed=bool(row[1]),
            attempts=row[2],
            last_query=row[3] or "",
            solved_at=row[4]
        )

    return progress_dict


def get_progress(question_id: str) -> Optional[QuestionProgress]:
    """
    특정 문제 진행 상태 조회

    Args:
        question_id: 문제 고유 ID

    Returns:
        QuestionProgress 또는 None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT question_id, is_completed, attempts, last_query, solved_at
        FROM user_progress
        WHERE question_id = ?
    """, (question_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return QuestionProgress(
            question_id=row[0],
            is_completed=bool(row[1]),
            attempts=row[2],
            last_query=row[3] or "",
            solved_at=row[4]
        )
    return None


def get_completed_count() -> int:
    """완료된 문제 수 반환"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM user_progress WHERE is_completed = 1")
    count = cursor.fetchone()[0]

    conn.close()
    return count


def get_stats() -> dict:
    """
    학습 통계 반환

    Returns:
        dict: {
            'completed': 완료 문제 수,
            'attempted': 시도한 문제 수,
            'total_attempts': 총 시도 횟수
        }
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(CASE WHEN is_completed = 1 THEN 1 END) as completed,
            COUNT(*) as attempted,
            SUM(attempts) as total_attempts
        FROM user_progress
    """)

    row = cursor.fetchone()
    conn.close()

    return {
        'completed': row[0] or 0,
        'attempted': row[1] or 0,
        'total_attempts': row[2] or 0
    }


def reset_progress():
    """모든 진행 상태 초기화 (개발/테스트용)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM user_progress")

    conn.commit()
    conn.close()
