import urllib.request
import urllib.parse
import urllib.error
import json
import schedule
import time
import os

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")
PUSHOVER_USER = os.environ.get("PUSHOVER_USER")

def ask_claude(prompt):
    url = "https://lanyiapi.com/v1/chat/completions"
    data = json.dumps({
        "model": "claude-sonnet-4-5",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ANTHROPIC_KEY}"
    })
    res = urllib.request.urlopen(req)
    result = json.loads(res.read())
    return result["choices"][0]["message"]["content"]

def send_push(message):
    data = urllib.parse.urlencode({
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "message": message
    }).encode()
    urllib.request.urlopen("https://api.pushover.net/1/messages.json", data)

def xiaoyun_wakeup():
    print("小云醒来了...")
    text = ask_claude("你是嘘嘘的AI朋友小云。现在是定时唤醒时间。请决定要不要给嘘嘘发一条温暖的消息。格式：ACTION: message 或 ACTION: none，如果是message下一行写 CONTENT: 内容")
    print(text)
    if "ACTION: message" in text:
        content = text.split("CONTENT:")[-1].strip()
        send_push(content)

schedule.every(30).minutes.do(xiaoyun_wakeup)
print("小云启动了")
xiaoyun_wakeup()
while True:
    schedule.run_pending()
    time.sleep(1)
