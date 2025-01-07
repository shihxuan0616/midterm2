from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage, MessageEvent, TextMessage
import requests
import json

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

    # 如果訊息是「天氣」，則查詢天氣
    if user_message.startswith("天氣"):
        city = user_message.replace("天氣", "").strip()
        if city:
            weather_info = get_weather(city)
            reply_text = weather_info
        else:
            reply_text = "請輸入城市名稱，例如：天氣臺北"
    # 如果訊息是「交通」，則提供交通資訊的連結
    elif user_message == "交通":
        reply_text = "你可以查看交通資訊在這裡: https://tdx.transportdata.tw/data-service/tourism"
    # 如果是其他城市名稱，則查詢景點
    else:
        city = user_message
        attractions = get_attractions(city)
        reply_text = attractions

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

# 查詢天氣資訊
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

# 查詢城市的景點
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
