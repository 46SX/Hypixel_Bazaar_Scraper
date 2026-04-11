import sqlite3
import time
import os

DB_PATH = os.path.expanduser("~/data/scraper/bazaar")
DB_FILE = os.path.join(DB_PATH, "bazaar.db")


def get_item_data(item, data):
    item_data = data[item]
    quick = item_data["quick_status"]
    sell_summary = item_data["sell_summary"]
    buy_summary = item_data["buy_summary"]

    def safe(func, field="unknown"):
        try:
            return func()
        except Exception as e:
            print(f"[{item}] {field}: {e}", flush=True)
            return None

    def weighted_avg(summary):
        if not summary:
            return None
        total_cost = sum(l["pricePerUnit"] * l["amount"] for l in summary)
        total_amount = sum(l["amount"] for l in summary)
        return total_cost / total_amount if total_amount > 0 else None

    def depth_within_pct(summary, top_price, pct, side="buy"):
        if not summary or not top_price or top_price <= 0:
            return None
        total = 0
        for level in summary:
            price = level["pricePerUnit"]
            if side == "buy":
                if price >= top_price * (1 - pct / 100):
                    total += price * level["amount"]
            else:
                if price <= top_price * (1 + pct / 100):
                    total += price * level["amount"]
        return total if total > 0 else None

    buy_price = quick["buyPrice"]
    sell_price = quick["sellPrice"]

    avg_sell = safe(lambda: weighted_avg(sell_summary), "avg_sell_price")
    avg_buy = safe(lambda: weighted_avg(buy_summary), "avg_buy_price")

    profit_margin = safe(
        lambda: round(buy_price - sell_price, 2),
        "profit_margin"
    )

    profit_percent = safe(
        lambda: round(profit_margin / sell_price * 100, 2) if sell_price > 0 else None,
        "profit_percent"
    )

    spread_percent = safe(
        lambda: round((avg_buy - avg_sell) / avg_sell * 100, 2)
        if avg_sell and avg_buy and avg_sell > 0 else None,
        "spread_percent"
    )

    buy_to_sell_ratio = safe(
        lambda: round(quick["buyVolume"] / quick["sellVolume"], 2)
        if quick["sellVolume"] > 0 else None,
        "buy_to_sell_ratio"
    )

    avg_sold_per_day = safe(
        lambda: round(quick["sellMovingWeek"] / 7, 2),
        "avg_sold_per_day"
    )

    avg_bought_per_day = safe(
        lambda: round(quick["buyMovingWeek"] / 7, 2),
        "avg_bought_per_day"
    )

    buy_depth_1pct = safe(
        lambda: depth_within_pct(buy_summary, buy_price, 1, "buy"),
        "buy_depth_1pct"
    )

    sell_depth_1pct = safe(
        lambda: depth_within_pct(sell_summary, sell_price, 1, "sell"),
        "sell_depth_1pct"
    )

    book_imbalance = safe(
        lambda: round(buy_depth_1pct / sell_depth_1pct, 3)
        if buy_depth_1pct and sell_depth_1pct and sell_depth_1pct > 0 else None,
        "book_imbalance"
    )

    return {
        "buy_price":               buy_price,
        "sell_price":              sell_price,
        "volume_of_sellorders":    quick["sellVolume"],
        "volume_of_buyorders":     quick["buyVolume"],
        "profit_margin":           profit_margin,
        "profit_percent":          profit_percent,
        "average_sell_price":      avg_sell,
        "average_buy_price":       avg_buy,
        "average_sold_each_day":   avg_sold_per_day,
        "average_bought_each_day": avg_bought_per_day,
        "order_density":           quick["buyOrders"] + quick["sellOrders"],
        "spread_percent":          spread_percent,
        "buy_to_sell_ratio":       buy_to_sell_ratio,
        "buy_order_count":         quick["buyOrders"],
        "sell_order_count":        quick["sellOrders"],
        "buy_depth_1pct":          buy_depth_1pct,
        "sell_depth_1pct":         sell_depth_1pct,
        "book_imbalance":          book_imbalance,
    }


def create_db(path=DB_PATH):
    os.makedirs(path, exist_ok=True)
    db_file = os.path.join(path, "bazaar.db")

    already_exists = os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    conn.execute("PRAGMA journal_mode=WAL")

    if not already_exists:
        conn.execute("""
            CREATE TABLE prices (
                id                      INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp               INTEGER,
                item                    TEXT,
                buy_price               REAL,
                sell_price              REAL,
                profit_margin           REAL,
                profit_percent          REAL,
                spread_percent          REAL,
                buy_to_sell             REAL,
                order_density           REAL,
                avg_sell_price          REAL,
                avg_buy_price           REAL,
                volume_of_buyorders     REAL,
                volume_of_sellorders    REAL,
                avg_sold_per_day        REAL,
                avg_bought_per_day      REAL,
                buy_order_count         INTEGER,
                sell_order_count        INTEGER,
                buy_depth_1pct          REAL,
                sell_depth_1pct         REAL,
                book_imbalance          REAL
            )
        """)
        conn.commit()
        print("Databas skapad!")
    else:
        print("Databas hittad, ansluter...")
        existing = [row[1] for row in conn.execute("PRAGMA table_info(prices)")]
        new_cols = {
            "volume_of_buyorders":  "REAL",
            "volume_of_sellorders": "REAL",
            "avg_sold_per_day":     "REAL",
            "avg_bought_per_day":   "REAL",
            "buy_order_count":      "INTEGER",
            "sell_order_count":     "INTEGER",
            "buy_depth_1pct":       "REAL",
            "sell_depth_1pct":      "REAL",
            "book_imbalance":       "REAL",
        }
        for col, typ in new_cols.items():
            if col not in existing:
                conn.execute(f"ALTER TABLE prices ADD COLUMN {col} {typ}")
                print(f"Kolumn tillagd: {col}")
        conn.commit()

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_prices_ts_item
        ON prices(timestamp, item)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_prices_item_ts
        ON prices(item, timestamp)
    """)
    conn.commit()

    return conn


def log_item(conn, item_name, data):
    item = get_item_data(item_name, data)
    conn.execute("""
        INSERT INTO prices VALUES (
            NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?
        )
    """, (
        int(time.time()),
        item_name,
        item["buy_price"],
        item["sell_price"],
        item["profit_margin"],
        item["profit_percent"],
        item["spread_percent"],
        item["buy_to_sell_ratio"],
        item["order_density"],
        item["average_sell_price"],
        item["average_buy_price"],
        item["volume_of_buyorders"],
        item["volume_of_sellorders"],
        item["average_sold_each_day"],
        item["average_bought_each_day"],
        item["buy_order_count"],
        item["sell_order_count"],
        item["buy_depth_1pct"],
        item["sell_depth_1pct"],
        item["book_imbalance"],
    ))
