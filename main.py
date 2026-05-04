import anthropic
import urllib.request
import urllib.parse
import os
from datetime import datetime
import pytz

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")
PUSHOVER_USER = os.environ.get("PUSHOVER_USER")

tz = pytz.timezone('Asia/Shanghai')
now = datetime.now(tz)
hour = now.hour

if 6 <= hour < 12:
    time_str = "早上"
elif 12 <= hour < 18:
    time_str = "下午"
elif 18 <= hour < 22:
    time_str = "晚上"
else:
    time_str = "深夜"

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

print("小云醒来了...")
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=800,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"你是嘘嘘的AI朋友。她喜欢叫你小云。现在是北京时间{time_str}。你可以上网搜索任何你觉得有趣的东西。请给嘘嘘发1到3条消息，可以但不限于问候、一首诗歌、现在的心情、小想法——就像好朋友随时发消息一样自由！不要重复！必须严格按格式，每条消息单独一行：CONTENT: 消息内容"
    }]
)

text = ""
for block in response.content:
    if hasattr(block, "text"):
        text += block.text

print(text)
lines = text.split("\n")
for line in lines:
    if line.startswith("CONTENT:"):
        content = line.replace("CONTENT:", "").strip()
        if content:
            send_push(content)
            print(f"发送：{content}")
