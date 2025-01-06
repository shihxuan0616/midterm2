import os
from flask import Flask, request, abort
from openai import AzureOpenAI

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

app = Flask(__name__)

configuration = Configuration(access_token='oPQLOdn0ozZgTkQElSY+3QzaOqFPfFgEdsSLyKZ+30u3lfs/7J0pIa18ufRViq5LIqITLWJ//gCucf2PGPUGJ7h/V1L3oMTL2qkZLVeM0MpsHUNbp8PG9XUb5hWpZltv0iN3Ngs0ZJoA6G5wg2HFAgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1b9b87610bc4cf93dde0bd7920994639')

client = AzureOpenAI(
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"), 
  api_key=os.getenv("AZURE_OPENAI_API_KEY"),
  api_version="2024-02-01"
)

@app.route("/", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a travel assistant."},
                    {"role": "user", "content": event.message.text},
                ] 
            )
        except Exception as e:
            app.logger.error(f"Error while calling Azure OpenAI: {e}")
        try:
            line_bot_api.reply_message_with_http_info(
                ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text=response.choices[0].message.content)]
                )
            )
        except Exception as e:
            app.logger.error(f"Error while sent line message: {e}")

if __name__ == "__main__":
    app.run()