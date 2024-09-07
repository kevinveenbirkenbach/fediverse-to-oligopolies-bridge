# Setup Guide: How to Obtain `PIXELFED_ACCESS_TOKEN`, `INSTAGRAM_ACCESS_TOKEN`, and `INSTAGRAM_PAGE_ID`

In this guide, you'll learn how to set up the necessary environment variables for accessing the Pixelfed and Instagram APIs. We'll cover how to retrieve the access tokens for both services and how to find the Instagram page ID.

## Prerequisites
- You should have accounts on Pixelfed and Instagram.
- For Instagram API access, you need an **Instagram Business Account** or a **Creator Account**.
- You should be familiar with basic command-line operations.

---

## 1. Obtaining `PIXELFED_ACCESS_TOKEN`

To interact with Pixelfed’s API, you will need an access token from your Pixelfed instance.

### Steps:

1. **Log into your Pixelfed instance**: Visit your Pixelfed instance and log into your account.
   
2. **Access Developer Settings**: Go to your **account settings**. Look for a section called **API** or **Developer Settings** (the exact name may vary by instance).

3. **Create a New Application**:
    - Navigate to the API section.
    - Look for an option like **Create a New Application** or **Generate Access Token**.
    - Fill in the required details such as:
      - **Application name**: Name of your application (e.g., `Instagram Sync`).
      - **Redirect URI**: You can often use `http://localhost` for testing purposes.
    
4. **Generate the Token**:
    - After filling out the form, generate the token.
    - Copy the generated token, which will look like a long string of letters and numbers.

5. **Store it in `.env`**:
    - Create a `.env` file in your project directory (if it doesn't already exist) and add:
      ```plaintext
      PIXELFED_ACCESS_TOKEN=your_pixelfed_access_token_here
      ```

---

## 2. Obtaining `INSTAGRAM_ACCESS_TOKEN` and `INSTAGRAM_PAGE_ID`

For Instagram, you need access to the **Instagram Graph API**, which requires an Instagram Business or Creator Account, as well as a connected Facebook Page.

### 2.1 Setting Up Instagram Business/Creator Account

1. **Convert to a Business/Creator Account**:
    - Go to your Instagram profile.
    - Tap the menu icon in the top-right corner and navigate to **Settings**.
    - Under **Account**, choose **Switch to Professional Account**.
    - Select either **Business** or **Creator**, depending on your needs.

2. **Link to a Facebook Page**:
    - Your Instagram account needs to be linked to a Facebook page.
    - In **Settings**, go to **Linked Accounts** and connect your Instagram account to a Facebook page you manage.

---

### 2.2 Obtain the `INSTAGRAM_ACCESS_TOKEN`

To obtain the Instagram access token, you need to set up a Facebook App through the Facebook Developer platform.

#### Steps:

1. **Create a Facebook Developer Account**:
   - Go to the [Facebook for Developers](https://developers.facebook.com/) site and log in with your Facebook account.
   - Click on **My Apps** and then **Create App**.
   - Choose **For Everything Else** and give your app a name.

2. **Set Up Instagram Graph API**:
   - Once your app is created, go to the **Add Products** section in the sidebar.
   - Find **Instagram** and click **Set Up**.

3. **Generate Access Token**:
   - In the **Instagram Basic Display** section, click **Generate Access Token**.
   - You may need to go through the Instagram authorization flow, where you will log into your Instagram account and authorize the app.
   - After the process, an access token will be generated for your Instagram account.

4. **Add to `.env`**:
    - Copy the token and store it in your `.env` file:
      ```plaintext
      INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
      ```

---

### 2.3 Get the `INSTAGRAM_PAGE_ID`

The `INSTAGRAM_PAGE_ID` refers to the Facebook Page ID connected to your Instagram account.

#### Steps:

1. **Get Your Facebook Page ID**:
   - Go to your **Facebook Page**.
   - In the **About** section, scroll down to find the **Page ID**.

2. **Store in `.env`**:
    - Add the page ID to your `.env` file:
      ```plaintext
      INSTAGRAM_PAGE_ID=your_facebook_page_id_here
      ```

---

## 3. Final `.env` Example

Your `.env` file should look like this:

```plaintext
PIXELFED_ACCESS_TOKEN=your_pixelfed_access_token_here
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token_here
INSTAGRAM_PAGE_ID=your_facebook_page_id_here
```

This file will allow your script to use the correct API keys for accessing and posting to Pixelfed and Instagram.

---

## 4. Testing the Access Tokens

You can test your access tokens by making simple API requests using a tool like `curl` or with your Python script. For example, to test the Instagram access token, you could use:

```bash
curl -X GET "https://graph.facebook.com/v16.0/me/accounts?access_token=your_instagram_access_token_here"
```

If successful, you should receive a response with details about your Instagram account.

---

## Conclusion

By following these steps, you now have the required access tokens (`PIXELFED_ACCESS_TOKEN`, `INSTAGRAM_ACCESS_TOKEN`) and the `INSTAGRAM_PAGE_ID` needed for integrating the Pixelfed and Instagram APIs in your project. You can now proceed to sync content between the platforms using your scripts.

---

### Troubleshooting

- Ensure that your Instagram account is properly linked to a Facebook page.
- Double-check your environment variables for any typos or missing values.
- If the access tokens expire, regenerate them by following the steps again.

