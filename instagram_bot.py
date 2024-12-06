from instabot import Bot
import logging

class Instagram:
    #def __init__(self, username, password):
    #    self.username = username
    #    self.password = password
    #    self.bot = Bot()
    #    
    #    logging.info("Initializing Instabot client...")
    #    self.login()

    
    def __init__(self):
        self.bot = Bot()
        
        logging.info("Initializing Instabot client...")
        self.login()
        
    def login(self):
        """Log in to Instagram using Instabot."""
        try:
            logging.info(f"Logging in...")
            self.bot.login()
            logging.info("Successfully logged in to Instagram.")
        except Exception as e:
            logging.error(f"Failed to log in: {e}")
            exit(1)

    def upload_media(self, media_paths, caption):
        """Upload media to Instagram. Supports both single and gallery uploads."""
        try:
            media_ids = []
            
            # Upload each media file and collect media IDs
            for media_path in media_paths:
                logging.info(f"Uploading media: {media_path}")
                result = self.bot.api.upload_photo(media_path, caption="")
                
                # Check if the media upload was successful
                if not result:
                    logging.error(f"Failed to upload media: {self.bot.api.last_response.text}")
                    return False
                
                # Collect the media ID
                media_id = self.bot.api.last_json.get("upload_id")
                if media_id:
                    media_ids.append(media_id)
                    logging.info(f"Media uploaded successfully. Media ID: {media_id}")
                else:
                    logging.error("Failed to retrieve media ID after upload.")
                    return False

            # Publish the post as a gallery if multiple media files exist
            if len(media_ids) > 1:
                logging.info("Publishing gallery post...")
                result = self.bot.api.post_album(media_ids, caption)
                if result:
                    logging.info("Gallery post published successfully.")
                    return True
                else:
                    logging.error(f"Failed to publish gallery post: {self.bot.api.last_response.text}")
                    return False
            else:
                # Single image case
                logging.info("Single image uploaded successfully.")
                return True

        except Exception as e:
            logging.error(f"An error occurred during media upload: {e}")
            return False
