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

# Pixelfed API URL
PIXELFED_API_URL = f"https://{PIXELFED_INSTANCE}/api/v1"

# Instagram API URL
INSTAGRAM_GRAPH_API_URL = f"https://graph.facebook.com/v21.0/{INSTAGRAM_PAGE_ID}/media"

# File to store posted Pixelfed post IDs and timestamps
POSTED_LOG_FILE = "posted.logs.json"

# Helper function to load already posted IDs and timestamps
def load_posted_ids():
    if os.path.exists(POSTED_LOG_FILE):
        with open(POSTED_LOG_FILE, 'r') as file:
            return json.load(file)
    return []

# Helper function to save posted IDs and timestamps
def save_posted_ids(posted_ids):
    with open(POSTED_LOG_FILE, 'w') as file:
        json.dump(posted_ids, file)

# Debugging function
def debug_api_request(url, headers=None, params=None, data=None, method="GET"):
    """
    Debug an API request by logging the details and the response.
    """
    if not logging.getLogger().isEnabledFor(logging.DEBUG):
        return  # Only run if verbose is enabled

    logging.debug("=== API Debugging ===")
    logging.debug(f"Method: {method}")
    logging.debug(f"URL: {url}")
    if headers:
        logging.debug(f"Headers: {headers}")
    if params:
        logging.debug(f"Parameters: {json.dumps(params, indent=2)}")
    if data:
        logging.debug(f"Data: {json.dumps(data, indent=2)}")

    # Make the request and log the response
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, data=data)
        else:
            logging.error(f"Unsupported method: {method}")
            return None

        logging.debug(f"Response Status Code: {response.status_code}")
        try:
            logging.debug(f"Response JSON: {json.dumps(response.json(), indent=2)}")
        except ValueError:
            logging.debug(f"Response Text: {response.text}")

        return response

    except requests.RequestException as e:
        logging.error(f"API request failed: {e}")
        return None

# Function to retrieve all Pixelfed posts between two timestamps with pagination
def get_all_pixelfed_posts(start_date, end_date):
    url = f"{PIXELFED_API_URL}/accounts/{PIXELFED_USERNAME}/statuses"
    headers = {
        "Authorization": f"Bearer {PIXELFED_ACCESS_TOKEN}"
    }
    
    params = {
        "limit": 40  # Max number of posts per request
    }

    all_posts = []
    
    while True:
        # Debug the request
        debug_api_request(url, headers=headers, params=params, method="GET")
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if not data:
                logging.debug(f"No more posts to retrieve")
                break

            for post in data:
                post_date = datetime.strptime(post['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
                
                if start_date <= post_date <= end_date:
                    logging.debug(f"Post {post['id']} created on {post['created_at']} is within the date range.")
                    all_posts.append(post)
                else:
                    logging.debug(f"Post {post['id']} created on {post['created_at']} is outside the date range.")

            if datetime.strptime(data[-1]['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ") < start_date:
                logging.debug(f"All posts until {start_date} loaded.")
                break

            # Paginate by using the ID of the last post in the current batch
            params['max_id'] = data[-1]['id']
        
        elif response.status_code == 404:
            logging.error(f"Endpoint not found. URL: {url}")
            break
        elif response.status_code == 401:
            logging.error("Unauthorized access. Check your token.")
            break
        else:
            logging.error(f"Error retrieving Pixelfed posts: {response.status_code}")
            break
    
    return all_posts

# Function to post a gallery or single entry to Instagram
def post_to_instagram(media_urls, caption):
    instagram_media_ids = []
    for media_url in media_urls:
        data = {
            "image_url": media_url,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
        # Debug the request
        debug_api_request(INSTAGRAM_GRAPH_API_URL, data=data, method="POST")
        response = requests.post(f"{INSTAGRAM_GRAPH_API_URL}", data=data)
        
        if response.status_code == 200:
            media_id = response.json().get("id")
            instagram_media_ids.append(media_id)
            logging.info(f"Image uploaded successfully. Media ID: {media_id}")
        else:
            logging.error(f"Error uploading image to Instagram.\nREQUEST:\n - URL:{INSTAGRAM_GRAPH_API_URL}\n - DATA:{data}\nResponse:\n - STATUS_CODE: {response.status_code}\n - TEXT: {response.text}")
            return False

    # Step 2: Create the carousel (multi-image post)
    if len(instagram_media_ids) > 1:
        data = {
            "media_type": "CAROUSEL",
            "caption": caption,
            "children": instagram_media_ids,
            "access_token": INSTAGRAM_ACCESS_TOKEN
        }
    else:
        # Single image post
        data = {
            "media_type": "IMAGE",
            "caption": caption,
            "access_token": INSTAGRAM_ACCESS_TOKEN,
            "media_id": instagram_media_ids[0]
        }
    
    # Debug the publish request
    debug_api_request(f"{INSTAGRAM_GRAPH_API_URL}/media_publish", data=data, method="POST")
    
    # Finalize the post
    response = requests.post(f"{INSTAGRAM_GRAPH_API_URL}/media_publish", data=data)
    
    if response.status_code == 200:
        logging.info("Post successfully sent to Instagram.")
        return True
    else:
        logging.error(f"Error publishing post to Instagram: {response.status_code}")
        return False

# Throttle function to ensure max 10 posts per hour
def throttle_posting(posted_ids):
    now = datetime.now()
    # Filter posts from the last hour
    last_hour_posts = [post for post in posted_ids if datetime.strptime(post['timestamp'], "%Y-%m-%dT%H:%M:%S") > now - timedelta(hours=1)]
    
    if len(last_hour_posts) >= 10:
        logging.info("Posting limit reached. Waiting for 1 hour.")
        # Wait for the next available post slot
        time_to_wait = 3600 - (now - datetime.strptime(last_hour_posts[0]['timestamp'], "%Y-%m-%dT%H:%M:%S")).seconds
        logging.debug(f"Sleeping for {time_to_wait} seconds.")
        time.sleep(time_to_wait)

# Helper function to parse date and datetime in ISO 8601 format
def parse_iso_datetime(date_str):
    try:
        # Try to parse full ISO 8601 datetime format
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        try:
            # Fallback to just date format (YYYY-MM-DD)
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise argparse.ArgumentTypeError(f"Invalid date or datetime format: {date_str}. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.")

# Main program
if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Sync Pixelfed posts to Instagram.")
    parser.add_argument("start_date", type=parse_iso_datetime, help="Start date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("end_date", type=parse_iso_datetime, help="End date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed logging output")

    # Parse arguments
    args = parser.parse_args()

    # Set logging level based on verbose argument
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    start_date = args.start_date
    end_date = args.end_date

    # Load already posted IDs
    posted_ids = load_posted_ids()

    # Retrieve Pixelfed posts
    logging.info(f"Retrieving posts from Pixelfed between {start_date} and {end_date}.")
    pixelfed_posts = get_all_pixelfed_posts(start_date, end_date)
    
    logging.debug(f"Access Token: {INSTAGRAM_ACCESS_TOKEN}")
    # Post each entry to Instagram
    for post in pixelfed_posts:
        post_id = post['id']

        # Skip already posted posts
        if post_id in [p['id'] for p in posted_ids]:
            logging.info(f"Post {post_id} already posted, skipping.")
            continue
        
        # Throttle posting to ensure no more than 10 posts per hour
        throttle_posting(posted_ids)

        # Retrieve media URLs for the post (multiple images for a gallery)
        media_urls = [media['url'] for media in post.get('media_attachments', [])]

        caption = post['caption'] if 'caption' in post else ''

        logging.info(f"Posting Pixelfed post {post_id} to Instagram as a gallery.")
        if post_to_instagram(media_urls, caption):
            posted_ids.append({
                'id': post_id,
                'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            })
            save_posted_ids(posted_ids)  # Save the updated list of posted IDs
            logging.info(f"Post {post_id} successfully posted and logged.")
