import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import time

# 🛠️ SETUP: Paste your free Hugging Face token here
HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://huggingface.co"
HEADERS = {"Authorization": f"Bearer {HF_TOKEN}"}

# Create a 'MotorFan_Archive' folder in your Google Drive if it doesn't exist
folder_path = "archive"
os.makedirs(folder_path, exist_ok=True)

# Create a unique file name for today (e.g., motorfan_2026-06-20.txt)
today = datetime.now().strftime("%Y-%m-%d")
file_path = os.path.join(folder_path, f"motorfan_{today}.txt")

def translate_text(text):
    api_url = f"https://translated.net{text[:500]}&langpair=ja|en"
    try:
        res = requests.get(api_url).json()
        return res['responseData']['translatedText']
    except:
        return text

def scrape_article_text(url):
    try:
        res = requests.get(url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = " ".join([p.text.strip() for p in paragraphs if len(p.text) > 20])
        return text[:2000]
    except:
        return ""

def summarize_text(text):
    payload = {"inputs": text, "parameters": {"max_length": 80, "min_length": 30}}
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload).json()
        return response['summary_text']
    except:
        return "Summary generation busy. Try running again."

# --- MAIN EXECUTION & ARCHIVING ---
feed = feedparser.parse("https://motor-fan.jp")

# Open the text file in 'write' mode to save our output
with open(file_path, "w", encoding="utf-8") as file:
    header = f"=========================================\n🏎️ MOTOR-FAN.JP UPDATES FOR {today}\n=========================================\n\n"
    print(header)
    file.write(header)

    for entry in feed.entries[:3]:
        print("🔄 Fetching and processing next article...")
        jp_title = entry.title
        link = entry.link
        
        en_title = translate_text(jp_title)
        jp_body = scrape_article_text(link)
        en_body = translate_text(jp_body) if jp_body else ""
        ai_summary = summarize_text(en_body) if len(en_body) > 100 else "No summary available."
        
        # Format the article block
        article_block = f"📢 Title: {en_title}\n📝 AI Summary: {ai_summary}\n🔗 Link: {link}\n" + ("-" * 50) + "\n\n"
        
        # Print to screen AND write to your Google Drive file
        print(article_block)
        file.write(article_block)
        time.sleep(1)

print(f"✅ Success! Today's updates saved to Google Drive at: MyDrive/MotorFan_Archive/motorfan_{today}.txt")
