#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : SuperFlix
# By AddonBrasil - 06/12/2019
# Atualizado (1.0.0) - 24/06/2021
# Atualizado (2.0.0) - 12/07/2021
#####################################################################

import urllib, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from bs4 import BeautifulSoup
from resources.lib import jsunpack
import time

version   = '2.0.0'
addon_id  = 'plugin.video.superflix'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = xbmcaddon.Addon()
_handle = int(sys.argv[1])

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/resources/fanart.png'
base        = 'https://superflix.vip/'
sbase       = 'navegar/series-2/?alphabet=all&sortby=v_started&sortdirection=desc'
v_views     = 'filmes-e-series-online-top-mais-vistos/'
v_dublados  = 'categoria/assistir-filmes-dublados-online/?type=movies'

############################################################################################################

def menuPrincipal():
        addDir('Categorias Filmes'          , base + 'assistir-filmes-online/'          ,    10, artfolder + 'categorias.png')
        addDir('Categorias Series'          , base + 'assistir-series-online/'          ,    10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'assistir-filmes-online/'          ,    20, artfolder + 'lancamentos.png')
        addDir('Filmes Dublados'            , base + v_dublados                         ,    20, artfolder + 'pesquisa.png')
        addDir('Filmes Mais Assistidos'     , base + v_views                            ,    20, artfolder + 'pesquisa.png')
        addDir('Series'                     , base + 'assistir-series-online/'          ,    25, artfolder + 'legendados.png')
        addDir('Pesquisa Series'            , '--'                                      ,    30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                                      ,    35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                                      ,   999, artfolder + 'config.png', 1, False)
        #addDir('Configurações ExtendedInfo' , base                                      ,  1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup.findAll('ul', attrs={'class':'sub-menu'})

        if 'filmes' in url :
                categorias   = conteudo[1]('li')
        elif 'series' in url:
                categorias   = conteudo[2]('li')

        for categoria in categorias:
                titC = categoria.a.text   #.encode('utf-8','')
                urlC = categoria.a["href"]
                imgC = artfolder + limpa(titC) + '.png'
                if 'filmes' in url:
                    addDir(titC,urlC,20,imgC)
                elif 'series' in url:
                    addDir(titC,urlC,25,imgC)

        setViewMenu()

def getFilmes(name,url,iconimage):
        xbmc.log("[plugin.video.SuperFlix] L77 - " + str(url), xbmc.LOGINFO)
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('main')
        dados = conteudo[0]('ul')
        a = len(dados)
        if a > 2 :
                lista = dados[0]('li')
        elif a == 2 :
                lista = dados[1]('li')
        elif a == 1 :
                lista = dados[0]('li')
        totF = len(lista)

        for f in lista:
                filme = f('article', attrs={'class':'post dfx fcl movies'})
                #xbmc.log("[plugin.video.SuperFlix] L87 - " + str(filme), xbmc.LOGINFO)
                titF = filme[0].header.h2.text.encode('utf-8')
                urlF = filme[0].a['href']
                imgF = filme[0].img['data-lazy-src']
                imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
                addDirF(titF, urlF, 100, imgF, False, totF)

        try :
                next_page = soup('div', attrs={'class':'nav-links'})
                pg = next_page[0]('a')
                i = len(pg)
                i = (i - 1)
                proxima = pg[i]['href']
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.SuperFlix] L114 - ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('main')
        dados = conteudo[0]('ul',attrs={'class':'post-lst rw sm rcl2 rcl3a rcl4b rcl3c rcl4d rcl6e'})
        lista = dados[0]('li')
        totF = len(lista)

        for f in lista:
                filme = f('article', attrs={'class':'post dfx fcl movies'})
                titF = filme[0].header.h2.text.encode('utf-8')
                urlF = filme[0].a['href']
                imgF = filme[0].img['src']
                imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
                addDir(titF, urlF, 26, imgF)

        try :
                next_page = soup('div', attrs={'class':'nav-links'})
                pg = next_page[0]('a')
                i = len(pg)
                i = (i - 1)
                proxima = pg[i]['href']
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(name,url,iconimage):
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('a',{'class':'btn lnk npd aa-arrow-right'})
        #conteudo = soup('section',{'class':'section episodes'})
        #dados = conteudo[0]('header',{'class':'section-header'})
        #seasons = dados[0]('a')
        #tF = len(dados)
        totF = len(conteudo)
        image = soup('article', {'class':'post single'})
        figure = image[0]('figure')
        imgF = figure[0].img['src']
        imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
        i = 0

        for i in range(totF):
                i = i + 1
                titF = str(i) + "ª Temporada"
                urlF = url
                addDirF(titF, urlF, 27, imgF, True, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
        xbmc.log('[plugin.video.SuperFlix] L164 - ' + str(url), xbmc.LOGINFO)
        n = name.replace('ª Temporada', '')
        n = int(n)
        n = n - 1
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('a',{'class':'btn lnk npd aa-arrow-right'})
        urlF = conteudo[n]['href']
        link = openURL(urlF)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('section',{'class':'section episodes'})
        dados = conteudo[0]('ul', {'id':'episode_by_temp'})
        episodes = dados[0]('li')
        totF = len(dados)
        figure = conteudo[0]('figure')
        imgF = figure[0].img['src']
        imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF

        for i in episodes:
            urlF = i.a['href']
            titF = urlF.split('/')[4].encode('utf-8')
            try:
                imgF = i.img['src']
            except:
                pass
            imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
            addDirF(titF, urlF, 110, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')

def pesquisa():
        hosts = []
        temp = []
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes/Series')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto = keyb.getText()
                pesquisa = urllib.parse.quote(texto)

                data = '' #urllib.parse.urlencode({'term':pesquisa})
                url = base + '?s=' + pesquisa

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                r = requests.post(url=url, data=data, headers=headers)
                link = r.content
                #link = unicode(link, 'utf-8', 'replace')
                soup = BeautifulSoup(link, "html.parser")
                conteudo = soup('main')
                dados = conteudo[0]('ul')
                lista = dados[1]('li')
                totF = len(lista)

                for f in lista:
                        xbmc.log('[plugin.video.SuperFlix] L219 - ' + str(f), xbmc.LOGINFO)
                        filme = f('article', attrs={'class':'post dfx fcl movies'})
                        titF = filme[0].header.h2.text.encode('utf-8')
                        urlF = filme[0].a['href']
                        imgF = filme[0].img['src']
                        imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
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
            addDirF(titulo, url2, 100, img, False, total)

        setViewFilmes()

def player(name,url,iconimage):
        xbmc.log('[plugin.video.SuperFlix] L249 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('SuperFlix', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)
        titsT = []
        idsT = []
        sub = None

        html = openURL(url)
        soup = BeautifulSoup(html, "html.parser")
        conteudo = soup('aside')
        srvs = conteudo[2]('span', {'class':'server'})

        for s in srvs:
            b = s.text
            b = b.replace(' ','')
            titsT.append(b)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        i = int(index)

        servers = conteudo[2]('span', {'class':'server'})
        totF = len(servers)
        for s in servers:
            try:
                urlS = s.iframe['src']
                idsT.append(urlS)
            except:
                pass
            try:
                l = s.get_text('src')
                urlS = re.findall(r'src="(.*?)"', l)[0].replace('#038;','')
                idsT.append(urlS)
            except:
                pass
            try:
                postid = re.findall(r'<body class="movies-template-default single single-movies postid-(.*?) wp-custom-logo side-right ">', html)[0]
                urlS = 'http://superflix.vip/?trembed=%s&trid=%s&trtype=1' % (i,postid)
                idsT.append(urlS)
            except:
                pass
        filme = idsT[i]
        xbmc.log('[plugin.video.SuperFlix] L296 - ' + str(filme), xbmc.LOGINFO)
        url2Play = filme
        html = openURL(url2Play)
        soup = BeautifulSoup(html, "html.parser")
        urlF = soup('iframe')[0]['src']

        xbmc.log('[plugin.video.SuperFlix] L304 - ' + str(urlF), xbmc.LOGINFO)
        
        if 'play' in urlF :
            headers = {'Referer': urlF,
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
               }
            r = requests.get(urlF)
            link = r.text
            link = openURL(urlF)
            urlF = r.url
            #urlVideo = re.findall(r'\"file\":\"(.*?)\"', link)[0]
        elif 'api.topflix' in urlF :
            html = openURL(urlF)
            urlVideo = re.findall("addiframe\('(.*?)'\);", html)[0]
            html = openURL(urlVideo)
            url2Play = re.findall(r'olplayer.src\(\{\n\s*src:\s*\'(.*?)\',\n\s*type:\s*\'application/x-mpegURL\'\n\s*\}\);',html)[0]
            xbmc.log('[plugin.video.SuperFlix] L318 - ' + str(html), xbmc.LOGINFO)
            OK = False
        
        elif 'trhide' in urlF :
            fxID = urlF.split('id=')[1]
            fxID = fxID.replace('&','')
            inverte = fxID[::-1]
            headers = {'Referer': urlF,
               'Upgrade-Insecure-Requests': '1',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
               }
            urlS = inverte.decode("hex")
            headers = {'Referer': urlF,
                       'Content-Type': 'application/x-www-form-urlencoded',
                       'Connection': 'keep-alive',
                       'Upgrade-Insecure-Requests': '1',
                       'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
                    }
            r = requests.get(url=urlS,headers=headers)
            url2Play = re.findall(r'var urlVideo = \'(.*?)\';',r.content)[1]
            xbmc.log('[plugin.video.SuperFlix] L332 - ' + str(urlF), xbmc.LOGINFO)

        if 'index.html' in urlF :
            fxID = urlF.split('id=')[1]
            if "&" in fxID: fxID = fxID.split('&')[0]
            host = urlF.split('public')[0]
            t = int(round(time.time() * 1000))
            '''trembed = 0 (dublado) | trembed = 1 (legendado) '''
            if "vlsub" in urlF:
                sub = 'https://sub.sfplayer.net/subdata/' + urlF.split('vlsub=')[1]
            #https://lbsuper3.sfplayer.net/playlist/e267a03be5f1204567da9fc99a9114f2/1624538417174
            urlF = host + 'playlist/%s/%s.m3u8' % (fxID, t)
            #urlF = 'https://slave1plus.sfplayer.net/hls/%s/%s.m3u8' % (fxID, fxID)
            #urlF = 'https://slave1plus.sfplayer.net/vl/%s?t=%s' % (fxID, t)
            #'https://002.yandexcloud.ga/drive/hls/%s/%s.m3u8' % (fxID, fxID)
            headers = {'accept-encoding': 'gzip, deflate, br',
                   'authority': 'lbsuper.sfplayer.net',
                   'accept': '*/*',
                   'x-requested-with': 'XMLHttpRequest',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
                }
            r = requests.get(url=urlF,headers=headers)
            titsT = re.findall('RESOLUTION=(.*?)\n/hls.+',r.text)
            idsT = re.findall('RESOLUTION=.*?\n/(.*?)\n',r.text)

            if not titsT : return

            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

            if index == -1 : return
            i = index
            urlVideo = host + idsT[i]
            url2Play = urlVideo
            OK = False

        xbmc.log('[plugin.video.SuperFlix] L346 - ' + str(url2Play), xbmc.LOGINFO)

        if OK :
            try:
                xbmc.log('[plugin.video.SuperFlix] L352 - ' + str(urlVideo), xbmc.LOGINFO)
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        if not url2Play : return

        xbmc.log('[plugin.video.SuperFlix] L362 - ' + str(url2Play), xbmc.LOGINFO)

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name +' Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setProperty('IsPlayable', 'true')
                listitem.setContentLookup(False)
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.hls')
                #listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
                '''
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.ffmpegdirect')
                listitem.setProperty('inputstream.ffmpegdirect.is_realtime_stream', 'false')
                listitem.setProperty('inputstream.ffmpegdirect.mistream_mode', 'timeshift')
                listitem.setProperty('inputstream.ffmpegdirect.manifest_type', 'hls')'''
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
                    sub_file_xml.write(requests.get(legendas).text)
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.SuperFlix] L411 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('SuperFlix', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)
        titsT = []
        idsT = []
        sub = None

        r = requests.get(url)
        html = r.content
        soup = BeautifulSoup(html, "html.parser")
        conteudo = soup('aside')
        srvs = conteudo[2]('span', {'class':'server'})

        for s in srvs:
            b = s.text
            b = b.replace(' ','')
            titsT.append(b)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        i = int(index)

        servers = conteudo[1]('a')
        totF = len(servers)
        for s in servers:
            try:
                auth = s['href']
                shex = auth.split('=')[1]
                urlS = bytes.fromhex(shex).decode('utf-8')
                urlS = urlS.replace('#038;','')
                urlS = 'https:%s' % urlS if urlS.startswith("//") else urlS
                idsT.append(urlS)
            except:
                pass
            try:
                l = s.get_text('src')
                urlS = re.findall(r'src="(.*?)"', l)[0].replace('#038;','')
                idsT.append(urlS)
            except:
                pass
            try:
                postid = re.findall(r'<body class="movies-template-default single single-movies postid-(.*?) side-right ">', r.text)[0]
                urlS = 'http://superflix.vip/?trembed=%s&trid=%s&trtype=2' % (i,postid)
                idsT.append(urlS)
            except:
                pass
        filme = idsT[i]
        xbmc.log('[plugin.video.SuperFlix] L495 - ' + str(filme), xbmc.LOGINFO)


        if 'trembed' in filme:
            urlVideo = filme
            url2Play = urlVideo
            OK =False
            r = requests.get(filme)
            html = r.content
            soup = BeautifulSoup(html, "html.parser")
            urlF = soup('iframe')[0]['src']

            if 'index.html' in urlF :
                fxID = urlF.split('id=')[1]
                if "&" in fxID: fxID = fxID.split('&')[0]
                host = urlF.split('public')[0]
                t = int(round(time.time() * 1000))
                '''trembed = 0 (dublado) | trembed = 1 (legendado) '''
                if "vlsub" in urlF:
                    sub = 'https://sub.sfplayer.net/subdata/' + urlF.split('vlsub=')[1]

                urlF = host + 'playlist/%s/%s.m3u8' % (fxID, t)
                auth = host.replace("https://","").replace("/","")

                xbmc.log('[plugin.video.SuperFlix] L518 - ' + str(auth), xbmc.LOGINFO)

                headers = {'accept-encoding': 'gzip, deflate, br',
                       'authority': auth,
                       'scheme': 'https',
                       'accept': '*/*',
                       'x-requested-with': 'XMLHttpRequest',
                       'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36'
                }
                r = requests.get(url=urlF,headers=headers)
                #xbmc.log('[plugin.video.SuperFlix] L528 - ' + str(r.text), xbmc.LOGINFO)
                titsT = re.findall('RESOLUTION=(.*?)\n/hls.+',r.text)
                idsT = re.findall('RESOLUTION=.*?\n/(.*?)\n',r.text)

                if not titsT : return

                index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                if index == -1 : return
                i = index
                urlVideo = host + idsT[i]
                url2Play = urlVideo
                OK = False

        try:

            if 'mix' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://mixdrop.co/e/%s' % fxID
                data = openURL(urlVideo)
                '''
                #url2Play = re.findall('MDCore.vsrc = "(.*?)";', data)[0]
                #url2Play = 'http:%s' % url2Play if url2Play.startswith("//") else url2Play
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(data)
                sUnpacked = jsunpack.unpack(aMatches[0])
                xbmc.log('[plugin.video.SuperFlix] L482 - ' + str(sUnpacked), xbmc.LOGINFO)
                url2Play = re.findall('MDCore.vsrc="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                '''
                url2Play = 'http:%s' % url if url.startswith("//") else url
                OK = False

            elif 'drive.google.com' in urlVideo :
                OK = True

            elif 'streamango' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://streamango.com/embed/%s' % fxID

            elif 'rapidvideo' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID

            elif 'mystream' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://mstream.cloud/%s' % fxID
                r = requests.get(urlVideo)
                data = r.content
                srv = re.findall('<meta name="og:image" content="([^"]+)">', data)[0]
                url2Play = srv.replace('/img','').replace('jpg','mp4')
                OK = False

            elif 'thevid' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://thevid.net/e/%s' % fxID

            elif 'vidoza' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://vidoza.net/embed-%s.html' % fxID

            elif 'jetload' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://jetload.net/e/%s' % fxID

            elif 'stream/' in urlVideo :
                url2Play = urlVideo
                OK = False

            xbmc.log('[plugin.video.SuperFlix] L524 - ' + str(urlVideo), xbmc.LOGINFO)

        except:
            pass

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        if not url2Play : return

        xbmc.log('[plugin.video.SuperFlix] L540 - ' + str(url2Play), xbmc.LOGINFO)

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name + 'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.adaptive')
                listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
                #listitem.setMimeType('application/dash+xml')
                listitem.setContentLookup(False)
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType("video/mp4")
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(playlist)

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(requests.get(legendas).text)
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

############################################################################################################

def openConfig():
        selfAddon.openSettings()
        setViewMenu()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
'''
def openConfigEI():
        eiID  = 'script.extendedinfo'
        eiAD  = xbmcaddon.Addon(id=eiID)
        eiAD.openSettings()
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
'''
def openURL(url):
        #dialog = xbmcgui.Dialog()
        #dialog.ok("openURL Erro:", str(url))

        headers= {'Referer': url,
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36'
        }
        link = requests.get(url=url,headers=headers).text
        return link

def postURL(url):
        headers = {'Referer': base,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'Host': 'www.midiaflixhd.net',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
        }
        response = requests.post(url=url, data='', headers=headers)
        link=response.text
        return link

def addDir(name, url, mode, iconimage, total=1, pasta=True):
        u = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'icon': iconimage, 'thumb': iconimage })

        #dialog = xbmcgui.Dialog()
        #dialog.ok("addDir Erro:", str(u))

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def addDirF(name,url,mode,iconimage,pasta=True,total=1) :
        u  = sys.argv[0]+"?url="+urllib.parse.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.parse.quote_plus(name)+"&iconimage="+urllib.parse.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'icon': iconimage, 'thumb': iconimage })

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.parse.quote(name), url, urllib.parse.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def getInfo(url)    :
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', {'class':'col-thumb'})
        title = conteudo[0]('div', {'class':'thumb'})
        titO = title[0].img['alt'].encode('utf-8')
        titO = titO.replace('Legendado','').replace('Dublado','').replace('Nacional','')
        titO = titO.replace('HD','').replace('Full','').replace('2019','').replace('Filme','')

        #xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        ytID = re.findall('<iframe width="560" height="315" src="https://www.youtube.com/embed/(.*?)" .+?></iframe>', link)[0]
        ytID = ytID.replace('?','')

        #xbmc.executebuiltin('XBMC.RunPlugin("plugin://script.extendedinfo/?info=youtubevideo&&id=%s")' % ytID)

def setViewMenu() :
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

        opcao = selfAddon.getSetting('menuVisu')

        if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def setViewFilmes() :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

        opcao = selfAddon.getSetting('filmesVisu')

        if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
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

params    = get_params()
url       = None
name      = None
mode      = None
iconimage = None

try       : url=urllib.parse.unquote_plus(params["url"])
except : pass
try       : name=urllib.parse.unquote_plus(params["name"])
except : pass
try       : mode=int(params["mode"])
except : pass
try       : iconimage=urllib.parse.unquote_plus(params["iconimage"])
except : pass

print("Mode: "+str(mode))
print("URL: "+str(url))
print("Name: "+str(name))
print("Iconimage: "+str(iconimage))

###############################################################################################################

if   mode == None : menuPrincipal()
elif mode == 10   : getCategorias(url)
elif mode == 20   : getFilmes(name,url,iconimage)
elif mode == 25   : getSeries(url)
elif mode == 26   : getTemporadas(name,url,iconimage)
elif mode == 27   : getEpisodios(name,url)
elif mode == 30   : doPesquisaSeries()
elif mode == 35   : doPesquisaFilmes()
elif mode == 40   : getFavoritos()
elif mode == 41   : addFavoritos(name,url,iconimage)
elif mode == 42   : remFavoritos(name,url,iconimage)
elif mode == 43   : cleanFavoritos()
elif mode == 98   : getInfo(url)
elif mode == 99   : playTrailer(name,url,iconimage)
elif mode == 100  : player(name,url,iconimage)
elif mode == 110  : player_series(name,url,iconimage)
elif mode == 999  : openConfig()
#elif mode == 1000 : openConfigEI()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
