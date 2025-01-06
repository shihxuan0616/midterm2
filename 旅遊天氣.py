from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage

app = Flask(__name__)

# 設定你的 Channel Access Token 和 Channel Secret
LINE_CHANNEL_ACCESS_TOKEN = 'YD570GyXga2k3k1pb+fGOvh2SrWF0znyUaFuyFmMbNtcwh3EGMGIhOGFUkZ/PHHYo7eyqt3LQgNGm14YHJNkOncswAcnsiCU1/0XWwLcjjO9GjqbNEPgW7Et/geQUXOu+GgmYxkEP6JK/FRWPkuhpwdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = 'f7bef1fe3683d84b1050f118dd1ac016'

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

    if user_message == "交通":
        reply_text = "你可以查看交通資訊在這裡: https://tdx.transportdata.tw/data-service/tourism"
    elif user_message == "天氣":
        reply_text = "請輸入城市名稱來查詢天氣資訊。"
    else:
        attractions = get_attractions(user_message)
        weather_info = get_weather(user_message)

        if attractions != "抱歉，我不知道這個城市的景點。" or weather_info != "抱歉，目前無法提供該城市的天氣資訊。":
            reply_text = f"{weather_info}\n\n推薦景點:\n{attractions}"
        else:
            reply_text = "抱歉，我無法辨識您的需求，請再試一次。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def get_attractions(city):
    attractions_dict = {
        '台北': '台北101, 故宮博物院, 士林夜市',
        '東京': '淺草寺, 東京塔, 秋葉原',
        '紐約': '自由女神像, 中央公園, 大都會藝術博物館'
    }
    return attractions_dict.get(city, '抱歉，我不知道這個城市的景點。')

def get_weather(city):
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
