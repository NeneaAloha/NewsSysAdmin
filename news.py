import feedparser
import requests
import os
import sys
import html
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN or not CHAT_ID:
    print("❌ Missing BOT_TOKEN or CHAT_ID")
    sys.exit(1)

feeds = [
    "https://dnsc.ro/feed",

    "https://api.msrc.microsoft.com/update-guide/rss",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=CoreInfrastructureandSecurityBlog",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=MicrosoftSentinelBlog",
    "https://techcommunity.microsoft.com/gxcuf89792/rss/board?board.id=WindowsServer",
    "https://azure.microsoft.com/en-us/updates/feed/",

    "https://blogs.vmware.com/security/feed/",
    "https://blogs.vmware.com/vsphere/feed/",

    "https://www.cisa.gov/cybersecurity-advisories/all.xml",
    "https://www.bleepingcomputer.com/feed/",
    "https://thehackernews.com/feeds/posts/default",
    "https://krebsonsecurity.com/feed/",
    "https://isc.sans.edu/rssfeed_full.xml",

    "https://thenewstack.io/feed/",
    "https://www.servethehome.com/feed/"
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
    "horizon"
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
    "network", "virtualization", "proxmox"
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
# HELPERS
# =========================

def contains_any(text, keywords):
    return any(k in text for k in keywords)

def clean_title(title):
    return html.escape(title.strip())

def make_item(title, link):
    return f"• <b>{title}</b>\n{link}"

# =========================
# PARSE FEEDS
# =========================

for url in feeds:

    print(f"📡 Parsing: {url}")

    try:
        feed = feedparser.parse(url)

        if not feed.entries:
            print("⚠️ No entries found")
            continue

        for entry in feed.entries[:6]:

            title = clean_title(
                getattr(entry, "title", "")
            )

            link = getattr(entry, "link", "")

            if not title or not link:
                continue

            # dedup case insensitive
            dedup_key = title.lower()

            if dedup_key in seen:
                continue

            seen.add(dedup_key)

            title_lower = title.lower()

            item = make_item(title, link)

            # =========================
            # PRIORITY ORDER
            # =========================

            if contains_any(title_lower, SECURITY):
                security_news.append(item)

            elif contains_any(title_lower, MICROSOFT):
                microsoft_news.append(item)

            elif contains_any(title_lower, VMWARE):
                vmware_news.append(item)

            elif contains_any(title_lower, INFRA):
                infra_news.append(item)

    except Exception as e:
        print(f"❌ Feed error: {e}")

# =========================
# LIMITS
# =========================

security_news = security_news[:5]
microsoft_news = microsoft_news[:5]
vmware_news = vmware_news[:3]
infra_news = infra_news[:3]

# =========================
# BUILD MESSAGE
# =========================

today = datetime.utcnow().strftime("%Y-%m-%d")

message = ""
message += "🛡️ <b>DAILY SYSADMIN DIGEST</b>\n"
message += f"📅 {today}\n"
message += "━━━━━━━━━━━━━━━━━━\n\n"

# SECURITY
if security_news:
    message += "🚨 <b>SECURITY & CVEs</b>\n\n"
    message += "\n\n".join(security_news)
    message += "\n\n"

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

# INFRA
if infra_news:
    message += "⚙️ <b>INFRA / CLOUD / DEVOPS</b>\n\n"
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
