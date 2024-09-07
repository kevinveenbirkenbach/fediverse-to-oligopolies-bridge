# Federated-to-Central Social Network Bridge

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
- Python 3.x
- OAuth API tokens for all platforms involved.
- Federated social media accounts (Pixelfed, Mastodon, PeerTube, etc.).
- Centralized accounts (Instagram Business/Creator Account, X, YouTube).

## Author

**Kevin Veen-Birkenbach**  
- [cybermaster.space](https://cybermaster.space)  
- [kevin@veen.world](mailto:kevin@veen.world)  


## Related Chat GPT Conversation:
- https://chatgpt.com/c/66dc06ba-4c2c-800f-9283-d77c6f56c3df
- https://chatgpt.com/share/482c2428-82b9-4e33-8591-20859adfde34