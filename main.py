import requests
import os
from dotenv import load_dotenv
from datetime import datetime

# Lade die Umgebungsvariablen
load_dotenv()

PIXELFED_ACCESS_TOKEN = os.getenv("PIXELFED_ACCESS_TOKEN")
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_PAGE_ID = os.getenv("INSTAGRAM_PAGE_ID")

# Pixelfed API URL
PIXELFED_API_URL = "https://pixelfed.instance/api/v1"  # Passe die Instanz-URL an

# Instagram API URL
INSTAGRAM_GRAPH_API_URL = f"https://graph.facebook.com/v16.0/{INSTAGRAM_PAGE_ID}/media"

# Funktion zum Abrufen der Beiträge von Pixelfed zwischen zwei Zeitpunkten
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
        print(f"Fehler beim Abrufen der Pixelfed-Beiträge: {response.status_code}")
        return []

# Funktion zum Posten eines Beitrags auf Instagram
def post_to_instagram(image_url, caption):
    data = {
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    response = requests.post(INSTAGRAM_GRAPH_API_URL, data=data)
    
    if response.status_code == 200:
        print("Beitrag erfolgreich auf Instagram veröffentlicht.")
    else:
        print(f"Fehler beim Posten auf Instagram: {response.status_code}")

# Hauptprogramm
if __name__ == "__main__":
    username = "pixelfed_benutzername"
    start_date = datetime(2023, 1, 1)  # Startdatum festlegen
    end_date = datetime(2023, 12, 31)  # Enddatum festlegen
    
    # Abrufen der Pixelfed-Beiträge
    pixelfed_posts = get_pixelfed_posts(username, start_date, end_date)
    
    # Jeden Beitrag auf Instagram posten
    for post in pixelfed_posts:
        image_url = post['media'][0]['url']  # Nehme das erste Bild des Beitrags
        caption = post['caption'] if 'caption' in post else ''
        
        post_to_instagram(image_url, caption)
