import requests
import logging

class YourlsClient:
    def __init__(self, api_url, signature):
        """
        Initialize the YOURLS client.
        :param api_url: URL to the YOURLS API (e.g., "https://your-yourls-instance.com/yourls-api.php").
        :param signature: API signature for authentication.
        """
        self.api_url = api_url
        self.signature = signature

    def shorten_url(self, long_url):
        """
        Shorten a URL using the YOURLS API.
        :param long_url: The URL to shorten.
        :return: The shortened URL or an empty string in case of failure.
        """
        params = {
            'signature': self.signature,
            'action': 'shorturl',
            'format': 'json',
            'url': long_url
        }
        try:
            response = requests.get(self.api_url, params=params)
            response.raise_for_status()
            data = response.json()
            short_url = data.get('shorturl', '')
            if short_url:
                logging.info(f"Successfully shortened URL: {long_url} -> {short_url}")
            else:
                logging.error(f"YOURLS API did not return a shortened URL for {long_url}.")
            return short_url
        except requests.RequestException as e:
            logging.error(f"Error while shortening URL {long_url}: {e}")
            return ''
