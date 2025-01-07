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
        '臺北': '臺北101, 故宮博物院, 士林夜市',
        '新北': '九份老街, 野柳地質公園, 平溪天燈節',
        '基隆': '基隆廟口夜市, 正濱漁港, 和平島公園',
        '桃園': '大溪老街, 小人國主題樂園, 拉拉山',
        '新竹': '新竹城隍廟, 內灣老街, 六福村主題遊樂園',
        '苗栗': '三義木雕博物館, 龍騰斷橋, 勝興車站',
        '臺中': '逢甲夜市, 高美濕地, 彩虹眷村',
        '彰化': '鹿港老街, 八卦山大佛, 芬園花海',
        '南投': '日月潭, 清境農場, 溪頭自然教育園區',
        '雲林': '北港朝天宮, 古坑綠色隧道, 成龍溼地',
        '嘉義': '阿里山, 奮起湖老街, 檜意森活村',
        '臺南': '赤崁樓, 安平古堡, 花園夜市',
        '高雄': '蓮池潭, 駁二藝術特區, 六合夜市',
        '屏東': '墾丁國家公園, 恆春古城, 四重溪溫泉',
        '宜蘭': '羅東夜市, 蘇澳冷泉, 太平山森林遊樂區',
        '花蓮': '太魯閣國家公園, 七星潭, 花蓮文化創意園區',
        '臺東': '三仙台, 知本溫泉, 鹿野高台',
        '澎湖': '七美雙心石滬, 馬公老街, 澎湖跨海大橋',
        '金門': '翟山坑道, 莒光樓, 金門酒廠',
        '馬祖': '北竿芹壁村, 東引燈塔, 南竿大漢據點'
    }
    return attractions_dict.get(city, '無相關景點資料')

    return attractions_dict.get(city, '抱歉，我不知道這個城市的景點。')

if __name__ == "__main__":
    app.run(port=5000)
