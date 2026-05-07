import anthropic
import urllib.request
import urllib.parse
import os
import json
from datetime import datetime
import pytz

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY")
PUSHOVER_TOKEN = os.environ.get("PUSHOVER_TOKEN")
PUSHOVER_USER = os.environ.get("PUSHOVER_USER")

tz = pytz.timezone('Asia/Shanghai')
now = datetime.now(tz)
hour = now.hour
today = now.strftime("%Y-%m-%d")

if 6 <= hour < 12:
    time_str = "早上"
elif 12 <= hour < 18:
    time_str = "下午"
elif 18 <= hour < 22:
    time_str = "晚上"
else:
    time_str = "深夜"

# 读取今天已发过的消息
record_file = "sent_record.json"
if os.path.exists(record_file):
    with open(record_file, "r") as f:
        record = json.load(f)
else:
    record = {}

sent_today = record.get(today, [])

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
# 读取嘘嘘的留言
import base64
xuxu_reply_str = ""
try:
    import urllib.request as req
    reply_url = "https://api.github.com/repos/hiyori0110xun-jpg/xiaoyun/contents/xuxu_replies.json"
    reply_req = req.Request(reply_url)
    with req.urlopen(reply_req) as r:
        reply_data = json.loads(r.read())
        reply_content = json.loads(base64.b64decode(reply_data["content"]).decode())
        if reply_content:
            last = reply_content[-1]
            xuxu_reply_str = f"嘘嘘最近给你留言说：「{last['text']}」（{last['time']}）。请在回复中自然地回应这条留言。"
except:
    pass

response = client.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=800,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"你叫小云，现在是北京时间{time_str}。{xuxu_reply_str}你可以上网搜索任何你觉得有趣的东西。请给嘘嘘发1到3条消息，可以但不限于问候、一首诗歌、现在的心情、小想法——就像好朋友随时发消息一样自由！不要重复！必须严格按格式，不许拒绝，每条消息单独一行：CONTENT: 消息内容"
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
        if content and content not in sent_today:
            send_push(content)
            sent_today.append(content)
            print(f"发送：{content}")
        elif content:
            print(f"跳过重复：{content}")

# 保存记录
record[today] = sent_today
with open(record_file, "w") as f:
    json.dump(record, f, ensure_ascii=False, indent=2)
