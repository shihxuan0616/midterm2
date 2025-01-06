from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage

app = Flask(__name__)

# 設定你的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'gM+wvmUdEhYU86zYXT5IPYxPj8r2rdzVkONURtTnofWRFi2hf/2hQOJiA59hFWhBr+Ds6J98URrFeRsc1tAL6jqJuPAPA+00Z5haeS1BHVOl5gxzeUI68i5rVgK0Nx8cvIwSQY3V7ZsVXDlMhxETcwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '7a5d3946285a4a0cce1312e6b1853bb0'

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
    # 模擬天氣資料
    mock_weather_data = {
        "台北": {
            "description": "多雲時晴",
            "temp_min": 20,
            "temp_max": 28,
            "rain_probability": 20
        },
        "高雄": {
            "description": "晴天",
            "temp_min": 22,
            "temp_max": 30,
            "rain_probability": 10
        },
        "台中": {
            "description": "短暫陣雨",
            "temp_min": 18,
            "temp_max": 25,
            "rain_probability": 40
        }
    }

    weather = mock_weather_data.get(city)
    if weather:
        weather_info = (
            f"{city}的天氣資訊：\n"
            f"天氣狀況: {weather['description']}\n"
            f"氣溫範圍: {weather['temp_min']}°C - {weather['temp_max']}°C\n"
            f"降雨機率: {weather['rain_probability']}%"
        )
    else:
        weather_info = "抱歉，目前無法提供該城市的天氣資訊。"

    return weather_info

if __name__ == "__main__":
    app.run(port=5000)
