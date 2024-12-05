import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime, timedelta
import argparse
import logging
import time

# Load the environment variables
load_dotenv()

PIXELFED_ACCESS_TOKEN = os.getenv("PIXELFED_ACCESS_TOKEN")
PIXELFED_INSTANCE = os.getenv("PIXELFED_INSTANCE")
PIXELFED_USERNAME = os.getenv("PIXELFED_USERNAME")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_PAGE_ID = os.getenv("INSTAGRAM_PAGE_ID")

PIXELFED_API_URL = f"https://{PIXELFED_INSTANCE}/api/v1"
INSTAGRAM_GRAPH_API_URL = f"https://graph.facebook.com/v21.0/{INSTAGRAM_PAGE_ID}/media"
POSTED_LOG_FILE = "posted.logs.json"

# Helper function to load already posted IDs
def load_posted_ids():
    if os.path.exists(POSTED_LOG_FILE):
        with open(POSTED_LOG_FILE, 'r') as file:
            return json.load(file)
    return []

# Helper function to save posted IDs
def save_posted_ids(posted_ids):
    with open(POSTED_LOG_FILE, 'w') as file:
        json.dump(posted_ids, file)

# Debugging function
def debug_api_request(url, headers=None, params=None, data=None, method="GET"):
    if not logging.getLogger().isEnabledFor(logging.DEBUG):
        return

    logging.debug("=== API Debugging ===")
    logging.debug(f"Method: {method}")
    logging.debug(f"URL: {url}")
    if headers:
        logging.debug(f"Headers: {headers}")
    if params:
        logging.debug(f"Parameters: {json.dumps(params, indent=2)}")
    if data:
        logging.debug(f"Data: {json.dumps(data, indent=2)}")

    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, data=data)
        else:
            logging.error(f"Unsupported method: {method}")
            return None

        log_request_response(response)
        return response
    except requests.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None

# Log request and response
def log_request_response(response, description="API Call"):
    logging.debug(f"=== {description} ===")
    if response.request:
        logging.debug(f"Request Method: {response.request.method}")
        logging.debug(f"Request URL: {response.request.url}")
        logging.debug(f"Request Headers: {response.request.headers}")
        logging.debug(f"Request Body: {response.request.body}")
    logging.debug(f"Response Status Code: {response.status_code}")
    try:
        logging.debug(f"Response JSON: {json.dumps(response.json(), indent=2)}")
    except ValueError:
        logging.debug(f"Response Text: {response.text}")

# Validate access token
def validate_access_token(token):
    debug_url = f"https://graph.facebook.com/debug_token?input_token={token}&access_token={token}"
    response = debug_api_request(debug_url, method="GET")
    if response and response.status_code == 200:
        data = response.json().get("data", {})
        if data.get("is_valid"):
            logging.debug(f"Access token is valid. Scopes: {data.get('scopes', [])}")
        else:
            logging.error("Access token is invalid or expired.")
            exit(1)
    else:
        logging.error("Failed to validate access token.")
        exit(1)

# Validate Instagram Page ID
def validate_instagram_page_id(page_id, token):
    url = f"https://graph.facebook.com/v21.0/{page_id}?fields=instagram_business_account&access_token={token}"
    response = debug_api_request(url, method="GET")
    if response and response.status_code == 200:
        data = response.json()
        if "instagram_business_account" in data:
            logging.debug("Instagram Business Account is correctly linked.")
        else:
            logging.error("Instagram Business Account is not linked to this page.")
            exit(1)
    else:
        logging.error("Failed to validate Instagram Page ID.")
        exit(1)

# Retrieve all Pixelfed posts
def get_all_pixelfed_posts(start_date, end_date):
    url = f"{PIXELFED_API_URL}/accounts/{PIXELFED_USERNAME}/statuses"
    headers = {"Authorization": f"Bearer {PIXELFED_ACCESS_TOKEN}"}
    params = {"limit": 40}
    all_posts = []

    while True:
        debug_api_request(url, headers=headers, params=params, method="GET")
        response = requests.get(url, headers=headers, params=params)
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
            logging.error(f"Error retrieving Pixelfed posts: {response.status_code}")
            break
    return all_posts

# Post to Instagram
def post_to_instagram(media_urls, caption):
    instagram_media_ids = []
    for media_url in media_urls:
        data = {"image_url": media_url, "access_token": INSTAGRAM_ACCESS_TOKEN}
        debug_api_request(INSTAGRAM_GRAPH_API_URL, data=data, method="POST")
        response = requests.post(INSTAGRAM_GRAPH_API_URL, data=data)
        if response.status_code == 200:
            media_id = response.json().get("id")
            instagram_media_ids.append(media_id)
        else:
            logging.error(f"Error uploading image to Instagram: {response.status_code}")
            return False

    if len(instagram_media_ids) > 1:
        data = {
            "media_type": "CAROUSEL",
            "caption": caption,
            "children": instagram_media_ids,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
    else:
        data = {
            "media_type": "IMAGE",
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
            "media_id": instagram_media_ids[0]
        }
    debug_api_request(f"{INSTAGRAM_GRAPH_API_URL}/media_publish", data=data, method="POST")
    response = requests.post(f"{INSTAGRAM_GRAPH_API_URL}/media_publish", data=data)
    return response.status_code == 200

# Throttle posting
def throttle_posting(posted_ids):
    now = datetime.now()
    last_hour_posts = [p for p in posted_ids if datetime.strptime(p['timestamp'], "%Y-%m-%dT%H:%M:%S") > now - timedelta(hours=1)]
    if len(last_hour_posts) >= 10:
        time_to_wait = 3600 - (now - datetime.strptime(last_hour_posts[0]['timestamp'], "%Y-%m-%dT%H:%M:%S")).seconds
        time.sleep(time_to_wait)

# Parse date
def parse_iso_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%d")

# Main program
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Pixelfed posts to Instagram.")
    parser.add_argument("start_date", type=parse_iso_datetime, help="Start date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("end_date", type=parse_iso_datetime, help="End date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed logging output")

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    validate_access_token(INSTAGRAM_ACCESS_TOKEN)
    validate_instagram_page_id(INSTAGRAM_PAGE_ID, INSTAGRAM_ACCESS_TOKEN)

    posted_ids = load_posted_ids()
    pixelfed_posts = get_all_pixelfed_posts(args.start_date, args.end_date)
    for post in pixelfed_posts:
        if post['id'] in [p['id'] for p in posted_ids]:
            continue
        throttle_posting(posted_ids)
        media_urls = [media['url'] for media in post.get('media_attachments', [])]
        caption = post.get('caption', '')
        if post_to_instagram(media_urls, caption):
            posted_ids.append({'id': post['id'], 'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
            save_posted_ids(posted_ids)
