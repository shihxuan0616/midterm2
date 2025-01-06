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

# 從環境變數讀取 OpenWeatherMap API 金鑰
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

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
    # 使用 OpenWeatherMap API 來獲取天氣資訊
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&lang=zh_tw&units=metric"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        city_name = data['name']
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        humidity = data['main']['humidity']
        
        weather_info = (f"{city_name}的天氣資訊：\n"
                        f"氣溫: {temperature}°C\n"
                        f"天氣: {weather_description}\n"
                        f"濕度: {humidity}%")
    else:
        weather_info = "抱歉，無法獲取該城市的天氣資訊，請確認城市名稱正確。"

    return weather_info

if __name__ == "__main__":
    app.run(port=5000)
