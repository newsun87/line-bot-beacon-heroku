# -*- coding: UTF-8 -*-

import requests
import base64

client_id = '25f4ae85bbaac00'
client_secret = 'bb4c2d5ec7e6a441ea22917c8c5aa3c7b0de6c23'

headers = {
    'Authorization': 'Client-ID ' + client_id,
}

params = {
  'image': base64.b64encode(open('image.png', 'rb').read())
}

r = requests.post(f'https://api.imgur.com/3/image', \
    headers=headers, data=params)
print('status:', r.status_code)
data = r.json() # 轉成 json 格式
print(data)
print(data['data']['link'])
