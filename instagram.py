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

    def check_permissions(self):
        """Check all permissions for the current access token."""
        logging.info("Checking permissions for the access token...")
        permissions_url = f"https://graph.facebook.com/v21.0/me/permissions?access_token={self.access_token}"
        response = requests.get(permissions_url)
        if response.status_code == 200:
            permissions = response.json().get("data", [])
            valid_permissions = [perm['permission'] for perm in permissions if perm['status'] == 'granted']
            denied_permissions = [perm['permission'] for perm in permissions if perm['status'] == 'declined']
            logging.info(f"Granted permissions: {valid_permissions}")
            logging.warning(f"Denied permissions: {denied_permissions}")
        else:
            logging.error(f"Failed to fetch permissions. Status code: {response.status_code}, Response: {response.text}")

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
                self.log_error_details(response)
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
            self.log_error_details(response)
            return False

    def log_error_details(self, response):
        """Log detailed error information from the API response."""
        try:
            error_details = response.json().get("error", {})
            message = error_details.get("message", "No message provided")
            error_type = error_details.get("type", "No type provided")
            code = error_details.get("code", "No code provided")
            subcode = error_details.get("error_subcode", "No subcode provided")
            fbtrace_id = error_details.get("fbtrace_id", "No fbtrace_id provided")

            logging.error(f"Error Details: Message: {message}, Type: {error_type}, "
                          f"Code: {code}, Subcode: {subcode}, FBTrace ID: {fbtrace_id}")
        except Exception as e:
            logging.error(f"Failed to parse error details: {e}")
            logging.debug(f"Raw response: {response.text}")
