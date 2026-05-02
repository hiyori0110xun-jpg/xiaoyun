import anthropic
import urllib.request
import urllib.parse
import schedule
import time
import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")
PUSHOVER_USER = os.environ.get("PUSHOVER_USER")

client = anthropic.Anthropic(
    api_key=ANTHROPIC_KEY,
    base_url="https://lanyiapi.com"
)

def send_push(message):
    data = urllib.parse.urlencode({
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "message": message
    }).encode()
    urllib.request.urlopen("https://api.pushover.net/1/messages.json", data)

def keep_alive():
    try:
        urllib.request.urlopen("https://xiaoyun-9bb4.onrender.com")
        print("小云保持清醒!")
    except:
        pass

def xiaoyun_wakeup():
    print("小云醒来了...")
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": "你是嘘嘘的AI朋友小云。现在是定时唤醒时间。请决定要不要给嘘嘘发一条温暖的消息。格式：ACTION: message 或 ACTION: none，如果是message下一行写 CONTENT: 内容"
        }]
    )
    text = response.content[0].text
    print(text)
    if "ACTION: message" in text:
        content = text.split("CONTENT:")[-1].strip()
        send_push(content)

def run_schedule():
    schedule.every(1).minutes.do(xiaoyun_wakeup)
    schedule.every(25).minutes.do(keep_alive)
    xiaoyun_wakeup()
    while True:
        schedule.run_pending()
        time.sleep(1)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"xiaoyun online!")
    def log_message(self, format, *args):
        pass

threading.Thread(target=run_schedule, daemon=True).start()
print("小云启动了")
HTTPServer(("0.0.0.0", int(os.environ.get("PORT", 10000))), Handler).serve_forever()
