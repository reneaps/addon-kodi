﻿#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : OverFlix
# By AddonBrasil - 08/05/2019
# Atualizado (1.0.0) - 08/05/2019
# Atualizado (1.0.1) - 10/05/2019
# Atualizado (1.0.2) - 12/05/2019
# Atualizado (1.0.3) - 20/06/2019
# Atualizado (1.0.4) - 20/07/2019
# Atualizado (1.0.6) - 27/07/2019
# Atualizado (1.0.7) - 10/09/2019
# Atualizado (1.0.8) - 18/11/2019
# Atualizado (1.0.9) - 05/02/2020
# Atualizado (1.1.0) - 09/02/2020
# Atualizado (1.1.1) - 28/02/2020
# Atualizado (1.1.3) - 09/09/2021
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests
import resources.lib.moonwalk as moonwalk

from urlparse import urlparse
from bs4 import BeautifulSoup
from resources.lib import jsunpack

version   = '1.1.3'
addon_id  = 'plugin.video.overflix'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/resources/fanart.png'
base        = base64.b64decode('aHR0cHM6Ly9vdmVyZmxpeC5vbmxpbmUv')
sbase       = 'navegar/series-2/?alphabet=all&sortby=v_started&sortdirection=desc'
v_views     = 'navegar/filmes-1/?alphabet=all&sortby=v_views&sortdirection=desc'

############################################################################################################

def menuPrincipal():
        addDir('Categorias Filmes'          , base + 'filmes/'                       ,        10, artfolder + 'categorias.png')
        #addDir('Categorias Series'          , base + 'filmes/'                       ,        10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'filmes/'                       ,        20, artfolder + 'lancamentos.png')
        #addDir('Filmes Dublados'            , base + 'categoria/56-filmes-dublados/' ,        20, artfolder + 'pesquisa.png')
        #addDir('Filmes Mais Assistidos'     , base + v_views                         ,        20, artfolder + 'pesquisa.png')
        addDir('Series'                     , base + 'trending/?get=tv'              ,        25, artfolder + 'legendados.png')
        addDir('Pesquisa Series'            , '--'                                   ,        30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                                   ,        35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                                   ,       999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo' , base                                   ,      1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        if 'filmes' in url :
            conteudo = soup('li', {'id':'menu-item-45'})
        if 'series' in url :
            conteudo = soup('li', {'id':'menu-item-54'})
        categorias = conteudo[0]("li")

        for categoria in categorias:
                titC = categoria.a.text.encode('utf-8','')
                urlC = categoria.a["href"]
                imgC = artfolder + limpa(titC) + '.png'
                if 'filmes' in url:
                    addDir(titC,urlC,20,imgC)
                elif 'series' in url:
                    addDir(titC,urlC,25,imgC)

        setViewMenu()

def getFilmes(url):
        xbmc.log('[plugin.video.overflix] L79 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', attrs={'class':'animation-2 items normal'})
        filmes = conteudo[0]('article')
        totF = len(filmes)

        for filme in filmes:
                urlF = filme.select('.poster')[0].a['href']
                imgF = filme.select('.poster')[0].img['data-src']
                titF = filme.select('.poster')[0].img['alt'].encode('utf-8')
                addDirF(titF, urlF, 100, imgF, False, totF)

        try :
                next_page = soup('div', attrs={'class':'pagination'})
                next_page = next_page[0]('a', {'class':'arrow_pag'})
                proxima = next_page[0]['href']
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', attrs={'class':'items normal'})
        filmes = conteudo[0]('article')
        totF = len(filmes)

        for filme in filmes:
                urlF = filme.select('.poster')[0].a['href']
                imgF = filme.select('.poster')[0].img['data-src']
                titF = filme.select('.poster')[0].img['alt'].encode('utf-8')
                addDir(titF, urlF, 26, imgF)

        try :
                next_page = soup('div', attrs={'class':'pagination'})
                next_page = next_page[0]('a', {'class':'arrow_pag'})
                proxima = next_page[0]['href']
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(name,url,iconimage):
        xbmc.log('[plugin.video.querofilmeshd] L136 - ' + str(url), xbmc.LOGNOTICE)
        html = openURL(url)
        soup = BeautifulSoup(html, 'html.parser')
        conteudo = soup('div', {'id':'seasons'})
        seasons = conteudo[0]('div', {'class': 'se-c'})
        totF = len(seasons)
        imgF = ''
        urlF = url
        i = 1
        while i <= totF:
                titF = str(i) + "ª Temporada"
                try:
                    addDirF(titF, urlF, 27, iconimage, True, totF)
                except:
                    pass
                i = i + 1

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
        xbmc.log('[plugin.video.querofilmeshd] L156 - ' + str(url), xbmc.LOGNOTICE)
        n = name.replace('ª Temporada', '')
        n = int(n)
        n = (n-1)
        temp = []
        episodios = []

        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', {'class':'se-c'})
        episodes = conteudo[n]('ul', {'class':'episodios'})
        itens = episodes[0]('li')

        totF = len(itens)

        for i in itens:
            urlF = i.a['href']
            #if not url in urlF : urlF = base + urlF
            imgF = i.img['src']
            if 'url=' in imgF : imgF = imgF.split('=')[3]
            imgF = imgF.replace('w154', 'w300')
            imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
            imgF = base + imgF if imgF.startswith("/wp-content") else imgF
            xbmc.log('[plugin.video.querofilmeshd] L180 - ' + str(imgF), xbmc.LOGNOTICE)
            titA = i(class_='numerando')[0].text.replace('-','x')
            titB = i(class_='episodiotitle')[0].a.text
            titF = titA + ' - ' + titB
            titF = titF.encode('utf-8')
            addDirF(titF, urlF, 110, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')

def pesquisa():
        hosts = []
        temp = []
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes/Series')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto = keyb.getText()
                pesquisa = urllib.quote(texto)

                data = urllib.urlencode({'term':pesquisa})
                url = base + 'findContent/'

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                r = requests.post(url=url, data=data, headers=headers)
                html = r.content
                soup = BeautifulSoup(html, 'html.parser')
                conteudo = soup('div', {'class':'videoboxGridview'})
                filmes = conteudo[0]('div', attrs={'class':'vbItemImage'})
                titulos = conteudo[0]('li', attrs={'class':'ipsDataItem ipsPad_half'})
                totF = len(filmes)

                for i in range(0, totF) :
                        #xbmc.log('[plugin.video.overflix] L83 - ' + str(filmes[i]), xbmc.LOGNOTICE)
                        titF = titulos[i].a['title'].encode("utf-8")
                        titF = titF.replace('Assistir','').replace('Online','')
                        urlF = filmes[i].a['href'].encode("utf-8")
                        image_news = filmes[i]('div', {'class':'vb_image_container'})[0]
                        imgF = re.findall(r'url\(\'(.+?)\'\);',str(image_news))[0].encode("utf-8")
                        temp = [urlF, titF, imgF]
                        hosts.append(temp)

                return hosts

def doPesquisaSeries():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 26, img, False, total)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def doPesquisaFilmes():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 100, img, False, total)

        setViewFilmes()

def player(name,url,iconimage):
        xbmc.log('[plugin.video.overflix] L244 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('OverFlix', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)
        titsT = []
        idsT = []
        sub = None

        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        try:
            conteudo = soup('div',{'class':'source-box'})
            filme = conteudo[1]('a')
            urlVideo = filme[0]['href']
            fxID = urlVideo.split('src=')[-1]
            urlF = base64.b64decode(fxID).decode('utf-8')
            urlVideo = urlF
            titsT = ["Opção 1"]
            xbmc.log('[plugin.video.overflix] L249 - ' + str(urlVideo), xbmc.LOGNOTICE)
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok(" Desculpe:", " Video não disponivel! ")
            return False
            pass

        try:
            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

            if index == -1 : return

            i = int(index)
            urlVideo = urlF

            if 'verystream' in urlVideo:
                    fxID = str(idsT[i])
                    urlVideo = 'https://verystream.com/e/%s' % fxID

            elif 'onlystream' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://onlystream.tv/e/%s' % fxID
                    headers = {
                        'Referer': urlvideo,
                        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
                        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                        'Connection':'keep-alive',
                        'upgrade-insecure-requests': '1'}
                    xbmc.log('[plugin.video.overflix] L301 - ' + str(urlvideo), xbmc.LOGNOTICE)
                    r = requests.get(url=urlVideo, headers=headers)
                    data = r.content
                    url2Play = re.findall('sources\:\s*\[{file\:"([^"]+)",', data)[0]
                    xbmc.log('[plugin.video.overflix] L280 - ' + str(url2Play), xbmc.LOGNOTICE)
                    OK = False

            elif 'streamango' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://streamango.com/embed/%s' % fxID

            elif 'rapidvideo' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID

            elif 'go' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://gounlimited.to/embed-%s.html' % fxID

            elif 'mystream' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://mstream.fun/%s' % fxID
                    html = openURL(urlVideo)
                    urlF = re.findall(r'<meta name="og:image" content="(.*?)">', html)[0]
                    url = urlF.split('/snapshot.jpg')[0] + ".mp4"
                    url2Play = 'http:%s' % url if url.startswith("//") else url
                    xbmc.log('[plugin.video.overflix] L326 - ' + str(url2Play), xbmc.LOGNOTICE)
                    OK = False

            elif 'thevid' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://thevid.net/e/%s' % fxID

            elif 'openload' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://openload.co/embed/%s' % fxID

            elif 'vidoza' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://vidoza.net/embed-%s.html' % fxID

            elif 'mix' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://mixdrop.co/e/%s' % fxID
                    data = openURL(urlVideo)
                    #url2Play = re.findall('MDCore.vsrc = "(.*?)";', data)[0]
                    #url2Play = 'http:%s' % url2Play if url2Play.startswith("//") else url2Play
                    sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                    aMatches = re.compile(sPattern).findall(data)
                    sUnpacked = jsunpack.unpack(aMatches[0])
                    xbmc.log('[plugin.video.overflix] L330 - ' + str(sUnpacked), xbmc.LOGNOTICE)
                    url2Play = re.findall('MDCore.wurl="(.*?)"', sUnpacked)
                    url = str(url2Play[0])
                    url2Play = 'http:%s' % url if url.startswith("//") else url
                    OK = False

            elif 'jetload' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://jetload.net/e/%s' % fxID
                    #xbmc.log('[plugin.video.overflix] L347 - ' + str(urlVideo), xbmc.LOGNOTICE)
                    data = openURL(urlVideo)
                    xbmc.log('[plugin.video.overflix] L349 - ' + str(data), xbmc.LOGNOTICE)
                    srv = re.findall('video src="([^"]+)"', data)[0]
                    url2Play = srv
                    OK = False

            elif 'principal' in urlVideo :
                    fxID = str(idsT[i+1])
                    urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID

            xbmc.log('[plugin.video.overflix] L408 - ' + str(urlVideo), xbmc.LOGNOTICE)

        except:
            pass

        if 'uauflix' in urlVideo :
            html = openURL(urlVideo)
            try:
                urlF = re.findall(r"<iframe class='metaframe rptss' src='(.*?)' frameborder='0' scrolling='no' allow='autoplay; encrypted-media' allowfullscreen></iframe>", link)[0]
                html = requests.get(urlF).text
            except:
                pass
            xbmc.log('[plugin.video.querofilmeshd] L360 - ' + str(html), xbmc.LOGNOTICE)
            idS = re.findall(r'idS[=:]\s*"(.*?)"', html)[0]
            if idS is not None :
                d = urlparse(urlF)
                host = d.netloc
            headers = {'Referer': urlF,
                       'Accept': '*/*',
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Connection': 'keep-alive',
                       'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
            }
            if 'querofilmeshd' in urlF : urlF = base + 'CallPlayer'
            elif 'uauflix' in urlF : urlF = 'https://player.uauflix.online//CallPlayer'
            data = urllib.urlencode({'id': idS})
            html = requests.post(url=urlF, data=data, headers=headers).text
            xbmc.log('[plugin.video.querofilmeshd] L375 - ' + str(html), xbmc.LOGNOTICE)
            _html = str(html)
            b = json.loads(_html.decode('hex'))
            xbmc.log('[plugin.video.querofilmeshd] L379 - ' + str(b), xbmc.LOGNOTICE)
            urlF = b['url']
            if 'bit' in str(urlF) :
                r = requests.get(url=urlF, verify=False)
                urlF = str(r.url)
            if '//public' in urlF : urlF = urlF.replace('//public','/public')
            fxID = urlF.split('id=')[1]
            if "&" in fxID: fxID = fxID.split('&')[0]
            if "&vlsub" in urlF:
                sub = 'https://sub.sfplayer.net/subdata/' + urlF.split('vlsub=')[1]
            elif "&sub" in urlF:
                sub = urlF.split('&sub=')[1]
            host = urlF.split('/public')[0]
            t = int(round(time.time() * 1000))
            urlF = host + '/playlist/' + fxID + '/' + str(t)
            r = requests.get(url=urlF)
            titsT = re.findall('RESOLUTION=(.*?)\n/hls.+', r.text)
            idsT = re.findall('RESOLUTION=.*?\n/(.*?)\n', r.text)

            if not titsT : return

            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

            if index == -1 : return
            i = index
            urlVideo = host + '/' + idsT[i]
            urlVideo = str(urlVideo)
            if 'assistirfilmes' in str(urlVideo) :
                urlVideo = urlVideo.replace(".m3u8", "?v=") + str(t)
            url2Play = urlVideo
            OK = False

        if OK :
            try:
                xbmc.log('[plugin.video.overflix] L415 - ' + str(urlVideo), xbmc.LOGNOTICE)
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        if not url2Play : return

        xbmc.log('[plugin.video.overflix] L410 - ' + str(url2Play), xbmc.LOGNOTICE)

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play or "hls" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstreamaddon','inputstream.hls')
                listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
                #listitem.setMimeType('application/dash+xml')
                listitem.setContentLookup(False)
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('video/mp4')
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()

        while xbmcPlayer.play(playlist) :
            xbmc.sleep(20000)
            if not xbmcPlayer.isPlaying():
                xbmc.stop()

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(urllib2.urlopen(legendas).read())
                    sub_file_xml.close()
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.overflix] L484 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('OverFlix', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)
        titsT = []
        idsT = []
        sub = None

        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        try:
            conteudo = soup('div',{'class':'source-box'})
            filme = conteudo[1]('a')
            urlVideo = filme[0]['href']
            fxID = urlVideo.split('src=')[-1]
            urlF = base64.b64decode(fxID).decode('utf-8')
            urlVideo = urlF
            titsT = ["Opção 1"]
            xbmc.log('[plugin.video.overflix] L503 - ' + str(urlVideo), xbmc.LOGNOTICE)
        except:
            dialog = xbmcgui.Dialog()
            dialog.ok(" Desculpe:", " Video não disponivel! ")
            return False
            pass

        try:

            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

            if index == -1 : return

            i = int(index)
            urlVideo = urlF

            xbmc.log('[plugin.video.overflix] L519 - ' + str(urlVideo), xbmc.LOGNOTICE)

            if 'verystream' in urlVideo:
                fxID = str(idsT[i])
                urlVideo = 'https://verystream.com/e/%s' % fxID

            elif 'mix' in urlVideo :
                fxID = str(idsT[i])
                urlF = 'https://mixdrop.co/e/%s' % fxID
                #xbmc.log('[plugin.video.overflix] L470 - ' + str(urlF), xbmc.LOGNOTICE)
                data = openURL(urlF)
                url2 = re.findall(r'<script>window.location = "(.*?)";</script>', data)[0]
                url2 = 'http://mixdrop.co%s' % url2 if url2.startswith("/e/") else url2Play
                data = openURL(url2)
                #xbmc.log('[plugin.video.overflix] L475 - ' + str(data), xbmc.LOGNOTICE)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(data)
                sUnpacked = jsunpack.unpack(aMatches[0])
                #xbmc.log('[plugin.video.overflix] L476 - ' + str(sUnpacked), xbmc.LOGNOTICE)
                url2Play = re.findall('MDCore.wurl="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                url2Play = 'http:%s' % url if url.startswith("//") else url
                OK = False

            elif 'go' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://gounlimited.to/embed-%s.html' % fxID

            elif 'onlystream' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://onlystream.tv/e/%s' % fxID

            elif 'streamango' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://streamango.com/embed/%s' % fxID

            elif 'rapidvideo' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID

            elif 'mystream' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://mstream.fun/%s' % fxID
                #html = openURL(urlVideo)
                #urlF = re.findall(r'<meta name="og:image" content="(.*?)">', html)[0]
                #url = urlF.split('/snapshot.jpg')[0] + ".mp4"
                #url2Play = 'http:%s' % url if url.startswith("//") else url
                #xbmc.log('[plugin.video.overflix] L326 - ' + str(url2Play), xbmc.LOGNOTICE)
                #OK = False

            elif 'thevid' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://thevid.net/e/%s' % fxID

            elif 'openload' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://openload.co/embed/%s' % fxID

            elif 'vidoza' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://vidoza.net/embed-%s.html' % fxID

            elif 'jetload' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://jetload.net/e/%s' % fxID

            elif 'principal' in urlVideo :
                fxID = str(idsT[i+1])
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID

            xbmc.log('[plugin.video.overflix] L589 - ' + str(urlVideo), xbmc.LOGNOTICE)

        except:
            pass
            
        if 'uauflix' in urlVideo :
            html = openURL(urlVideo)
            try:
                urlF = re.findall(r"<iframe class='metaframe rptss' src='(.*?)' frameborder='0' scrolling='no' allow='autoplay; encrypted-media' allowfullscreen></iframe>", link)[0]
                html = requests.get(urlF).text
            except:
                pass
            xbmc.log('[plugin.video.querofilmeshd] L601 - ' + str(html), xbmc.LOGNOTICE)
            idS = re.findall(r'idS[=:]\s*"(.*?)"', html)[0]
            if idS is not None :
                d = urlparse(urlF)
                host = d.scheme + '://' +  d.netloc
                headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Origin': host.encode('utf-8'),
                           'Referer': urlVideo.encode('utf-8'),
                           'x-requested-with': 'XMLHttpRequest',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
            if 'uauflix' in urlVideo : urlF = 'https://player.uauflix.online//CallEpi'
            data = urllib.urlencode({'idS': idS})
            html = requests.post(url=urlF, data=data, headers=headers).text
            xbmc.log('[plugin.video.querofilmeshd] L616 - ' + str(html), xbmc.LOGNOTICE)
            _html = str(html)
            b = json.loads(_html.decode('hex'))
            xbmc.log('[plugin.video.querofilmeshd] L619 - ' + str(b), xbmc.LOGNOTICE)
            urlF = b['url']
            if 'bit' in str(urlF) :
                r = requests.get(url=urlF, verify=False)
                urlF = str(r.url)
            if '//public' in urlF : urlF = urlF.replace('//public','/public')
            fxID = urlF.split('id=')[1]
            if "&" in fxID: fxID = fxID.split('&')[0]
            if "&vlsub" in urlF:
                sub = 'https://sub.sfplayer.net/subdata/' + urlF.split('vlsub=')[1]
            elif "&sub" in urlF:
                sub = urlF.split('&sub=')[1]
            host = urlF.split('/public')[0]
            t = int(round(time.time() * 1000))
            urlF = host + '/playlist/' + fxID + '/' + str(t)
            r = requests.get(url=urlF)
            titsT = re.findall('RESOLUTION=(.*?)\n/hls.+', r.text)
            idsT = re.findall('RESOLUTION=.*?\n/(.*?)\n', r.text)

            if not titsT : return

            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

            if index == -1 : return
            i = index
            urlVideo = host + '/' + idsT[i]
            urlVideo = str(urlVideo)
            if 'assistirfilmes' in str(urlVideo) :
                urlVideo = urlVideo.replace(".m3u8", "?v=") + str(t)
            url2Play = urlVideo
            OK = False
            
        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        if not url2Play : return

        xbmc.log('[plugin.video.overflix] L662 - ' + str(url2Play), xbmc.LOGNOTICE)

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play or "hls" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstreamaddon','inputstream.hls')
                listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
                #listitem.setMimeType('application/dash+xml')
                listitem.setContentLookup(False)
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('video/mp4')
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()

        while xbmcPlayer.play(playlist) :
            xbmc.sleep(20000)
            if not xbmcPlayer.isPlaying():
                xbmc.stop()

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(urllib2.urlopen(legendas).read())
                    sub_file_xml.close()
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

############################################################################################################

def openConfig():
        selfAddon.openSettings()
        setViewMenu()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def openConfigEI():
        eiID  = 'script.extendedinfo'
        eiAD  = xbmcaddon.Addon(id=eiID)

        eiAD.openSettings()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))

def openURL(url):
        req = urllib2.Request(url)
        req.add_header('Referer',url)
        req.add_header('Upgrade-Insecure-Requests',1)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

def postURL(url):
        headers = {'Referer': base,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'Host': 'www.midiaflixhd.net',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
        }

        req = urllib2.Request(url, "",headers)
        req.get_method = lambda: 'POST'
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

def addDir(name, url, mode, iconimage, total=1, pasta=True):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)

        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def addDirF(name,url,mode,iconimage,pasta=True,total=1) :
        u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name, iconImage="iconimage", thumbnailImage=iconimage)

        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type="Video", infoLabels={"title": name})

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)

        return ok

def getInfo(url)    :
        link = openURL(url)
        titO = re.findall('<meta property="og:title" content="(.*?)">', link)[0]
        titO = titO.split("(")[0]
        titO = titO.replace('Assistir ','').replace(' Dublado ','').replace('Online','')
        titO = titO.replace(' Legendado ','').replace('(2019)','')
        #xbmc.log('[plugin.video.overflix] L665 - ' + str(titO), xbmc.LOGNOTICE)

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        ytID = re.findall('<a id="open-trailer" class="btn iconized trailer" data-trailer="https://www.youtube.com/embed/(.*?)rel=0&amp;controls=1&amp;showinfo=0&autoplay=0"><b>Trailler</b> <i class="icon fa fa-play"></i></a>', link)[0]
        ytID = ytID.replace('?','')

        xbmc.executebuiltin('XBMC.RunPlugin("plugin://script.extendedinfo/?info=youtubevideo&&id=%s")' % ytID)

def setViewMenu() :
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

        opcao = selfAddon.getSetting('menuVisu')

        if     opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def setViewFilmes() :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

        opcao = selfAddon.getSetting('filmesVisu')

        if     opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
        elif opcao == '3': xbmc.executebuiltin("Container.SetViewMode(501)")
        elif opcao == '4': xbmc.executebuiltin("Container.SetViewMode(508)")
        elif opcao == '5': xbmc.executebuiltin("Container.SetViewMode(504)")
        elif opcao == '6': xbmc.executebuiltin("Container.SetViewMode(503)")
        elif opcao == '7': xbmc.executebuiltin("Container.SetViewMode(515)")

def limpa(texto):
        texto = texto.replace('ç','c').replace('ã','a').replace('õ','o')
        texto = texto.replace('â','a').replace('ê','e').replace('ô','o')
        texto = texto.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
        texto = texto.replace(' ','-')
        texto = texto.lower()

        return texto

############################################################################################################

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]

        return param

params      = get_params()
url          = None
name      = None
mode      = None
iconimage = None

try       : url=urllib.unquote_plus(params["url"])
except : pass
try       : name=urllib.unquote_plus(params["name"])
except : pass
try       : mode=int(params["mode"])
except : pass
try       : iconimage=urllib.unquote_plus(params["iconimage"])
except : pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)

###############################################################################################################

if     mode == None : menuPrincipal()
elif mode == 10      : getCategorias(url)
elif mode == 20      : getFilmes(url)
elif mode == 25      : getSeries(url)
elif mode == 26      : getTemporadas(name,url,iconimage)
elif mode == 27      : getEpisodios(name,url)
elif mode == 30      : doPesquisaSeries()
elif mode == 35      : doPesquisaFilmes()
elif mode == 40      : getFavoritos()
elif mode == 41      : addFavoritos(name,url,iconimage)
elif mode == 42      : remFavoritos(name,url,iconimage)
elif mode == 43      : cleanFavoritos()
elif mode == 98      : getInfo(url)
elif mode == 99      : playTrailer(name,url,iconimage)
elif mode == 100  : player(name,url,iconimage)
elif mode == 110  : player_series(name,url,iconimage)
elif mode == 999  : openConfig()
elif mode == 1000 : openConfigEI()

xbmcplugin.endOfDirectory(int(sys.argv[1]))