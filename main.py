from scraper import *
from utils import *
from notis import notify
import threading
import time
import os

data = {}
data_ready = threading.Event()

conn = create_db()

def update_data():
    global data
    while True:
        result = get_data()
        if result:
            data, last_updated = result
            data_ready.set()
            for item_name in data.keys():
                log_item(conn, item_name, data)
        
        notify("Succesful Update", title="Scraper", priority="low", tags="Bazaar")
        
        time.sleep(300)

dataupdate_thread = threading.Thread(target=update_data)
dataupdate_thread.daemon = True
dataupdate_thread.start()

data_ready.wait()  # Vänta tills första datan är hämtad
print("Kör! Loggar data var 5:e minut...")