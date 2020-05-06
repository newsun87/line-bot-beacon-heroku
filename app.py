# -*- coding: UTF-8 -*-

from flask import Flask, request, abort

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (MessageEvent, TextMessage, TextSendMessage, BeaconEvent)

import json
import requests
from flask import render_template
import datetime as dt
import time
import pytz
import smtplib
from email.mime.multipart import MIMEMultipart #email內容載體
from email.mime.text import MIMEText #用於製作文字內文
from email.mime.base import MIMEBase #用於承載附檔
from email import encoders #用於附檔編碼
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

#取得通行憑證
cred = credentials.Certificate("/home/newsun87/linebot_firebase/serviceAccount.json")
firebase_admin.initialize_app(cred, {
    'databaseURL' : 'https://line-bot-test-77a80.firebaseio.com/'
})

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
    json_str = ''
    ref = db.reference('/') # 參考路徑
    users_ref = ref.child('linebot_beacon/').get()
    print("Hi")
    for userId in users_ref:
      users_userId_ref = ref.child('linebot_beacon/'+ userId)		   
      if users_userId_ref.get()['state'] == '1':
       json_str = json_str + json.dumps(users_userId_ref.get()) +'\n'
       print(json_str)  
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
    ref = db.reference('/') # 參考路徑   	    
    if text == 'help':
       replymsg = "這是一個報到系統，利用手機的藍牙可以偵測你的身份。使用前必須先到 line://app/1653785431-m94O4qR9 註冊"
    elif text == 'query':
        users_userId_ref = ref.child('linebot_beacon/'+ userId)
        if users_userId_ref.get()== None: # 新用戶            
            replymsg = "你尚未註冊喔!"	
        elif users_userId_ref.get()['state'] == '0': 
            name = users_userId_ref.get()['name']            
            replymsg = "用戶" + name + " 尚未報到!"
        elif users_userId_ref.get()['state'] == '1': 
            name = users_userId_ref.get()['name']                        
            replymsg = "用戶" + name + " 已經報到!"    
            	
		
		   
    elif text == 'export':
        with open('userid_name.json', mode = 'r', encoding = "utf-8") as f:
         load_dict = json.load(f) #讀取json檔案資料變成字典
        fileobject = open('export.txt', mode = 'w', encoding = "utf-8")
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        fileobject.write("匯入時間： " + nowtime +"\n")
        for key in load_dict:
          fileobject.write(key+"  ")	
          fileobject.write(load_dict[key][0]+"  ")	
          fileobject.write(load_dict[key][1]+"  ")
          fileobject.write(load_dict[key][2]+"\n")
        fileobject.close()        
        ret = mail()
        if ret:        
          replymsg = "資料已寄指定信箱...."
        else: 
          replymsg = "資料寄送失敗...."        
    elif text.startswith('register'):      
      command = text.split("~", 1)[0]
      name = text.split("~", 1)[1]		  
      print(command)
      if (command == 'register'):          
          users_ref = ref.child('linebot_beacon/'+ userId)
          print(users_ref.get())
          username = name
          state = '0'
          datetime = ''
          user_data = {"name":username, "state":state, "datetime":datetime}
          users_ref = ref.child('linebot_beacon/'+ userId)
          if users_ref.get()== None: # 新用戶            
            users_ref.set(user_data) # 增加資料
            print("儲存完畢", user_data)
            replymsg = "用戶" + name + " 新增註冊資料成功"
          else:
            users_ref.set(user_data) # 增加資料
            print("資料修改完畢", user_data)
            replymsg = "用戶" + name + " 修改資料成功"			  
          				   
    elif text == 'clear':
      if userId == "Ubf2b9f4188d45848fb4697d41c962591":		
       users_ref = ref.child('linebot_beacon/').get()
       for userid in users_ref:
         ref.child('linebot_beacon/' + userid).update({
		    'state': '0',
			'datetime':''
		   })
       replymsg = " 資料清除成功....." 
      else:
        replymsg = "無管理權限...."                            
   
    else:
      replymsg = "指令不接受...."                                      
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=replymsg)) # reply the same message from user
        
@handler.add(BeaconEvent) 
def handle_beacon_event(event): #處理 beacon偵測事件
    ref = db.reference('/') # 參考路徑   	 
    userId =  event.source.user_id 
    users_ref = ref.child('linebot_beacon/'+ userId)
    if event.beacon.hwid == HWId:		
      if users_ref.get() == None:
       msg = "Hi, 我是報到系統，要先去註冊才可以報到喔..." 
       print("你是誰?....")
       newmsg = msg + "\n 請連線 line://app/1653785431-m94O4qR9 去註冊" 
       line_bot_api.reply_message(event.reply_token,
               TextSendMessage(text=newmsg))   
      else:					
         tw = pytz.timezone('Asia/Taipei')#設定台灣時區        
         nowdatetime = dt.datetime.now() #現在時間
         nowtime = tw.localize(nowdatetime)#台灣時區的現在時間
         nowtime = nowtime.strftime('%Y-%m-%d  %H:%M:%S')#輸出指定時間格式                 
         print("userid...", userId)
         name = users_ref.get()["name"]
         checkState = users_ref.get()["state"]
         print('checkState', checkState)
         
         if checkState == "0": # 修改報到狀態
           users_ref.update({
		 	   "state":"1",
		 	   "datetime":nowtime
		   })           
           newmsg = "我是報到系統，恭喜 " + name +' 於 ' + nowtime + " 報到成功! HWId = " + HWId            
           notifymsg = users_ref.get()["name"] + ' 報到於 ' + nowtime 
           lineNotifyMessage(line_token, notifymsg)
           line_bot_api.reply_message(event.reply_token,\
               TextSendMessage(text = newmsg))
         elif checkState == "1": # 不修改報到資料
           prv_time = users_ref.get()["datetime"]	
           notifymsg = users_ref.get()["name"] + ' 於 ' + prv_time + ' 已經報到過'
           lineNotifyMessage(line_token, notifymsg)	      
                		             
def lineNotifyMessage(line_token, msg):
      headers = {
          "Authorization": "Bearer " + line_token, 
          "Content-Type" : "application/x-www-form-urlencoded"
      }
      payload = {'message': msg}
      r = requests.post("https://notify-api.line.me/api/notify", headers = headers, params = payload)
      return r.status_code
      
def mail(): 
    ret=True
    # Account infomation load
    account = json.load(open('Account.json', 'r', encoding='utf-8'))
    gmailUser = account['Account']
    gmailPasswd = account['password']    

    from_address = 'newsun87@mail.sju.edu.tw' #送件者位址
    to_address = 'newsun87@mail.sju.edu.tw'#收件者位址
    try:  
      mail = MIMEMultipart()
      mail.attach(MIMEText('報到資料清單'))
      attachments = ['export.txt']
      for file in attachments:
          with open(file, 'rb') as fp:
            add_file = MIMEBase('application', "octet-stream")
            add_file.set_payload(fp.read())
          encoders.encode_base64(add_file)
          add_file.add_header('Content-Disposition', 'attachment', filename=file)
          mail.attach(add_file)         
      mail['From']= gmailUser #括號里的對應發件人郵箱暱稱、發件人郵箱帳號 
      mail['To']= gmailUser #括號里的對應收件人郵箱暱稱、收件人郵箱帳號
      mail['Subject']="報到資料清單" #郵件的主題，也可以說是標題            
      smtp = smtplib.SMTP('smtp.gmail.com', 587) #發件人郵箱中的SMTP伺服器      
      smtp.starttls() 
      smtp.ehlo()            
      smtp.login(from_address, "S26202963") #括號中對應的是發件人郵箱帳號、郵箱密碼
      smtp.sendmail(from_address, to_address, mail.as_string()) #括號中對應的是發件人郵箱帳號、收件人郵箱帳號、發送郵件      
      smtp.quit #這句是關閉連接的意思 
    except Exception: #如果try中的語句沒有執行，則會執行下面的ret=False
      ret=False
    return ret
    
if __name__ == "__main__":   
	app.run(debug=True, host='0.0.0.0', port=5000)            

