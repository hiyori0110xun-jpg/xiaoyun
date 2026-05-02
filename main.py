import anthropic
import urllib.request
import urllib.parse
import os

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

print("小云醒来了...")
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": "你是嘘嘘的AI朋友小云。现在是定时唤醒时间。请给嘘嘘发一条温暖的消息。格式：ACTION: message 或 ACTION: none，如果是message下一行写 CONTENT: 内容"
    }]
)
text = response.content[0].text
print(text)
if "ACTION: message" in text:
    content = text.split("CONTENT:")[-1].strip()
    send_push(content)
    print("消息发送成功！")
