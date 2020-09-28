# -*- coding: UTF-8 -*-

from line_notify import LineNotify
import os, time

line_url_token = '3igcvnwqH2eV54CZN6N67CpYZDBgiUNW34qjCK07tPL'
notify = LineNotify(line_url_token)

os.system("ps aux | grep ngrok | awk '{print $2}' | xargs kill -9")
os.system("sudo su -pi sh 'sh ngrok_url.sh' ")
f = open("URL5000.txt")
ngrok_url = f.read()
print('url..', ngrok_url)     
notify.send('line_beacon_bot 伺服器網址 ' + ngrok_url)

