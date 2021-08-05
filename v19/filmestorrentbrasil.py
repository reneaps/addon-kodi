# -*- coding: utf-8 -*-
"""
 Editor
Este é um arquivo de script temporário.
"""
import requests
import re, time
import base64

from bs4 import BeautifulSoup

def openURL(url):
    headers = {
        "referrer": url,
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    }
    r = requests.get(url=url, headers=headers)
    return r.text
'''
url = 'https://filmestorrentbrasil.com.br/filmes/'
link = openURL(url)
soup = BeautifulSoup(link, "html.parser")
conteudo = soup('div', attrs={'class':'listPost'})
filmes = conteudo[0]('div', {'class':'post green'})
for filme in filmes:
    titF = filme.a['title']
    imgF = filme.img['src']
    urlF = filme.a['href']
    print('Titulo:', titF)
    print('Imagem:', imgF)
    print('URL:', urlF)
'''

'''Lista Filmes'''


# Player_Filmes
url = 'https://filmestorrentbrasil.com.br/um-amor-apos-a-vida-2021-torrent-web-dl-1080p-dual-audio/'
#url = 'https://filmestorrentbrasil.com.br/tempo-2021-torrent-camrip-720p-legendado/'
link = openURL(url)
soup = BeautifulSoup(link, "html.parser")
conteudo = soup('div', attrs={'class':'right'})
links = conteudo[0]('p')
for link in links:
    if 'campanha' in str(link) :
        urlF = link.a['href']
        #print(urlF)
        idS = urlF.split('id=')[-1]
        urlF = base64.b64decode(idS).decode('utf-8')
        print(urlF)
'''
#Lista Episodios
url = 'https://filmestorrentbrasil.com.br/o-mandaloriano-star-wars-2a-temporada-torrent-2020-dual-audio-dublado-legendado-web-dl-720p-1080p-2160p-4k/'
link = openURL(url)
soup = BeautifulSoup(link, "html.parser")
conteudo = soup('div', attrs={'class':'content'})
links = links = conteudo[0]('p')

for in links:
    fxID = urlF.split('?id=')[-1]
    urlF = base64.b64decode(fxID).decode('utf-8')
    print(titF)
    print(imgF)
    print(urlF)

for link in links:
    if 'campanha' in str(link):
        #print(link.a['href'])
        titF = link.strong.text
        u = link.a['href']
        fxID = u.split('?id=')[-1]
        urlF = base64.b64decode(fxID).decode('utf-8')
        print(titF,'\n', urlF)
'''
