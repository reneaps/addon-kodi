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

'''
# Player_Filmes
#url = 'https://filmestorrentbrasil.com.br/um-amor-apos-a-vida-2021-torrent-web-dl-1080p-dual-audio/'
url = 'https://filmestorrentbrasil.com.br/tempo-2021-torrent-camrip-720p-legendado/'
link = openURL(url)
soup = BeautifulSoup(link, "html.parser")
conteudo = soup('div', attrs={'class':'right'})
links = conteudo[0]('p')
for link in links:
    if 'campanha' in str(link) :
        u = link.a['href']
        #print(urlF)
        fxID = u.split('id=')[-1]
        urlF = base64.b64decode(fxID).decode('utf-8')
        print(urlF)
    if 'tulo Traduzido:' in str(link):
        titF = link.strong.text
        print(titF)
        
'''
#Lista Episodios
url = 'https://filmestorrentbrasil.com.br/krypton-2a-temporada-2019-torrent-web-dl-720p-1080p-dual-audio/'
html = openURL(url)
soup = BeautifulSoup(html, "html.parser")
#conteudo = soup('div', attrs={'class':'content'})
links = soup('p')
'''
for link in links:
    fxID = urlF.split('?id=')[-1]
    urlF = base64.b64decode(fxID).decode('utf-8')
    print(titF)
    print(imgF)
    print(urlF)
'''
for link in links:
        if 'tulo Traduzido:' in str(link):
            titF = link.strong.text
        elif 'tulo Original:' in str(link):
            titF = link.strong.text            
        elif 'emporada' in str(link):
            if 'strong' in str(link):
                titF = link.strong.text
            if 'img' in str(link):
                titF = link.img['alt']
        elif 'Epis' in str(link):
            titF = link.strong.text
        if 'campanha' in str(link):
            u = link.a['href']
            fxID = u.split('?id=')[-1]
            urlF = base64.b64decode(fxID).decode('utf-8')
            print(titF,'\n', urlF)

