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
INSTAGRAM_GRAPH_API_URL = f"https://graph.facebook.com/v16.0/{INSTAGRAM_PAGE_ID}/media"

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

# Function to retrieve Pixelfed posts between two timestamps
def get_pixelfed_posts(start_date, end_date):
    url = f"{PIXELFED_API_URL}/accounts/{PIXELFED_USERNAME}/posts"
    headers = {
        "Authorization": f"Bearer {PIXELFED_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        logging.debug(f"Retrieved posts from Pixelfed API.")
        posts = response.json()
        filtered_posts = []
        
        for post in posts['data']:
            post_date = datetime.strptime(post['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if start_date <= post_date <= end_date:
                logging.debug(f"Post {post['id']} is within the date range.")
                filtered_posts.append(post)
            else:
                logging.debug(f"Post {post['id']} is outside the date range.")
        
        return filtered_posts
    if response.status_code == 404:
        instance_api_overview = f"{PIXELFED_API_URL}/instance"
        if requests.get(instance_api_overview).status_code == 200:
            logging.info(f"Instance is reachable. URL: {url}")
        else:
            logging.info(f"Instance is NOT reachable. URL: {url}")
        logging.error(f"Post endpoint not found. Possible issues: incorrect endpoint or user not found. URL: {url}")
    elif response.status_code == 401:
        logging.error(f"Unauthorized. Check if your access token is valid and the API permissions are correct.")
    else:
        logging.error(f"Error retrieving Pixelfed posts: {response.status_code}")
    return []

# Function to post an entry to Instagram
def post_to_instagram(image_url, caption):
    data = {
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    response = requests.post(INSTAGRAM_GRAPH_API_URL, data=data)
    
    if response.status_code == 200:
        logging.info(f"Post successfully sent to Instagram.")
        return True
    else:
        logging.error(f"Error posting to Instagram: {response.status_code}")
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
    pixelfed_posts = get_pixelfed_posts(start_date, end_date)
    
    # Post each entry to Instagram
    for post in pixelfed_posts:
        post_id = post['id']
        
        # Skip already posted posts
        if post_id in [p['id'] for p in posted_ids]:
            logging.info(f"Post {post_id} already posted, skipping.")
            continue
        
        # Throttle posting to ensure no more than 10 posts per hour
        throttle_posting(posted_ids)
        
        image_url = post['media'][0]['url']  # Take the first image of the post
        caption = post['caption'] if 'caption' in post else ''
        
        logging.info(f"Posting Pixelfed post {post_id} to Instagram.")
        if post_to_instagram(image_url, caption):
            posted_ids.append({
                'id': post_id,
                'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            })
            save_posted_ids(posted_ids)  # Save the updated list of posted IDs
            logging.info(f"Post {post_id} successfully posted and logged.")
