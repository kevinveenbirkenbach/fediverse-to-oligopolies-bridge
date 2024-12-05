import requests
import logging
from config import INSTAGRAM_GRAPH_API_URL, INSTAGRAM_ACCESS_TOKEN

class Instagram:
    def __init__(self):
        self.access_token = INSTAGRAM_ACCESS_TOKEN

    def validate_access_token(self):
        debug_url = f"https://graph.facebook.com/debug_token?input_token={self.access_token}&access_token={self.access_token}"
        response = requests.get(debug_url)
        if response.status_code == 200:
            data = response.json().get("data", {})
            if not data.get("is_valid"):
                logging.error("Invalid or expired access token.")
                exit(1)
        else:
            logging.error("Failed to validate access token.")
            exit(1)

    def upload_media(self, media_urls, caption):
        media_ids = []
        for url in media_urls:
            data = {"image_url": url, "access_token": self.access_token}
            response = requests.post(INSTAGRAM_GRAPH_API_URL, data=data)
            if response.status_code == 200:
                media_ids.append(response.json().get("id"))
            else:
                logging.error(f"Error uploading media: {response.status_code}")
                return False
        return self.publish_post(media_ids, caption)

    def publish_post(self, media_ids, caption):
        if len(media_ids) > 1:
            data = {
                "media_type": "CAROUSEL",
                "caption": caption,
                "children": media_ids,
                "access_token": self.access_token
            }
        else:
            data = {
                "media_type": "IMAGE",
                "caption": caption,
                "access_token": self.access_token,
                "media_id": media_ids[0]
            }
        response = requests.post(f"{INSTAGRAM_GRAPH_API_URL}/media_publish", data=data)
        return response.status_code == 200
