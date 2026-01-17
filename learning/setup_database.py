"""
학습용 SQLite 데이터베이스 생성 스크립트

실행: python learning/setup_database.py
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import sys
from pathlib import Path

# 프로젝트 루트 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.data_generator import generate_customers, generate_transactions, generate_campaigns

DB_PATH = Path(__file__).parent / "data" / "crm.db"


def create_database():
    """학습용 데이터베이스 생성"""

    print("데이터베이스 생성 중...")

    # 데이터 생성 (더 많은 데이터로 실습 효과 증대)
    customers = generate_customers(n_customers=2000, seed=42)
    transactions = generate_transactions(customers, seed=42)
    campaigns = generate_campaigns(n_campaigns=50, seed=42)

    # 이벤트 로그 데이터 추가 생성 (Funnel 분석용)
    events = generate_events(customers, seed=42)

    # SQLite 연결
    conn = sqlite3.connect(DB_PATH)

    # 테이블 생성 및 데이터 삽입
    customers.to_sql("customers", conn, if_exists="replace", index=False)
    transactions.to_sql("transactions", conn, if_exists="replace", index=False)
    campaigns.to_sql("campaigns", conn, if_exists="replace", index=False)
    events.to_sql("events", conn, if_exists="replace", index=False)

    # 인덱스 생성 (쿼리 성능 향상)
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_customers_id ON customers(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_customer ON transactions(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(transaction_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_user ON events(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date)")

    conn.commit()
    conn.close()

    print(f"데이터베이스 생성 완료: {DB_PATH}")
    print(f"- customers: {len(customers)} rows")
    print(f"- transactions: {len(transactions)} rows")
    print(f"- campaigns: {len(campaigns)} rows")
    print(f"- events: {len(events)} rows")


def generate_events(customers: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """
    Funnel 분석용 이벤트 로그 생성

    이벤트 종류:
    - page_view: 페이지 조회
    - product_view: 상품 조회
    - add_to_cart: 장바구니 추가
    - checkout_start: 결제 시작
    - purchase: 구매 완료
    """
    np.random.seed(seed)
    random.seed(seed)

    event_types = ["page_view", "product_view", "add_to_cart", "checkout_start", "purchase"]
    # 각 단계별 전환율 (누적)
    conversion_probs = [1.0, 0.6, 0.25, 0.15, 0.08]

    events = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)

    for _, customer in customers.iterrows():
        user_id = customer["customer_id"]

        # 사용자당 세션 수
        n_sessions = np.random.randint(1, 20)

        for _ in range(n_sessions):
            session_date = start_date + timedelta(days=np.random.randint(0, 730))
            session_id = f"S{np.random.randint(100000, 999999)}"

            # Funnel 진행
            current_time = session_date
            for i, (event_type, prob) in enumerate(zip(event_types, conversion_probs)):
                if np.random.random() > prob:
                    break

                events.append({
                    "event_id": f"E{len(events)}",
                    "user_id": user_id,
                    "session_id": session_id,
                    "event_type": event_type,
                    "event_date": current_time.strftime("%Y-%m-%d"),
                    "event_timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "page_url": f"/{'home' if i == 0 else event_type}",
                    "device": np.random.choice(["mobile", "desktop", "tablet"], p=[0.6, 0.35, 0.05]),
                    "channel": customer["acquisition_channel"]
                })

                # 다음 이벤트까지 시간 간격
                current_time += timedelta(minutes=np.random.randint(1, 30))

    return pd.DataFrame(events)


if __name__ == "__main__":
    create_database()
