# Author: JC
# Date: 2018/11/12 18:54
# encoding: utf-8
from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, BeaconEvent
)
access_token = '4vOSpHm6ybXdM4H8juFy82HfM2TSUVE3Ty2FLoT+5kjTzNhQdzz1dUfquvRaMCKuqbt/YYXbPj2Kv3W2MKDkxdtZWJZgcC+gKg2RyphLbPF0uaqybQurPvX9sT+eFFY1Qf8z4KuhvqT3tPdr/pX+/wdB04t89/1O/w1cDnyilFU='
channel_secret = '17af62e5969376a42034ad93f6bf9efe'

app = Flask(__name__)

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)
HWId = "0138532680"

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text  # message from user

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=text))  # reply the same message from user


@handler.add(BeaconEvent)
def handle_beacon_event(event):
    if event.beacon.hwid == HWId:
        msg = 'Line Beacon Detected\n HWId = ' + HWId    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=msg))

if __name__ == "__main__":           
    app.run(debug=True, host='127.0.0.1', port=5000)    
