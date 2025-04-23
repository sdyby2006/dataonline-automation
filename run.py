import os
import requests
import json
from datetime import datetime, timezone, timedelta

def open_web_pages(urls_info):
    successful_urls = []
    failed_urls = []

    for url_info in urls_info:
        url = url_info['url']
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                successful_urls.append(url)
            else:
                failed_urls.append(url)
                print(f"访问 {url} 失败，状态码: {response.status_code}")
        except Exception as e:
            failed_urls.append(url)
            print(f"访问 {url} 时出错: {str(e)}")
    return successful_urls, failed_urls

# 从环境变量获取 URL_INFO（确保是合法的 JSON 格式）
url_info_str = os.getenv('URL_INFO', '[]')
urls_info = json.loads(url_info_str)  # 修正变量名：ssh_info_str → url_info_str

successful_urls, failed_urls = open_web_pages(urls_info)
success_url_num = len(successful_urls)
failed_url_num = len(failed_urls)
url_num = success_url_num + failed_url_num

content = "网页打开信息：\n"
for url in successful_urls:  # 修正：去掉 zip()，直接遍历列表
    content += f"页面：{url} 打开成功\n"
for url in failed_urls:  # 修正：去掉 zip()，直接遍历列表
    content += f"页面：{url} 打开失败\n"

beijing_timezone = timezone(timedelta(hours=8))
time = datetime.now(beijing_timezone).strftime('%Y-%m-%d %H:%M:%S')

menu = requests.get('https://api.zzzwb.com/v1?get=tg').json()
loginip = requests.get('https://api.ipify.org?format=json').json()['ip']

content += f"\n本次打开网页共：{url_num} 个\n成功：{success_url_num} 个\n失败：{failed_url_num} 个\n打开IP：{loginip}\n时间：{time}"

push = os.getenv('PUSH')

def mail_push(url):
    data = {
        "body": content,
        "email": os.getenv('MAIL')
    }
    response = requests.post(url, json=data)
    try:
        response_data = response.json()  # 直接使用 .json() 方法
        if response_data['code'] == 200:
            print("推送成功")
        else:
            print(f"推送失败，错误代码：{response_data['code']}")
    except json.JSONDecodeError:
        print("连接邮箱服务器失败")

def telegram_push(message):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    payload = {
        'chat_id': os.getenv('TELEGRAM_CHAT_ID'),
        'text': message,
        'parse_mode': 'HTML',
        'reply_markup': json.dumps({
            "inline_keyboard": menu,
            "one_time_keyboard": True
        })
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"发送消息到Telegram失败: {response.text}")

if push == "mail":
    mail_push('https://zzzwb.us.kg/test')
elif push == "telegram":
    telegram_push(content)
else:
    print("推送失败，推送参数设置错误")
