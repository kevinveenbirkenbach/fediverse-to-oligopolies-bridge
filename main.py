import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import argparse

# Load the environment variables
load_dotenv()

PIXELFED_ACCESS_TOKEN = os.getenv("PIXELFED_ACCESS_TOKEN")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_PAGE_ID = os.getenv("INSTAGRAM_PAGE_ID")

# Pixelfed API URL
PIXELFED_API_URL = "https://pixelfed.instance/api/v1"  # Adjust the instance URL

# Instagram API URL
INSTAGRAM_GRAPH_API_URL = f"https://graph.facebook.com/v16.0/{INSTAGRAM_PAGE_ID}/media"

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
        print(f"Error retrieving Pixelfed posts: {response.status_code}")
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
        print("Successfully posted to Instagram.")
    else:
        print(f"Error posting to Instagram: {response.status_code}")

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

    # Retrieve Pixelfed posts
    pixelfed_posts = get_pixelfed_posts(username, start_date, end_date)
    
    # Post each entry to Instagram
    for post in pixelfed_posts:
        image_url = post['media'][0]['url']  # Take the first image of the post
        caption = post['caption'] if 'caption' in post else ''
        
        post_to_instagram(image_url, caption)
