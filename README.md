# AutoNewsDigest

**AutoNewsDigest** is a personal project I developed during the summer break of my first year in Software Engineering to improve my skills. It automatically tracks selected Telegram channels, summarizes news on your topics of interest using OpenAI GPT, and sends it to your email. This project demonstrates Python automation, web scraping, natural language processing, and API integration.

## Features

- Monitors multiple Telegram channels in real-time.
- Filters messages based on predefined topics of interest.
- Extracts full articles using Newspaper3k and Playwright for JS-rendered pages.
- Summarizes news according to publication standards with OpenAI GPT.
- Sends summarized content via email automatically.
- Logs events and handles errors with Python’s logging module.

## Technologies Used

- **Python 3.11+**
- **Telethon** (Telegram API client)
- **Newspaper3k & Playwright** (web scraping)
- **OpenAI API** (GPT-based summarization)
- **SMTP** (email delivery)
- **Langdetect** (language detection)

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Replace placeholder values with your own:
   - `API_ID` and `API_HASH` for Telegram
   - `MY_CHAT_ID` for your account
   - `OPENAI_CLIENT API Key`
   - Email sender address, password, and recipients
     
3. Run the bot.
    ```
   python main.py
   ```
