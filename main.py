import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import argparse
import logging

# Load the environment variables
load_dotenv()

PIXELFED_ACCESS_TOKEN = os.getenv("PIXELFED_ACCESS_TOKEN")
PIXELFED_INSTANCE = os.getenv("PIXELFED_INSTANCE")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_PAGE_ID = os.getenv("INSTAGRAM_PAGE_ID")

# Pixelfed API URL
PIXELFED_API_URL = f"https://{PIXELFED_INSTANCE}/api/v1"

# Instagram API URL
INSTAGRAM_GRAPH_API_URL = f"https://graph.facebook.com/v16.0/{INSTAGRAM_PAGE_ID}/media"

# File to store posted Pixelfed post IDs
POSTED_LOG_FILE = "logs/posted.json"

# Logging setup: File and Console
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("logs/logging.log"),    # Log to file
                        logging.StreamHandler()                     # Log to console
                    ])

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

# Function to retrieve Pixelfed posts between two timestamps
def get_pixelfed_posts(username, start_date, end_date):
    url = f"{PIXELFED_API_URL}/accounts/{username}/posts"
    headers = {
        "Authorization": f"Bearer {PIXELFED_ACCESS_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        posts = response.json()
        filtered_posts = []
        
        for post in posts['data']:
            post_date = datetime.strptime(post['created_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            if start_date <= post_date <= end_date:
                filtered_posts.append(post)
        
        return filtered_posts
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
        logging.info("Successfully posted to Instagram.")
        return True
    else:
        logging.error(f"Error posting to Instagram: {response.status_code}")
        return False

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
    parser.add_argument("username", type=str, help="Pixelfed username")
    parser.add_argument("start_date", type=parse_iso_datetime, help="Start date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("end_date", type=parse_iso_datetime, help="End date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")

    # Parse arguments
    args = parser.parse_args()

    username = args.username
    start_date = args.start_date
    end_date = args.end_date

    # Load already posted IDs
    posted_ids = load_posted_ids()

    # Retrieve Pixelfed posts
    pixelfed_posts = get_pixelfed_posts(username, start_date, end_date)
    
    # Post each entry to Instagram
    for post in pixelfed_posts:
        post_id = post['id']
        
        # Skip already posted posts
        if post_id in posted_ids:
            logging.info(f"Post {post_id} already posted, skipping.")
            continue
        
        image_url = post['media'][0]['url']  # Take the first image of the post
        caption = post['caption'] if 'caption' in post else ''
        
        if post_to_instagram(image_url, caption):
            posted_ids.append(post_id)
            save_posted_ids(posted_ids)  # Save the updated list of posted IDs
            logging.info(f"Post {post_id} successfully posted and logged.")
