import requests

# Zugriffstoken und Instagram-Benutzer-ID (ersetzen)
ACCESS_TOKEN = "dein_access_token"
INSTAGRAM_USER_ID = "deine_instagram_user_id"

# Foto-URL und Beschreibung
PHOTO_URL = "https://example.com/path-to-your-photo.jpg"
CAPTION = "Mein neuestes Abenteuer! 🌍✨ #Abenteuer #Reisen"

def post_photo():
    # Schritt 1: Erstelle einen Container
    url_create_container = f"https://graph.facebook.com/v17.0/{INSTAGRAM_USER_ID}/media"
    payload = {
        "image_url": PHOTO_URL,
        "caption": CAPTION,
        "access_token": ACCESS_TOKEN
    }
    response = requests.post(url_create_container, data=payload)
    response_data = response.json()

    if "id" not in response_data:
        print("Fehler beim Erstellen des Containers:", response_data)
        return

    container_id = response_data["id"]
    print("Container erstellt:", container_id)

    # Schritt 2: Veröffentliche den Container
    url_publish = f"https://graph.facebook.com/v17.0/{INSTAGRAM_USER_ID}/media_publish"
    payload_publish = {
        "creation_id": container_id,
        "access_token": ACCESS_TOKEN
    }
    response_publish = requests.post(url_publish, data=payload_publish)
    response_publish_data = response_publish.json()

    if "id" in response_publish_data:
        print("Foto erfolgreich gepostet! Medien-ID:", response_publish_data["id"])
    else:
        print("Fehler beim Veröffentlichen:", response_publish_data)

if __name__ == "__main__":
    post_photo()
