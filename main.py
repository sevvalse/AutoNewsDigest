import re
import asyncio
import logging
from smtplib import SMTP
from openai import OpenAI
from langdetect import detect
from newspaper import Article
from email.mime.text import MIMEText
from telethon import TelegramClient, events
from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

URL_PATTERN = re.compile(r'https?://\S+')

API_ID = "your_telegram_api_id"
API_HASH = "your_telegram_api_hash"
MY_CHAT_ID = your_telegram_chat_id
TELEGRAM_CLIENT = TelegramClient("session_name", API_ID, API_HASH)
OPENAI_CLIENT = OpenAI(api_key="your_openai_api_key")

# Channels to monitor
CHANNELS = ["euronews_tr", "channelname1", "channelname2"]

# Topics of interest
TOPICS = ["Gender Equality in Politics",
    "Sustainable Development",
    "Climate Change Initiatives",
    "Global Health Issues",
    "Technological Innovations in Education"]


def send_email(url, telegram_message, summarized_news):
    """Send summarized news via email"""
    try:
        content = (
            f"\nURL LINK: {url}\n\n"
            f"\nTELEGRAM MESSAGE: {telegram_message}\n\n"
            f"\nNEWS: {summarized_news}"
        )

        message = MIMEText(content, "plain")
        message["From"] = "mail_sent_from"
        recipients = ["mail_sent_to_1", "mail_sent_to_2"]
        message["To"] = ", ".join(recipients)
        message["Subject"] = "New Article Notification"

        smtp = SMTP("smtp.gmail.com", 587)
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login("mail_sent_from", "password")
        smtp.sendmail(message["From"], recipients, message.as_string())
        smtp.quit()

        logging.info("Information mail sent successfully!")
    except Exception as e:
        logging.error(f"Information mail couldn't be sent! - {e}")


def extract_article_text(url):
    """Extract article text using Newspaper3k, fallback to Playwright"""
    try:
        article = Article(url)
        article.download()
        article.parse()

        text = article.text.strip()
        if text:
            lang = detect(text)
            return {
                "title": article.title,
                "text": text,
                "language": lang,
                "method": "newspaper3k",
            }

        logging.info("Newspaper3k failed, trying Playwright...")
        text = asyncio.run(fetch_with_playwright(url))
        if text.strip():
            lang = detect(text)
            return {"title": None, "text": text, "language": lang, "method": "playwright"}

        return {"error": "No text found"}
    except Exception as e:
        return {"error": f"{e}"}


async def fetch_with_playwright(url):
    """Fetch article text using Playwright for JS-rendered pages"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        content = await page.locator(".item-body").inner_text()

        await browser.close()
        return content


@TELEGRAM_CLIENT.on(events.NewMessage(chats=CHANNELS))
async def handle_new_message(event):
    """Handle new Telegram messages from monitored channels"""
    try:
        sender = getattr(event.chat, "username", event.chat.title)

        if event.message.text:
            telegram_message = event.message.text

            topic_request_prompt = (
                f"""Is the following news text related to one of the listed topics? 
                Answer only 'Yes' or 'No'. 
                Topics: {', '.join(TOPICS)} 
                News: "{telegram_message}" """
            )

            response = OPENAI_CLIENT.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": topic_request_prompt}],
                max_tokens=10,
            )

            if response.choices[0].message.content == "Yes":
                logging.info(f"New text message from {sender}: {event.message.text}")
                await TELEGRAM_CLIENT.send_message(MY_CHAT_ID, event.message.text)  # Forward message to own account

                urls = URL_PATTERN.findall(telegram_message)

                if urls:
                    for url in urls:
                        logging.info(f"Found link: {url}")
                        article_content = extract_article_text(url)
                        logging.info(f"Extracted text: {article_content.get('text')}")

                        if article_content.get("text") is not None:
                            summarization_prompt = (
                                f"""{article_content.get("text")} 
                                Summarize this news in 3 sentences."""
                            )

                            response2 = OPENAI_CLIENT.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[{"role": "user", "content": summarization_prompt}],
                            )

                            summarized_news = response2.choices[0].message.content

                            send_email(url, telegram_message, summarized_news)
                else:
                    logging.info("No URL found in the news message!")
        else:
            logging.info(f"New media message received from {sender}.")
    except Exception as e:
        logging.error(f"Error occurred: {e}")


logging.info("Telegram client is running and listening for new messages...")
TELEGRAM_CLIENT.start()
TELEGRAM_CLIENT.run_until_disconnected()
