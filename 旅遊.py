from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage  # 確保導入這些類別
import requests

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


    if user_message == "交通":
        reply_text = "你可以查看交通資訊在這裡: https://tdx.transportdata.tw/data-service/tourism"
    else:
        city = user_message
        attractions = get_attractions(city)
        reply_text = attractions

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def get_attractions(city):
    # 假設這裡有一個函數來獲取城市的景點，可以用 API 或資料庫
    # 這裡簡單回傳一些假資料
    attractions_dict = {
        '台北': '台北101, 故宮博物院, 士林夜市',
        '東京': '淺草寺, 東京塔, 秋葉原',
        '紐約': '自由女神像, 中央公園, 大都會藝術博物館'
    }
    return attractions_dict.get(city, '抱歉，我不知道這個城市的景點。')

if __name__ == "__main__":
    app.run(port=5000)
