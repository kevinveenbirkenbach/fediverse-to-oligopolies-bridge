import os
from dotenv import load_dotenv

load_dotenv()

PIXELFED_ACCESS_TOKEN = os.getenv("PIXELFED_ACCESS_TOKEN")
PIXELFED_INSTANCE = os.getenv("PIXELFED_INSTANCE")
PIXELFED_USERNAME = os.getenv("PIXELFED_USERNAME")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_PAGE_ID = os.getenv("INSTAGRAM_PAGE_ID")

PIXELFED_API_URL = f"https://{PIXELFED_INSTANCE}/api/v1"
INSTAGRAM_GRAPH_API_URL = f"https://graph.facebook.com/v21.0/{INSTAGRAM_PAGE_ID}/media"
POSTED_LOG_FILE = "posted.logs.json"
