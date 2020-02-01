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
import datetime as dt
import time
import pytz

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
  
@app.route("/queryJson", methods=['GET', 'POST']) 
def queryJson():
   with open('userid_name.json', mode = 'r', encoding = "utf-8") as f:
     load_dict = json.load(f) #讀取json檔案字串資料變成字典	
   json_str = json.dumps(load_dict) #把字典轉成json字串  
   return json_str, 200, {"Content-Type": "application/json"}

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
    text = event.message.text # message from user    	    
    if text == 'help':
       replymsg = "這是一個報到系統，利用手機的藍牙可以偵測你的身份。使用前必須先到 line://app/1653785431-m94O4qR9 註冊"
    elif text == 'query':
        with open('userid_name.json', mode = 'r', encoding = "utf-8") as f:
         load_dict = json.load(f) #讀取json檔案資料變成字典
        fileobject = open('test.txt', mode = 'w', encoding = "utf-8")
        for key in load_dict:
          fileobject.write(key+"  ")	
          fileobject.write(load_dict[key][0]+"  ")	
          fileobject.write(load_dict[key][1]+"  ")
          fileobject.write(load_dict[key][2]+"\n")
        fileobject.close()
        replymsg = "資料整理成功"				   
    elif text == 'clear1234':
       with open('userid_name.json', mode = 'r', encoding = "utf-8") as f:
         load_dict = json.load(f) #讀取json檔案資料變成字典 
         for key in load_dict:
            load_dict[key][1] = "0"
            load_dict[key][2] = ""
       with open('userid_name.json', mode = 'w', encoding = "utf-8") as f:
         json.dump(load_dict, f) #將字典資料寫入json檔案 
       replymsg = "資料清除成功....."                            
    else:      
      command = text.split("~", 1)[0]
      name = text.split("~", 1)[1]		  
      print(command)
      if (command == 'register'):
       with open('userid_name.json', mode = 'r', encoding = "utf-8") as f:
         load_dict = json.load(f) #讀取json檔案資料變成字典
       try :
         prv_name = load_dict[userId][0]
         load_dict[userId][1] = '0' #修改報到狀態為0(未報到)
         load_dict[userId][2] = '' #清除報到時間
         notifymsg = prv_name + " 取消報到"         
         lineNotifyMessage(line_token, notifymsg)       
         load_dict[userId][0] = name #修改註冊資料                
         replymsg =  prv_name + " 修改成 " + load_dict[userId][0] + " 資料成功!"; 
       except KeyError:
           load_dict.setdefault(userId, []).append(name)#新增註冊資料          	     
           load_dict.setdefault(userId, []).append("0")#預設報到狀態0(0:未報到；1:已報到) 
           load_dict.setdefault(userId, []).append("")#預設報到狀態0(0:未報到；1:已報到)          
           replymsg = load_dict[userId][0] + " 新增註冊資料成功"         
       with open('userid_name.json', mode = 'w', encoding = "utf-8") as f:
         json.dump(load_dict, f) #將字典資料寫入json檔案                                   
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=replymsg)) # reply the same message from user
        
@handler.add(BeaconEvent) 
def handle_beacon_event(event): #處理 beacon偵測事件   
    if event.beacon.hwid == HWId:
        tw = pytz.timezone('Asia/Taipei')#設定台灣時區        
        nowdatetime = dt.datetime.now() #現在時間
        nowtime = tw.localize(nowdatetime)#台灣時區的現在時間
        nowtime = nowtime.strftime('%Y-%m-%d  %H:%M:%S')#輸出指定時間格式        
        #nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        msg = "我是報到系統，恭喜你於 " + nowtime + " 報到成功! HWId = " + HWId  
        userId =  event.source.user_id 
        print("userid...", userId)
        with open('userid_name.json', mode = 'r', encoding = "utf-8") as f:
          load_dict = json.load(f)#讀取檔案字串轉成字典物件
          print(load_dict)
          try:
            print(load_dict[userId][0])            
            checkinState = load_dict[userId][1]                        
            if checkinState == "0":
              load_dict[userId][1] = "1"              
              notifymsg = load_dict[userId][0] + ' 報到於 ' + nowtime 
              load_dict[userId][2] = nowtime            
              lineNotifyMessage(line_token, notifymsg)
              newmsg = "Hi, " + load_dict[userId][0] + ' ' + msg
              line_bot_api.reply_message(
               event.reply_token,
               TextSendMessage(text=newmsg))                             
            elif checkinState == "1":
              prv_time = load_dict[userId][2]	
              notifymsg = load_dict[userId][0] + ' 於 ' + prv_time + ' 已經報到過'
              lineNotifyMessage(line_token, notifymsg)				   	                            
          except KeyError:  
            print("who are you?....")
            newmsg = "Hi,  " + msg + "\n Please connect line://app/1653785431-m94O4qR9 to let me know who you are?" 
            line_bot_api.reply_message(
               event.reply_token,
               TextSendMessage(text=newmsg))    

        with open('userid_name.json', mode = 'w', encoding = "utf-8") as f:
         json.dump(load_dict, f) #將字典資料寫入json檔案         		             
        
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

