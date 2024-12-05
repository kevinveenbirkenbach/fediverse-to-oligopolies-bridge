import requests
import logging
from datetime import datetime
from config import PIXELFED_API_URL, PIXELFED_ACCESS_TOKEN, PIXELFED_USERNAME
from utils import throttle_posting

class Pixelfed:
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {PIXELFED_ACCESS_TOKEN}"}

    def get_posts(self, start_date, end_date):
        url = f"{PIXELFED_API_URL}/accounts/{PIXELFED_USERNAME}/statuses"
        params = {"limit": 40}
        all_posts = []

        while True:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                data = response.json()
                if not data:
                    break
                for post in data:
                    post_date = datetime.strptime(post['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
                    if start_date <= post_date <= end_date:
                        all_posts.append(post)
                params['max_id'] = data[-1]['id']
            else:
                logging.error(f"Error fetching Pixelfed posts: {response.status_code}")
                break
        return all_posts
