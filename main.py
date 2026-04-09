from scraper import *
from utils import *
from notis import notify
import threading
import time
import os

data = {}
data_ready = threading.Event()

def update_data():
    global data
    conn = create_db()  
    while True:
        try:
            result = get_data()
            if result:
                data, last_updated = result
                data_ready.set()
                for item_name in data.keys():
                    log_item(conn, item_name, data)
                notify("Succesful Update", title="Scraper", priority="low", tags="Bazaar")
            else:
                notify("Failed to fetch data!", title="Scraper", priority="high", tags="warning")
        except Exception as e:
            print(f"FEL I UPDATE_DATA: {e}", flush=True)
        
        time.sleep(300)

dataupdate_thread = threading.Thread(target=update_data)
dataupdate_thread.daemon = True
dataupdate_thread.start()

data_ready.wait() 
print("Kör! Loggar data var 5:e minut...")

while True:
    time.sleep(1)