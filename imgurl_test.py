# -*- coding: UTF-8 -*-

import io
from PIL import Image
import requests
import json
import base64

url = "http://www.tallheights.com/wp-content/uploads/2016/06/background_purple.jpg"
r = requests.get(url)
image = Image.open(io.BytesIO(r.content))
imagestring = str(image)
client_id = '841a7400f5fa1b8'
url = 'https://api.imgur.com/3/upload'
body = {'type':'file','image': imagestring , 'name' : 'abc.jpeg'}
headers = {'Authorization': 'Client-ID' + client_id}

req = requests.post(url, data=body, headers=headers)
print (req.content)
