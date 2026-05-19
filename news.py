import feedparser
import requests

BOT_TOKEN = "TOKENUL_TAU"
CHAT_ID = "GROUP_CHAT_ID"

with open("feeds.txt", "r") as f:
    feeds = f.readlines()

message = "📰 Daily SysAdmin News\n\n"

for feed_url in feeds:
    feed = feedparser.parse(feed_url.strip())

    for entry in feed.entries[:2]:
        message += f"• {entry.title}\n{entry.link}\n\n"

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

requests.post(url, data={
    "chat_id": CHAT_ID,
    "text": message
})
