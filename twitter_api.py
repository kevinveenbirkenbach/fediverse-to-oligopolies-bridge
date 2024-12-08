import tweepy
import logging
from config import TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET

class Twitter:
    def __init__(self):
        auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET)
        auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
        self.api = tweepy.API(auth)

    def post_tweet(self, content):
        try:
            if len(content) > 280:
                content = content[:277] + "..."
            self.api.update_status(content)
            logging.info(f"Tweet posted successfully: {content}")
            return True
        except tweepy.TweepError as e:
            logging.error(f"Failed to post tweet: {e}")
            return False
