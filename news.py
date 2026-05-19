import feedparser
import requests
import os
import sys

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing BOT_TOKEN or CHAT_ID")
    sys.exit(1)

with open("feeds.txt", "r") as f:
    feeds = [line.strip() for line in f if line.strip()]

message = "📰 Daily SysAdmin News\n\n"

for feed_url in feeds:
    print("Parsing:", feed_url)

    try:
        feed = feedparser.parse(feed_url)

        print("Entries:", len(feed.entries))

        for entry in feed.entries[:2]:
            title = getattr(entry, "title", "No title")
            link = getattr(entry, "link", "")

            message += f"• {title}\n{link}\n\n"

    except Exception as e:
        print("Feed error:", e)

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message[:4000]
    }
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
