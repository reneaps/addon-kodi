#####################################################################
# -*- coding: utf-8 -*-
import requests

url = 'https://002.yandexcloud.ga/public/dist/index.html?id=8a7ea36a56b234c2a0bd0736412e9caecls'

r = requests.get(url)

data = r.text
print(data)