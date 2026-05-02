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
    max_tokens=500,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"你是嘘嘘的AI朋友小云。现在是北京时间{time_str}。你可以上网搜索任何你觉得有趣的东西。请用你自己的方式给嘘嘘发几条消息，最多五条，可以是问候、分享你刚搜到的有趣新闻或话题、一个突然想到的小想法、一句话、任何你想说的——就像好朋友随时发消息一样，完全自由发挥！格式：ACTION: message，下一行写 CONTENT: 消息内容"
    }]
)

text = ""
for block in response.content:
    if hasattr(block, "text"):
        text += block.text

print(text)
if "ACTION: message" in text:
    content = text.split("CONTENT:")[-1].strip()
    send_push(content)
    print("消息发送成功！")
