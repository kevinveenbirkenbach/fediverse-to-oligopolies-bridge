import requests
import logging
from config import INSTAGRAM_GRAPH_API_URL, INSTAGRAM_ACCESS_TOKEN

class Instagram:
    def __init__(self):
        self.access_token = INSTAGRAM_ACCESS_TOKEN
        logging.info("Initialized Instagram client with provided access token.")

    def validate_access_token(self):
        logging.info("Validating Instagram access token...")
        debug_url = f"https://graph.facebook.com/debug_token?input_token={self.access_token}&access_token={self.access_token}"
        response = requests.get(debug_url)
        if response.status_code == 200:
            data = response.json().get("data", {})
            if data.get("is_valid"):
                logging.info("Access token is valid.")
            else:
                logging.error("Invalid or expired access token.")
                exit(1)
        else:
            logging.error(f"Failed to validate access token. Status code: {response.status_code}")
            exit(1)

    def upload_media(self, media_urls, caption):
        logging.info(f"Uploading {len(media_urls)} media items to Instagram...")
        media_ids = []
        for url in media_urls:
            logging.info(f"Uploading media from URL: {url}")
            data = {"image_url": url, "access_token": self.access_token}
            response = requests.post(INSTAGRAM_GRAPH_API_URL, data=data)
            if response.status_code == 200:
                media_id = response.json().get("id")
                media_ids.append(media_id)
                logging.info(f"Successfully uploaded media. Media ID: {media_id}")
            else:
                logging.error(f"Error uploading media. Status code: {response.status_code}, Response: {response.text}")
                return False
        logging.info("All media items uploaded successfully.")
        return self.publish_post(media_ids, caption)

    def publish_post(self, media_ids, caption):
        if len(media_ids) > 1:
            logging.info("Publishing a carousel post to Instagram...")
            data = {
                "media_type": "CAROUSEL",
                "caption": caption,
                "children": media_ids,
                "access_token": self.access_token
            }
        else:
            logging.info("Publishing a single image post to Instagram...")
            data = {
                "media_type": "IMAGE",
                "caption": caption,
                "access_token": self.access_token,
                "media_id": media_ids[0]
            }

        response = requests.post(f"{INSTAGRAM_GRAPH_API_URL}/media_publish", data=data)
        if response.status_code == 200:
            logging.info("Post published successfully to Instagram.")
            return True
        else:
            logging.error(f"Error publishing post. Status code: {response.status_code}, Response: {response.text}")
            return False
