# Federated-to-Central Social Network Bridge
[![GitHub Sponsors](https://img.shields.io/badge/Sponsor-GitHub%20Sponsors-blue?logo=github)](https://github.com/sponsors/kevinveenbirkenbach) [![Patreon](https://img.shields.io/badge/Support-Patreon-orange?logo=patreon)](https://www.patreon.com/c/kevinveenbirkenbach) [![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20Coffee-Funding-yellow?logo=buymeacoffee)](https://buymeacoffee.com/kevinveenbirkenbach) [![PayPal](https://img.shields.io/badge/Donate-PayPal-blue?logo=paypal)](https://s.veen.world/paypaldonate)


This project is a **bridge tool** designed to synchronize and automate the posting of content from **federated social networks** (such as [Pixelfed](https://pixelfed.org/)) to **centralized social platforms** like Instagram, X (formerly Twitter), Facebook, and YouTube.

## Features
- **Pixelfed to Instagram Sync**: Automatically fetches and posts images from your Pixelfed account to your Instagram profile.
- **Planned Integrations**:
  - **Mastodon to X/Facebook**: Synchronize text posts from Mastodon to X and Facebook.
  - **PeerTube to YouTube**: Seamlessly publish videos from PeerTube to YouTube.
  
## How It Works
- The software connects to your **federated social network accounts** via their respective APIs and retrieves the latest posts.
- It then cross-posts the content (e.g., images, videos, text) to your accounts on centralized networks using the appropriate API endpoints (e.g., Instagram Graph API for Instagram).
- Post tracking ensures that content is not duplicated on the destination platforms.

## Usage

1. Clone the repository:
    ```bash
    git clone https://github.com/kevinveenbirkenbach/federated-to-central-social-network-bridge.git
    ```

2. Set up your environment by creating a `.env` file with the required API tokens for Pixelfed, Instagram, etc.

3. Run the script to synchronize posts:
    ```bash
    python main.py [start_date] [end_date]
    ```

## Requirements
### Technical Requirements
- Python 3.x
- OAuth API tokens for all platforms involved.
- Federated social media accounts (Pixelfed, Mastodon, PeerTube, etc.).
- Centralized accounts (Instagram Business/Creator Account, X, YouTube).
### Token Requirements 
- https://developers.facebook.com/apps/1572282100376225/instagram-business/API-Setup/
- Generate long time token curl -X GET "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=<APP_ID>&client_secret=<APP_SECRET>&fb_exchange_token=<SHORT_LIVED_TOKEN>"


## Development
- https://graph.facebook.com/debug_token?input_token={dein_access_token}&access_token={dein_app_access_token}
- curl -X GET "https://graph.facebook.com/debug_token?input_token=<DEIN_TOKEN>&access_token=<APP_ACCESS_TOKEN>"
- https://www.getphyllo.com/post/how-to-use-instagram-api-to-post-photos-on-instagram
- https://developers.facebook.com/tools/debug/accesstoken/
- https://developers.facebook.com/tools/explorer/


## Author

**Kevin Veen-Birkenbach**  
- [cybermaster.space](https://cybermaster.space)  
- [kevin@veen.world](mailto:kevin@veen.world)  


## Related Chat GPT Conversation:
- https://chatgpt.com/c/66dc06ba-4c2c-800f-9283-d77c6f56c3df
- https://chatgpt.com/share/482c2428-82b9-4e33-8591-20859adfde34