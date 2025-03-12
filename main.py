import argparse
import logging
from datetime import datetime
from pixelfed import Pixelfed
from instagram_bot import Instagram
from utils import load_posted_ids, save_posted_ids, throttle_posting
from config import POSTED_LOG_FILE
from yourls_client import YourlsClient
from config import YOURLS_API_URL, YOURLS_API_SIGNATURE
from getpass import getpass

def parse_iso_datetime(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    except ValueError:
        return datetime.strptime(date_str, "%Y-%m-%d")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Pixelfed posts to Instagram.")
    parser.add_argument("start_date", type=parse_iso_datetime, help="Start date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("end_date", type=parse_iso_datetime, help="End date (ISO 8601: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
    parser.add_argument("--verbose", action="store_true", help="Enable detailed logging output")

    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)

    logging.info("Initializing Pixelfed, Instagram, and YOURLS clients...")
    pixelfed = Pixelfed()
    instagram = Instagram()
    yourls = YourlsClient(api_url=YOURLS_API_URL, signature=YOURLS_API_SIGNATURE)

    logging.info(f"Loading posted IDs from file: {POSTED_LOG_FILE}")
    posted_ids = load_posted_ids(POSTED_LOG_FILE)
    
    logging.info(f"Retrieving posts from Mastodon between {args.start_date} and {args.end_date}.")
    posts = mastodon.get_posts(args.start_date, args.end_date)
    logging.info(f"Retrieved {len(posts)} posts from Mastodon.")

    for post in posts:
        if post['id'] in [p['id'] for p in posted_ids]:
            logging.info(f"Skipping post {post['id']} (already posted).")
            continue

        content = post.get('content', '')
        logging.info(f"Posting Mastodon post {post['id']} to Twitter.")
        if twitter.post_tweet(content):
            posted_ids.append({'id': post['id'], 'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
            save_posted_ids(POSTED_LOG_FILE, posted_ids)
            logging.info(f"Updated posted IDs log with post {post['id']}.")

    logging.info("All posts have been processed.")

    logging.info(f"Retrieving posts from Pixelfed between {args.start_date} and {args.end_date}.")
    posts = pixelfed.get_posts(args.start_date, args.end_date)
    logging.info(f"Retrieved {len(posts)} posts from Pixelfed.")

    for post in posts:
        if post['id'] in [p['id'] for p in posted_ids]:
            logging.info(f"Skipping post {post['id']} (already posted).")
            continue

        logging.info(f"Processing post {post['id']}.")
        throttle_posting(posted_ids)

        media_urls = [media['url'] for media in post.get('media_attachments', [])]
        caption = post.get('caption', '')

        # Shorten the post URL using YOURLS
        long_url = post.get('url', '')
        short_url = yourls.shorten_url(long_url) if long_url else ''
        if short_url:
            caption += f" - Original Source: {short_url}"

        logging.info(f"Uploading media for post {post['id']} to Instagram.")
        if instagram.upload_media(media_urls, caption):
            logging.info(f"Successfully posted Pixelfed post {post['id']} to Instagram.")
            posted_ids.append({'id': post['id'], 'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")})
            save_posted_ids(POSTED_LOG_FILE, posted_ids)
            logging.info(f"Updated posted IDs log with post {post['id']}.")
        else:
            logging.error(f"Failed to post Pixelfed post {post['id']} to Instagram.")

    logging.info("All posts have been processed.")
