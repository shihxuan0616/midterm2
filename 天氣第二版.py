from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage
import requests
import json

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

    if user_message.startswith("天氣"):
        city = user_message.replace("天氣", "").strip()
        if city:
            weather_info = get_weather(city)
            reply_text = weather_info
        else:
            reply_text = "請輸入城市名稱，例如：天氣臺北"
    else:
        reply_text = "抱歉，我只支援天氣查詢功能。請輸入例如：天氣臺北"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def get_weather(city):
    try:
        token = 'CWA-2230B583-3E8E-47E9-9D7F-1617AA73C3D3'
        url = f'https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization={token}'
        response = requests.get(url)
        response.raise_for_status()  # 檢查 HTTP 狀態碼
        data = response.json()

        # 印出 API 回應以供除錯
        print(f"API 回應: {json.dumps(data, ensure_ascii=False, indent=2)}")

        # 迭代所有的 Station 資料
        for station in data['records']['Station']:
            station_name = station['StationName']

            # 進行更靈活的比對
            if city in station_name or station_name.startswith(city):  
                weather_element = station['WeatherElement']
                weather_description = weather_element['Weather']
                temperature = weather_element['AirTemperature']
                humidity = weather_element['RelativeHumidity']
                wind_speed = weather_element['WindSpeed']
                pressure = weather_element['AirPressure']

                return (
                    f"{city}的天氣資訊：\n"
                    f"天氣狀況: {weather_description}\n"
                    f"氣溫: {temperature}°C\n"
                    f"相對濕度: {humidity}%\n"
                    f"風速: {wind_speed} 公尺/秒\n"
                    f"氣壓: {pressure} hPa"
                )
        return "抱歉，找不到該城市的天氣資訊。"
    except requests.exceptions.RequestException as e:
        print(f"HTTP 請求錯誤: {e}")
        return "抱歉，無法連接到天氣服務，請稍後再試。"
    except Exception as e:
        print(f"程式錯誤: {e}")
        return "抱歉，無法取得天氣資訊，請稍後再試。"

if __name__ == "__main__":
    app.run(port=5000)
