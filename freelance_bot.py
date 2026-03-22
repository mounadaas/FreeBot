import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timezone, timedelta

# 🔹 قراءة متغيرات البيئة
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔹 تخزين الروابط المرسلة
sent_links = set()

# 🔹 Headers
headers = {"User-Agent": "Mozilla/5.0"}

# 🔹 أول تشغيل: نرجع 5 دقائق للخلف
last_checked_time = datetime.now(timezone.utc) - timedelta(minutes=15)

# 🔹 إرسال رسالة Telegram
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": CHAT_ID, "text": text})
        print(f"📤 Sent message | Status: {res.status_code}")
    except Exception as e:
        print("❌ Failed to send message:", e)

# 🔹 Mostaql
def check_mostaql():
    url = "https://mostaql.com/projects"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        projects = soup.select("h2 a")

        print(f"📌 Mostaql found: {len(projects)}")

        for p in projects:
            title = p.text.strip().lower()
            link = "https://mostaql.com" + p["href"]

            print("🔎 Mostaql project:", title)

            if link not in sent_links:
                sent_links.add(link)
                send_message(f"🚀 Mostaql Project\n{title}\n{link}")

    except Exception as e:
        print("❌ Error checking Mostaql:", e)

# 🔹 Khamsat
def check_khamsat():
    global last_checked_time

    url = "https://khamsat.com/community/requests"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        projects = soup.select("h3 > a[href^='/community/requests/']")
        times = soup.select("h3 span[dir='ltr']")

        print(f"📌 Khamsat found: {len(projects)}")

        for p, t in zip(projects, times):
            title = p.text.strip().lower()
            link = "https://khamsat.com" + p["href"]

            try:
                project_time = datetime.strptime(
                    t["title"], "%d/%m/%Y %H:%M:%S GMT"
                ).replace(tzinfo=timezone.utc)
            except Exception as e:
                print("⚠️ Failed parsing time:", e)
                continue

            print("🕒 Project time:", project_time)
            print("🕒 Last checked:", last_checked_time)

            # 🔥 شرط الإرسال
            if project_time > last_checked_time and link not in sent_links:
                print("✅ Sending Khamsat project:", title)
                sent_links.add(link)
                send_message(f"🚀 Khamsat Project\n{title}\n{link}")
            else:
                print("⏭️ Skipped:", title)

        # 🔹 تحديث الوقت بعد كل دورة
        last_checked_time = datetime.now(timezone.utc)
        print("🔄 Updated last_checked_time:", last_checked_time)

    except Exception as e:
        print("❌ Error checking Khamsat:", e)

# 🔹 رسالة بداية
send_message("✅ Bot started successfully!")

# 🔹 Loop
while True:
    try:
        print("\n==============================")
        print("🔄 Checking for new projects...")
        print("Current time:", datetime.now(timezone.utc))

        check_mostaql()
        check_khamsat()

    except Exception as e:
        print("❌ Unexpected error:", e)

    time.sleep(20)