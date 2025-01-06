import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage
import requests

app = Flask(__name__)

# 設定你的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'yG7wKul+NpxFU9c0XaXSZiNMplH2JtYH62OhTNT/3yc5v/73oXXT/0gsSbULA3GLV8XNHD+90J/I5KvhSXmiLwrMo9UJIFQjo823gavlSfOchg'
LINE_CHANNEL_SECRET = 'b4e1bfe3bb07c0893e0e5d282f4eefb3'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print(f"收到的訊息: {user_message}")

    if user_message == "天氣":
        reply_text = "請輸入城市名稱來查詢天氣資訊。"
    else:
        # 查詢天氣資訊
        weather_info = get_weather(user_message)
        reply_text = weather_info

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def get_weather(city):
    # 使用中央氣象局開放資料 API 查詢天氣
    base_url = "https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001"
    params = {
        "Authorization": "你的授權碼",  # 需要在中央氣象局網站註冊並獲得授權碼
        "format": "JSON",
        "locationName": city,
    }
    
    response = requests.get(base_url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        try:
            location_data = data['records']['location'][0]
            city_name = location_data['locationName']
            weather_elements = location_data['weatherElement']
            
            # 提取天氣資訊
            weather_description = weather_elements[0]['time'][0]['parameter']['parameterName']
            temperature_min = weather_elements[2]['time'][0]['parameter']['parameterName']
            temperature_max = weather_elements[4]['time'][0]['parameter']['parameterName']
            rain_probability = weather_elements[1]['time'][0]['parameter']['parameterName']
            
            weather_info = (
                f"{city_name}的天氣資訊：\n"
                f"天氣狀況: {weather_description}\n"
                f"氣溫範圍: {temperature_min}°C - {temperature_max}°C\n"
                f"降雨機率: {rain_probability}%"
            )
        except (IndexError, KeyError):
            weather_info = "抱歉，無法獲取該城市的天氣資訊，請確認城市名稱正確。"
    else:
        weather_info = "抱歉，目前無法連線到氣象服務，請稍後再試。"

    return weather_info

if __name__ == "__main__":
    app.run(port=5000)
