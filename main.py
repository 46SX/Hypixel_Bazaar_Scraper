from scraper import *
from utils import *
import threading
import time
import os


path = os.path.expanduser("~/data/bazaar")

# Data Updater
data = {}
def update_data():
    while True:
        global data
        data = get_data()

dataupdate_thread = threading.Thread(target=update_data)
dataupdate_thread.daemon = True
dataupdate_thread.start()

if not os.path.exists(path):
    os.makedirs(path, exist_ok=True)
conn = make
    

    






