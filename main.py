from scraper import *
from utils import *
import threading
import time

data = {}

def update_data():
    while True:
        global data
        data = get_data()

dataupdate_thread = threading.Thread(target=update_data)
dataupdate_thread.daemon = True
dataupdate_thread.start()

while not data:
    time.sleep(0.1)

databefore = None

while data:

    item = get_item_data("ENCHANTED_MUTTON", data[0])

    if item != databefore: 
        print(item)
        databefore = item
        
    






