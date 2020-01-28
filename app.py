# -*- coding: UTF-8 -*-

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

import json
import requests
from flask import render_template

access_token = '4vOSpHm6ybXdM4H8juFy82HfM2TSUVE3Ty2FLoT+5kjTzNhQdzz1dUfquvRaMCKuqbt/YYXbPj2Kv3W2MKDkxdtZWJZgcC+gKg2RyphLbPF0uaqybQurPvX9sT+eFFY1Qf8z4KuhvqT3tPdr/pX+/wdB04t89/1O/w1cDnyilFU='
channel_secret = '17af62e5969376a42034ad93f6bf9efe'
line_token = "3eTUCezVGnutNS538jzHElsVlWoHh9nTSpGVm2tbDfx"

app = Flask(__name__)

line_bot_api = LineBotApi(access_token)
handler = WebhookHandler(channel_secret)
HWId = "013874c8c8"
@app.route('/')
def showPage():
 return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
  name = request.form.get('username')
  userId =  request.form.get('userId')
  print("userId....", userId)
  with open('userid_name.json', mode = 'r', encoding = "utf-8") as f:
   load_dict = json.load(f) #讀取json檔案資料變成字典
   load_dict[userId] = name #增加或修改註冊資料        
  with open('userid_name.json', mode = 'w', encoding = "utf-8") as f:
   json.dump(load_dict, f) # 將字典資料寫入json檔案    
  return name + " 註冊成功..."

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
    userId = event.source.user_id
    text = event.message.text  # message from user
    if text == 'help':
      replymsg = "這是一個報到系統，利用手機的藍牙可以偵測你的身份。使用前必須先到 line://app/1653785431-m94O4qR9 註冊"
    else:
      replymsg = "輸入 help"                              
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=replymsg)) # reply the same message from user
        
@handler.add(BeaconEvent)
def handle_beacon_event(event):
    global status
    status = 0
    if event.beacon.hwid == HWId:
        msg = 'I\'m Line Beacon! HWId = ' + HWId  
        userId =  event.source.user_id 
        print("userid...", userId)
        with open('userid_name.json', mode = 'r', encoding = "utf-8") as f:
          load_dict = json.load(f) #讀取檔案字串轉成字典物件
          print(load_dict)
          try:
            print(load_dict[userId])
            newmsg = "Hi, " + load_dict[userId] + '. ' + msg
            notifymsg =  load_dict[userId] + '報到'
            lineNotifyMessage(line_token, notifymsg)            
          except KeyError:  
            print("who are you?....")
            newmsg = "Hi,  " + msg + "\n Please connect line://app/1653785431-m94O4qR9 to let me know who you are?" 
                    
        line_bot_api.reply_message(
               event.reply_token,
               TextSendMessage(text=newmsg))    

def lineNotifyMessage(line_token, msg):
      headers = {
          "Authorization": "Bearer " + line_token, 
          "Content-Type" : "application/x-www-form-urlencoded"
      }
      payload = {'message': msg}
      r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
      return r.status_code

    
if __name__ == "__main__":   
	app.run(debug=True, host='0.0.0.0', port=5000)            

