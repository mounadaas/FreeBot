import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timezone

# 🔹 قراءة متغيرات البيئة من .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 🔹 لتخزين الروابط المرسلة لتجنب التكرار
sent_links = set()

# 🔹 Headers لتجنب حظر requests
headers = {"User-Agent": "Mozilla/5.0"}

# 🔹 آخر وقت تحقق، timezone-aware UTC
last_checked_time = datetime.now(timezone.utc)

# 🔹 دالة لإرسال رسالة إلى Telegram
def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except Exception as e:
        print("❌ Failed to send message:", e)

# 🔹 تابع مراقبة Mostaql
def check_mostaql():
    url = "https://mostaql.com/projects"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        projects = soup.select("h2 a")
        for p in projects:
            title = p.text.strip().lower()
            link = "https://mostaql.com" + p["href"]
            if link not in sent_links:
                sent_links.add(link)
                send_message(f"🚀 Mostaql Project\n{title}\n{link}")
    except Exception as e:
        print("❌ Error checking Mostaql:", e)

# 🔹 تابع مراقبة Khamsat
def check_khamsat():
    global last_checked_time
    url = "https://khamsat.com/community/requests"
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        projects = soup.select("h3 > a[href^='/community/requests/']")
        times = soup.select("h3 span[dir='ltr']")
        for p, t in zip(projects, times):
            title = p.text.strip().lower()
            link = "https://khamsat.com" + p["href"]
            try:
                project_time = datetime.strptime(t["title"], "%d/%m/%Y %H:%M:%S GMT")
                # نجعل الوقت aware بالـ timezone UTC
                project_time = project_time.replace(tzinfo=timezone.utc)
            except:
                continue
            if project_time > last_checked_time and link not in sent_links:
                sent_links.add(link)
                send_message(f"🚀 Khamsat Project\n{title}\n{link}")
        # تحديث آخر وقت تحقق
        last_checked_time = datetime.now(timezone.utc)
    except Exception as e:
        print("❌ Error checking Khamsat:", e)

# 🔹 رسالة بداية تشغيل البوت
send_message("✅ Bot started successfully!")

# 🔹 الحلقة الرئيسية للبوت
while True:
    try:
        print("🔄 Checking for new projects...")
        check_mostaql()
        check_khamsat()
    except Exception as e:
        print("❌ Unexpected error:", e)
    time.sleep(20)