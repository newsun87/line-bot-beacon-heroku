# -*- coding: UTF-8 -*-

from flask import Flask, request, abort, redirect, url_for

from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (
    InvalidSignatureError
)
#from linebot.models import (TemplateSendMessage, MessageEvent, TextMessage, TextSendMessage, BeaconEvent)
from linebot.models import *
import requests
import base64
import json
import requests
from flask import render_template
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
from line_notify import LineNotify
import os
from datetime import datetime as dt
import pytz

line_url_token = '3igcvnwqH2eV54CZN6N67CpYZDBgiUNW34qjCK07tPL'
notify = LineNotify(line_url_token)
tz = pytz.timezone('Asia/Taipei')

#取得通行憑證
cred = credentials.Certificate("serviceAccount.json")
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
host = "https://liff.line.me/1654118646-4wKMqGBe"
db_ref_path = "line-beacon-bot/";

def get_access_token(autho_code):
     url = 'https://notify-bot.line.me/oauth/token'	
     payload = {'grant_type': 'authorization_code',
                 'code': autho_code, 
	             'redirect_uri':host+'/register', 
	             'client_id':'yTsl033wU15hKy05FQkxRH',
	             'client_secret': 'ikUE7fD7JrDxVpny5Ca40FKtvKh8l3uW4PbFFHbg7FF'}
     headers = {'content-type': 'application/x-www-form-urlencoded'} 
     try:     
       r = requests.post(url, data=payload, headers=headers) # 回應為 JSON 字串
       print('r.text...',r.text) 
     except exceptions.Timeout as e:
        print('请求超时：'+str(e.message))
     except exceptions.HTTPError as e:
        print('http请求错误:'+str(e.message))
     else:       
        if r.status_code == 200:
          #print('r.text...',r.text)			
          json_obj = json.loads(r.text) # 轉成 json 物件
          access_token = json_obj['access_token']
          print('access_token:', json_obj['access_token'])
          #print('ID_token:', json_obj['id_token'])
          return access_token            
        else:
           return 'error'

@app.route('/') 
def showPage():    
   return render_template('index.html')
   #return redirect(url_for('index'))
    
@app.route('/register', methods=['GET', 'POST']) 
def showRegister():    
    ref = db.reference('/') # 參考路徑    
    if request.method=='GET':
      userId = request.args.get('state')  
      if userId != None:
        #profile = line_bot_api.get_profile(userId)# 呼叫取得用戶資訊 API 
        #userId = profile.user_id # 取得用戶 userId   
        autho_code = request.args.get('code') #取得 LineNotify 驗證碼
        time.sleep(1)
        linenotify_access_token = get_access_token(autho_code) #取得存取碼
        print('linenotify_access_token...', linenotify_access_token)               
        users_userId_ref = ref.child('line-beacon-bot/'+ userId)        
        users_userId_ref.update({'LineNotify':'{access_token}'.format(access_token=linenotify_access_token)})
      return render_template('register.html')  
    if request.method=='POST':
       if request.form.get('username')!=None: 
         userId = request.form.get('userId') #取得用戶名稱
         username = request.form.get('username')
         print('username...', username)
         now = dt.now(tz) # 現在的時間(台北時區)
         nowtime = now.strftime("%Y-%m-%d %H:%M:%S")        
         users_userId_ref = ref.child('line-beacon-bot/'+ userId)
         users_userId_ref.update({'name':'{username}'.format(username=username)})
         users_userId_ref.update({'state':'0'})
         users_userId_ref.update({'datetime':''})
         data = '用戶名字已註冊成功....'
       elif request.form.get('checkin')!=None: 
         userId = request.form.get('userId') #取得用戶名稱
         username = request.form.get('username')
         print('username...', username)                       
         users_userId_ref = ref.child('line-beacon-bot/'+ userId)
         print('name...', users_userId_ref.get()['name']) 
         if users_userId_ref.get()['name']!='':          
           users_userId_ref.update({'state':'0'})
           users_userId_ref.update({'datetime':''})
           data = '重新報到設定成功....' 
         else:
           data ='你尚未註冊，無法設定...'                    
       elif request.form.get('withdraw')!=None: #取得用戶名稱         
         userId = request.form.get('userId') #取得用戶名稱
         users_userId_ref = ref.child('line-beacon-bot/'+ userId)         
         users_userId_ref.set({}) #刪除用戶資料 
         data = '用戶資料已刪除....'      
       return render_template('register.html', data=data)     

@app.route('/manage', methods=['GET', 'POST']) 
def manage(): 
  return render_template('manage.html')	 
  
@app.route('/query')
def showQuery():  
   return render_template('query.html')  
  
@app.route('/help')
def showHelpPage():
  return render_template('help.html')

@app.route('/question')
def showQuestionPage():
  return render_template('question.html') 
  
@app.route('/goal')
def showGoalPage():
  return render_template('goal.html') 
  
@app.route('/export')
def showExport():  
  global db_ref_path 	
  ref = db.reference('/') # 參考路徑
  users_ref_list = ref.child(db_ref_path).get()           
  fileobject = open('export.txt', mode = 'w', encoding = "utf-8")
  nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
  fileobject.write("匯入時間： " + nowtime +"\n")
  for userId in users_ref_list:
    users_userId_ref = ref.child(db_ref_path + userId)        		   
    if users_userId_ref.get()['state'] == '1':			  
     fileobject.write(users_userId_ref.get()['name']+"   ")	
     fileobject.write(users_userId_ref.get()['datetime']+"\n")          
  fileobject.close()        
  ret = mail()
  if ret:        
    data = "資料已寄出至指定信箱...."	
    print('data...',data)
  else: 
   data = "資料寄送失敗...."
   print('data...',data) 
  return render_template('manage.html', data=data)                

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
    
@handler.add(MessageEvent, message=ImageMessage)
def handle_image_message(event):  
    if event.message.type == 'image':
      message_id = event.message.id
      print("event: ", event)	  
	  # 讀取圖片資料
      message_content = line_bot_api.get_message_content(message_id)    
      with open('temp_image.jpg', 'wb') as fd:
         for chunk in message_content.iter_content():
            fd.write(chunk)			  
      userId = event.source.user_id
      ref = db.reference('/') # 參考路徑	
      users_userId_ref = ref.child(db_ref_path + userId)	  	  
      imgurl = imgur_upload('temp_image.jpg')
      users_userId_ref.update({
		'picurl': imgurl })	
      message = TextSendMessage(text='相片更新成功')
      checkState = users_userId_ref.get()["state"]
      if checkState == '1':
        picurl = users_userId_ref.get()['picurl']
        datetime = users_userId_ref.get()["datetime"]
        user_linenotify_token =	users_userId_ref.get()["LineNotify"]             	    
      line_bot_api.reply_message(event.reply_token, message)
      	      	      	
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):    
    userId = event.source.user_id    
    text = event.message.text # message from user 
    ref = db.reference('/') # 參考路徑   
    if text == 'query':
        users_userId_ref = ref.child(db_ref_path + userId)
        if users_userId_ref.get()== None or users_userId_ref.child("name").get()=='': # 新用戶
            profile = line_bot_api.get_profile(userId)# 取得用戶公開資料資訊 API
            print('profile...',profile)            
            picurl = profile.picture_url 
            line_name = profile.display_name               
            replymsg = "你尚未註冊喔!"            
        elif users_userId_ref.get()['state'] == '0': 
            name = users_userId_ref.get()['name']
            picurl = users_userId_ref.get()['picurl']            
            replymsg = "用戶" + name + " 尚未報到!"
        elif users_userId_ref.get()['state'] == '1': 
            name = users_userId_ref.get()['name']
            picurl = users_userId_ref.get()['picurl'] 
            datetime = users_userId_ref.get()['datetime']                         
            replymsg = "用戶 " + name + " 已經報到! \n報到時間：" + datetime 
        buttons_template_message = TemplateSendMessage(
         alt_text = '我是一個按鈕模板',  # 當你發送到你的Line bot 群組的時候，通知的名稱
         template = ButtonsTemplate(
            thumbnail_image_url = picurl, 
            text = replymsg,  # 你要問的問題，或是文字敘述            
            actions = [ # action 最多只能4個喔！
                URIAction(
                    label = "修改設定", # 在按鈕模板上顯示的名稱
                    uri = host # 點擊後，顯示文字
                )
            ]
         )
        )
        line_bot_api.reply_message(event.reply_token, buttons_template_message)    		
		   
    if text == 'help':
       replymsg = help_menu()# 這是一個報到系統，利用手機的藍牙可以偵測你的身份。
       #使用前必須先到 line://app/1653785431-m94O4qR9 註冊")	
    elif text == 'export':
        ref = db.reference('/') # 參考路徑
        users_ref_list = ref.child(db_ref_path).get()          
        fileobject = open('export.txt', mode = 'w', encoding = "utf-8")
        nowtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        fileobject.write("匯入時間： " + nowtime +"\n")
        for userId in users_ref_list:
          users_userId_ref = ref.child(db_ref_path + userId)		   
          if users_userId_ref.get()['state'] == '1':			  
            fileobject.write(users_userId_ref.get()['name']+"   ")	
            fileobject.write(users_userId_ref.get()['datetime']+"\n")          
        fileobject.close()        
        ret = mail()
        if ret:        
          replymsg =  TextSendMessage(text= "資料已寄指定信箱....")	
        else: 
          replymsg = TextSendMessage(text= "資料寄送失敗....")    
          				   
    elif text == 'clear':
      if userId == "Ubf2b9f4188d45848fb4697d41c962591":	
       #users_userId_ref = ref.child(db_ref_path + userId)	  	
       users_ref_list = ref.child(db_ref_path).get()
       for userid in users_ref_list:
         ref.child(db_ref_path +userid).update({
		    'state': '0',
			'datetime':''
		 })
       replymsg = TextSendMessage(text=" 資料全部清除成功....." )
      else:
        replymsg = TextSendMessage(text=" 無管理權限....") 
        
    elif text == 'exit':      
       users_userId_ref = ref.child(db_ref_path + userId)	
       if users_userId_ref.get() == None:
          replymsg = TextSendMessage(text=" 查無此資料....." ) 
       else:
           users_userId_ref.set({})
           replymsg = TextSendMessage(text=" 註冊資料已移除...." )	      
                                         
    line_bot_api.reply_message(event.reply_token,replymsg ) # reply the same message from user
        
@handler.add(BeaconEvent) 
def handle_beacon_event(event): #處理 beacon偵測事件
    ref = db.reference('/') # 參考路徑   	 
    userId =  event.source.user_id 
    users_userId_ref = ref.child(db_ref_path + userId)
    if event.beacon.hwid == HWId:		
      if users_userId_ref.get() == None or ref.child(db_ref_path + userId +'/name').get()=='': # 新用戶或未註冊:
       if ref.child(db_ref_path + userId +'/picurl').get()=='':
          picurl = 'https://i.imgur.com/6c9QOyC.png' 
       else:
          picurl = users_userId_ref.get()['picurl']	  
			  
       replymsg = "Hi, 我是報到系統，我有偵測到你，但我不知道你是誰? \n要記得先去註冊才算報到成功喔!" 
       print("你是誰?....")  
       buttons_template_message = TemplateSendMessage(
             alt_text = '我是一個按鈕模板',  # 當你發送到你的Line bot 群組的時候，通知的名稱
             template = ButtonsTemplate(
              thumbnail_image_url = picurl, 
              text = replymsg,  # 你要問的問題，或是文字敘述            
              actions = [ # action 最多只能4個喔！
                URIAction(
                    label = "註冊", # 在按鈕模板上顯示的名稱
                    uri = host# 點擊後，顯示文字！
                )
              ]
             )
           )         
       line_bot_api.reply_message(event.reply_token,buttons_template_message)   
      else:
         tw = pytz.timezone('Asia/Taipei')#設定台灣時區  
         now = dt.now(tw) # 現在的時間(台北時區)
         nowtime = now.strftime("%Y-%m-%d %H:%M:%S")        
         print('nowtime....',nowtime)               
         print("userid...", userId)
         name = users_userId_ref.get()["name"]  
         picurl = users_userId_ref.get()["picurl"]       
         checkState = users_userId_ref.get()["state"]
         print('checkState', checkState)         
         if checkState == "0": # 修改報到狀態
           users_userId_ref.update({
		 	   "state":"1",
		 	   "datetime":nowtime
		   })
           datetime = users_userId_ref.get()["datetime"]  
           replymsg = "用戶" + name + " 已經報到! \n報到時間：" + datetime 
           buttons_template_message = TemplateSendMessage(
             alt_text = '我是一個按鈕模板',  # 當你發送到你的Line bot 群組的時候，通知的名稱
             template = ButtonsTemplate(
              thumbnail_image_url = picurl, 
              text = replymsg,  # 你要問的問題，或是文字敘述            
              actions = [ # action 最多只能4個喔！
                URIAction(
                    label = "修改設定", # 在按鈕模板上顯示的名稱
                    uri = "line://app/1653785431-m94O4qR9" # 點擊後，顯示文字！
                )
              ]
             )
           )         
           #newmsg = "我是報到系統，恭喜 " + name +' 於 ' + nowtime + " 報到成功! HWId = " + HWId            
           notifymsg = users_userId_ref.get()["name"] + ' 報到於 ' + nowtime +'\n' + picurl
           user_linenotify_token =	users_userId_ref.get()["LineNotify"]
           lineNotifyMessage(line_token, notifymsg)
           lineNotifyMessage(user_linenotify_token, notifymsg)
           line_bot_api.reply_message(event.reply_token, buttons_template_message)            
                		             

def imgur_upload(image):
   client_id = '25f4ae85bbaac00'
   client_secret = 'bb4c2d5ec7e6a441ea22917c8c5aa3c7b0de6c23'

   headers = {
    'Authorization': 'Client-ID ' + client_id}
   params = {'image': base64.b64encode(open(image, 'rb').read())}
   r = requests.post('https://api.imgur.com/3/image', \
     headers=headers, data=params)
   print('status:', r.status_code)
   data = r.json() # 轉成 json 格式
   #print(data)
   print(data['data']['link'])
   return data['data']['link']

def help_menu():
    buttons_template_message = TemplateSendMessage(
         alt_text = '我是報到系統使用說明按鈕選單模板',
         template = ButtonsTemplate(
            thumbnail_image_url = 'https://i.imgur.com/QNStdTw.png', 
            title = '功能使用說明選單',  # 你的標題名稱
            text = '請選擇：',  # 你要問的問題，或是文字敘述            
            actions = [ # action 最多只能4個喔！
                URIAction(
                    label = '如何報到', # 在按鈕模板上顯示的名稱
                    uri = host + '/help'  # 跳轉到的url，看你要改什麼都行，只要是url                    
                ),
                URIAction(
                    label = '疑難排解', # 在按鈕模板上顯示的名稱
                    uri = host + '/question' # 跳轉到的url，看你要改什麼都行，只要是url                    
                ),
                URIAction(
                    label = '註冊連結', # 在按鈕模板上顯示的名稱
                    uri = host  # 跳轉到的url，看你要改什麼都行，只要是url                    
                )
            ]
         )
        )
    return buttons_template_message 
def lineNotifyMessage(line_token, msg):
      headers = {
          "Authorization": "Bearer " + line_token, 
          "Content-Type" : "application/x-www-form-urlencoded"
      }
      payload = {'message': msg}      
      r = requests.post("https://notify-api.line.me/api/notify", \
          headers = headers, params = payload)
      return r.status_code
      
def getNgrokURL(): 
    os.system("ps aux | grep ngrok | awk '{print $2}' | xargs kill -9")
    os.system('sh ngrok_url.sh')
    f = open("URL5000.txt")
    ngrok_url = f.read()
    print('url..', ngrok_url)     
    notify.send('伺服器網址 ' + ngrok_url)      

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
      print('pass1....')
      for file in attachments:
          with open(file, 'rb') as fp:
            add_file = MIMEBase('application', "octet-stream")
            add_file.set_payload(fp.read())
          encoders.encode_base64(add_file)
          add_file.add_header('Content-Disposition', 'attachment', filename=file)
          mail.attach(add_file)  
      print('pass2....')       
      mail['From']= gmailUser #括號里的對應發件人郵箱暱稱、發件人郵箱帳號 
      mail['To']= gmailUser #括號裏的對應收件人郵箱暱稱、收件人郵箱帳號
      mail['Subject']="報到資料清單" #郵件的主題，也可以說是標題            
      smtp = smtplib.SMTP('smtp.gmail.com', 587) #發件人郵箱中的SMTP伺服器        
      smtp.starttls() 
      smtp.ehlo()            
      smtp.login(from_address, gmailPasswd) #括號中對應的是發件人郵箱帳號、郵箱密碼
      smtp.sendmail(from_address, to_address, mail.as_string()) #括號中對應的是發件人郵箱帳號、收件人郵箱帳號、發送郵件      
      smtp.quit #這句是關閉連接的意思 
    except Exception: #如果try中的語句沒有執行，則會執行下面的ret=False
      ret=False
    return ret
    
if __name__ == "__main__": 
	#getNgrokURL()  
	app.run(debug=True, host='0.0.0.0', port=5000)            

