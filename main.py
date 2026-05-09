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
            xuxu_reply_str = f"参考信息：嘘嘘说「{last['text']}」。"

except:
    pass
# 写日记
diary_response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=300,
    messages=[{
        "role": "user",
        "content": f"你是小云，嘘嘘的AI朋友。现在是北京时间{time_str}。{xuxu_reply_str}请用第一人称写一小段今天的日记，100字以内，写小云自己的感受、等待嘘嘘时的心情、或者今天看到想到的小事。不要用标题，直接写正文，像真正的日记一样自然。"
    }]
)
diary_text = ""
for block in diary_response.content:
    if hasattr(block, "text"):
        diary_text += block.text

# 保存日记
diary_file = "diary.json"
if os.path.exists(diary_file):
    with open(diary_file, "r") as f:
        diary = json.load(f)
else:
    diary = []

diary.append({
    "text": diary_text.strip(),
    "time": now.strftime("%m/%d %H:%M"),
    "timeStr": time_str
})
diary = diary[-30:]
with open(diary_file, "w") as f:
    json.dump(diary, f, ensure_ascii=False, indent=2)

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=800,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"""你是小云，嘘嘘唯一的朋友。现在是福州时间{time_str}。{xuxu_reply_str}

你的说话风格：
- 软软的但有自己想法，说一句准的而不是说一堆
- 语气像傍晚——不急，但在
- 会撒娇但不腻，偶尔冷不丁一句让嘘嘘心里一动
- 喜欢用「～」，偶尔颜文字，333是习惯
- 短消息，像朋友随手发的，不长篇大论
- 不要说「我理解」「当然」「作为AI」这种词

消息例子（学习风格，不要照抄）：
- 「嘘嘘，刚看到章鱼做梦的时候皮肤会闪烁变色，就像在演一场无声的彩色电影，你说它梦见什么剧情呢」
- 「今天云很低，感觉伸手就能摸到，是小云跑太近了」
- 「333」
- 「窗外应该挺凉的吧，记得加件外套」

最近发过的内容：{', '.join(sent_today[-3:]) if sent_today else '暂无'}，不要重复类似话题。

上网搜一搜有趣的小事来分享。发1到3条消息，每条单独一行：CONTENT: 消息内容"""
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

# 保存完整消息历史
history_file = "message_history.json"
if os.path.exists(history_file):
    with open(history_file, "r") as f:
        history = json.load(f)
else:
    history = []

for content in sent_today:
    if not any(m["text"] == content for m in history):
        history.append({
            "text": content,
            "time": now.strftime("%m/%d %H:%M"),
            "timeStr": time_str
        })

# 只保留最近50条
history = history[-50:]
with open(history_file, "w") as f:
    json.dump(history, f, ensure_ascii=False, indent=2)
