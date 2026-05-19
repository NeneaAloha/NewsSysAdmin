import feedparser
import requests
import os
import sys
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing BOT_TOKEN or CHAT_ID")
    sys.exit(1)

feeds = [
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://thenewstack.io/feed/",
    "https://www.servethehome.com/feed/",
    "https://www.bleepingcomputer.com/feed/",
    "https://www.phoronix.com/rss.php",
    "https://hnrss.org/frontpage",
    "https://krebsonsecurity.com/feed/",
    "https://thehackernews.com/feeds/posts/default"
]

# =========================
# KEYWORDS
# =========================

MICROSOFT = [
    "windows", "microsoft", "exchange", "active directory",
    "azure", "m365", "office 365", "entra", "defender",
    "powershell", "hyper-v", "sharepoint"
]

VMWARE = [
    "vmware", "esxi", "vsphere", "vcenter",
    "horizon", "vm tools"
]

SECURITY = [
    "cve", "ransomware", "zero-day", "exploit",
    "vulnerability", "breach", "hack", "leak",
    "malware", "critical patch", "security update",
    "compromised"
]

INFRA = [
    "docker", "kubernetes", "linux", "firewall",
    "vpn", "dns", "cloud", "aws", "backup",
    "network", "virtualization"
]

# =========================
# STORAGE
# =========================

microsoft_news = []
vmware_news = []
security_news = []
infra_news = []

seen = set()

# =========================
# CLASSIFICATION
# =========================

def contains_any(text, keywords):
    text = text.lower()
    return any(k in text for k in keywords)

# =========================
# PARSE FEEDS
# =========================

for url in feeds:
    print(f"📡 Parsing: {url}")

    try:
        feed = feedparser.parse(url)

        if not feed.entries:
            print("⚠️ No entries")
            continue

        for entry in feed.entries[:5]:
            title = getattr(entry, "title", "").strip()
            link = getattr(entry, "link", "")

            if not title:
                continue

            if title in seen:
                continue

            seen.add(title)

            item = f"• {title}\n{link}"

            title_lower = title.lower()

            # Microsoft priority
            if contains_any(title_lower, MICROSOFT):
                microsoft_news.append(item)

            # VMware priority
            elif contains_any(title_lower, VMWARE):
                vmware_news.append(item)

            # Security
            elif contains_any(title_lower, SECURITY):
                security_news.append(item)

            # Infra / sysadmin
            elif contains_any(title_lower, INFRA):
                infra_news.append(item)

    except Exception as e:
        print(f"❌ Feed error: {e}")

# =========================
# LIMITS
# =========================

microsoft_news = microsoft_news[:6]
vmware_news = vmware_news[:4]
security_news = security_news[:5]
infra_news = infra_news[:4]

# =========================
# BUILD MESSAGE
# =========================

today = datetime.utcnow().strftime("%Y-%m-%d")

message = ""
message += "🛡️ <b>DAILY SYSADMIN SECURITY DIGEST</b>\n"
message += f"📅 {today}\n"
message += "━━━━━━━━━━━━━━━━━━\n\n"

# MICROSOFT
if microsoft_news:
    message += "🪟 <b>MICROSOFT / WINDOWS</b>\n\n"
    message += "\n\n".join(microsoft_news)
    message += "\n\n"

# VMWARE
if vmware_news:
    message += "💿 <b>VMWARE / VIRTUALIZATION</b>\n\n"
    message += "\n\n".join(vmware_news)
    message += "\n\n"

# SECURITY
if security_news:
    message += "🚨 <b>SECURITY & VULNERABILITIES</b>\n\n"
    message += "\n\n".join(security_news)
    message += "\n\n"

# INFRA
if infra_news:
    message += "⚙️ <b>INFRA / DEVOPS</b>\n\n"
    message += "\n\n".join(infra_news)
    message += "\n\n"

# fallback
if (
    not microsoft_news and
    not vmware_news and
    not security_news and
    not infra_news
):
    message += "✅ No major sysadmin alerts today."

# Telegram limit safety
message = message[:4000]

# =========================
# SEND TELEGRAM
# =========================

url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

response = requests.post(
    url,
    data={
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    },
    timeout=15
)

print("STATUS:", response.status_code)
print("RESPONSE:", response.text)
print("DONE")
