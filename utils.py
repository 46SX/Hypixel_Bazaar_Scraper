import sqlite3
import time
import os

def get_item_data(item, data):
    item_data = data[item]
    quick_data = item_data["quick_status"]
    sell_sum = item_data["sell_summary"]
    buy_sum = item_data["buy_summary"]

    def safe_calc(func, field="unknown", item="unknown"):
        try: return func()
        except Exception as e:
            print(f"safe_calc error [{item}] [{field}]: {e}", flush=True) 
            return 0

    def average(sum_data):
        total_cost = sum(listing["pricePerUnit"] * listing["amount"] for listing in sum_data)
        total_amount = sum(listing["amount"] for listing in sum_data)
        try: return total_cost / total_amount if total_amount > 0 else 0
        except: return "Error"


    average_sell_price      = safe_calc(lambda: average(sell_sum),                                                          "average_sell_price", item)
    average_buy_price       = safe_calc(lambda: average(buy_sum),                                                           "average_buy_price", item)
    spread_percent          = safe_calc(lambda: round((((average_buy_price - average_sell_price) / average_sell_price) * 100 if average_sell_price > 0 else 0), 2), "spread_percent", item)
    profit_margin           = safe_calc(lambda: round(quick_data["buyPrice"] - quick_data["sellPrice"], 2),                 "profit_margin", item)
    profit_percent          = safe_calc(lambda: round(profit_margin / quick_data["sellPrice"] * 100, 2),                    "profit_percent", item)
    average_sold_each_day   = safe_calc(lambda: round(quick_data["sellMovingWeek"] / 7, 2),                                 "average_sold_each_day", item)
    average_bought_each_day = safe_calc(lambda: round(quick_data["buyMovingWeek"] / 7, 2),                                  "average_bought_each_day", item)
    buy_to_sell_ratio       = safe_calc(lambda: round(quick_data["buyVolume"] / quick_data["sellVolume"], 2),               "buy_to_sell_ratio", item)
    order_density           = safe_calc(lambda: round(quick_data["buyOrders"] + quick_data["sellOrders"], 2),               "order_density", item)

    return {
        # -----------Normal-Data----------- # 
        "buy_price"               : quick_data["buyPrice"],              #Highest buy order (instant sell price)
        "sell_price"              : quick_data["sellPrice"],             #Lowest sell offer (instant buy price)
        "volume_of_sellorders"    : quick_data["sellVolume"],            #Amount up for sale
        "volume_of_buyorders"     : quick_data["buyVolume"],             #Amount up for purchase
        
        # ----------Enchaned-Data---------- #
        "profit_margin"           : profit_margin,                       #Diffrence between lowest sell order and highest buy order
        "profit_percent"          : profit_percent,                      #Profit_margin but in percent
        "average_sell_price"      : average_sell_price,                  #Average sell price
        "average_buy_price"       : average_buy_price,                   #Average buy price 
        "average_sold_each_day"   : average_sold_each_day,               #Average amount sold every day, calculated by dividing amount sold every week with 7
        "average_bought_each_day" : average_bought_each_day,              #Same thing but for the average bought every day ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        "order_density"           : order_density,                       #Total activity of a item (buyOrders + sellOrders)
        "spread_percent"          : spread_percent,                      #Diffrence between average buy and average sell in percent. Better than quick_status margin for finding flips
        "buy_to_sell_ratio"       : buy_to_sell_ratio                    #buyVolume/sellVolume, Basically demand and supply =)
    }

def create_db(path=os.path.expanduser("~/data/scraper/bazaar")):
    os.makedirs(path, exist_ok=True)
    db_file = os.path.join(path, "bazaar.db")
    
    already_exists = os.path.exists(db_file)
    conn = sqlite3.connect(db_file)
    
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
                avg_bought_per_day      REAL
            )
        """)
        conn.commit()
        print("Databas skapad!")
    else:
        print("Databas hittad, ansluter...")
        # Migrera befintlig databas
        existing = [row[1] for row in conn.execute("PRAGMA table_info(prices)")]
        new_cols = {
            "volume_of_buyorders":  "REAL",
            "volume_of_sellorders": "REAL",
            "avg_sold_per_day":     "REAL",
            "avg_bought_per_day":   "REAL"
        }
        for col, typ in new_cols.items():
            if col not in existing:
                conn.execute(f"ALTER TABLE prices ADD COLUMN {col} {typ}")
                print(f"Kolumn tillagd: {col}")
        conn.commit()
    
    return conn

def log_item(conn, item_name, data):
    item = get_item_data(item_name, data)
    conn.execute("""
        INSERT INTO prices VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        item["average_bought_each_day"]
    ))
    conn.commit()
