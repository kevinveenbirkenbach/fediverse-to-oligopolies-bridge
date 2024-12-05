import json
import os
import logging
from datetime import datetime, timedelta
import time

def load_posted_ids(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return []

def save_posted_ids(file_path, posted_ids):
    with open(file_path, 'w') as file:
        json.dump(posted_ids, file)

def throttle_posting(posted_ids, max_per_hour=10):
    now = datetime.now()
    last_hour_posts = [p for p in posted_ids if datetime.strptime(p['timestamp'], "%Y-%m-%dT%H:%M:%S") > now - timedelta(hours=1)]
    if len(last_hour_posts) >= max_per_hour:
        time_to_wait = 3600 - (now - datetime.strptime(last_hour_posts[0]['timestamp'], "%Y-%m-%dT%H:%M:%S")).seconds
        logging.info(f"Throttling: Waiting for {time_to_wait} seconds.")
        time.sleep(time_to_wait)
