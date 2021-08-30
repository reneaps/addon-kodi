#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : MegaFilmesOnlineHD
# By AddonReneSilva - 11/12/2015
# Atualizado (1.0.1) - 02/11/2016
# Atualizado (1.1.0) - 14/06/2018
# Atualizado (1.1.1) - 01/09/2019
# Atualizado (1.1.2) - 27/03/2020
# Atualizado (1.1.3) - 07/07/2020
# Atualizado (1.1.4) - 20/10/2020
# Atualizado (1.1.5) - 30/08/2021
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver
import requests
import json

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib               import jsunpack
from urlparse import urlparse

s = requests.Session()

version     = '1.1.5'
addon_id    = 'plugin.video.megafilmesonlinehd'
selfAddon   = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/img/'
fanart      = addonfolder + '/fanart.png'
base        = 'https://megafilmeshd50.com/'

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                , base + '/'                             ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'               , base + 'categoria/lancamentos/'        ,   20, artfolder + 'ultimos.png')
        addDir('Melhor Classificação'      , base + 'ratings/?get=movies'           ,   20, artfolder + 'filmes.png')
        addDir('Seriados'                  , base + 'serie/'                        ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'           , '--'                                   ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'           , '--'                                   ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'             , base                                   ,  999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo', base                                   , 1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link)
        conteudo = soup("div", {"class": "head-main-nav"})
        dados = conteudo[0]("ul")
        categorias = dados[0]('li')

        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.a.text.encode('utf-8','replace')
                if not 'Lançamento' in titC :
                    if not 'Categorias' in titC:
                        urlC = categoria.a["href"]
                        imgC = artfolder + limpa(titC) + '.png'
                        addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        xbmc.log('[plugin.video.megafilmesonlinehd] L67 - ' + str(url), xbmc.LOGNOTICE)
        link  = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup     = BeautifulSoup(link)
        filmes = soup("article", {"class":"item movies"})
        totF = len(filmes)

        for filme in filmes:
                urlF = filme.a["href"].encode('utf-8')
                imgF = filme.img["src"].encode('utf-8')
                titF = filme.img["alt"].encode('utf-8')
                imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
                addDirF(titF, urlF, 100, imgF, False, totF)

        try :
                proxima = re.findall('<link rel="next" href="(.*?)" />', link)[0]
                xbmc.log('[plugin.video.megafilmesonlinehd] L87 - ' + str(proxima), xbmc.LOGNOTICE)
                #getFilmes(proxima)
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.megafilmesonlinehd] L96 - ' + str(url), xbmc.LOGNOTICE)
        link  = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        filmes = soup("article", {'class':'item tvshows'})
        totF = len(filmes)

        for filme in filmes:
                urlF = filme.a["href"].encode('utf-8')
                imgF = filme.img["src"].encode('utf-8')
                titF = filme.img["alt"].encode('utf-8')
                imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
                addDir(titF, urlF, 26, imgF)

        try :
                proxima = re.findall('<link rel="next" href="(.*?)" />', link)[0]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass
                
        setViewFilmes()

def getTemporadas(url):
        xbmc.log('[plugin.video.megafilmesonlinehd] L119 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup('div', {'class':'sheader'})
        figure = conteudo[0]('div', {'class':'poster'})
        imgF = figure[0].img['src']
        imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
        seasons = soup('div',{'class':'se-c'})
        totF = len(seasons)
        i = 0

        for i in range(totF):
                i = i + 1
                titF = str(i) + "ª Temporada"
                urlF = url
                addDir(titF, urlF, 27, imgF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
        n = name.replace('ª Temporada', '')
        n = int(n)
        n = n - 1
        link = openURL(url)
        soup = BeautifulSoup(link)
        conteudo = soup('div', {'class':'sheader'})
        figure = conteudo[0]('div', {'class':'poster'})
        imgF = figure[0].img['src']
        conteudo = soup('div', {'class':'se-c'})
        dados = conteudo[n]('ul', {'class':'episodios'})
        episodes = dados[0]('li')
        totF = len(episodes)
        
        for i in episodes:
            urlF = i.a['href']
            #if not url in urlF : urlF = base + urlF
            imgF = i.img['src']
            if 'url=' in imgF : imgF = imgF.split('=')[3]
            imgF = imgF.replace('w154', 'w300')
            imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
            imgF = base + imgF if imgF.startswith("/wp-content") else imgF
            #titA = i(class_='numerando')[0].text.replace('-','x')
            #titB = i.a.text  #i(class_='episodiotitle')[0].a.text
            #titF = titA + ' - ' + titB
            titF = i.a.text + ', ' + i.span.text
            titF = titF.encode('utf-8')
            addDirF(titF, urlF, 110, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes/Series')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.quote(texto)
                url      = base + '?s=%s' % str(pesquisa)
                hosts = []

                link  = openURL(url)
                #link = unicode(link, 'utf-8', 'ignore')
                soup = BeautifulSoup(link)
                filmes = soup("article")
                totF = len(filmes)

                for filme in filmes:
                        urlF = filme.a["href"].encode('utf-8')
                        imgF = filme.img["src"].encode('utf-8')
                        titF = filme.img["alt"].encode('utf-8')
                        imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
                        temp = [urlF, titF, imgF]
                        hosts.append(temp)

                a = []
                for url, titulo, img in hosts:
                    temp = [url, titulo, img]
                    a.append(temp);

                return a

def doPesquisaSeries():
        a = pesquisa()
        total = len(a)
        for url2, titulo, img in a:
            if 'serie' in str(url2):
                addDir(titulo, url2, 26, img, False, total)
            else:
                addDirF(titulo, url2, 100, img, False, total)
                
        setViewFilmes()
        
def doPesquisaFilmes():
        a = pesquisa()
        total = len(a)
        for url2, titulo, img in a:
            if 'serie' in str(url2):
                addDir(titulo, url2, 26, img, False, total)
            else:
                addDirF(titulo, url2, 100, img, False, total)
                
        setViewFilmes()

def player(name,url,iconimage):
        xbmc.log('[plugin.video.megafilmesonlinehd] L223 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MegaFilmesOnline', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        matriz = []
        '''
        html = openURL(urlF)
        links = re.findall("addiframe\('(.*?)'\);", html)
        
        for i in links:
            titsT.append(i)
            idsT.append(i)
            xbmc.log('[plugin.video.megafilmesonlinehd] L289 - ' + str(i), xbmc.LOGNOTICE)
            
        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        i = int(index)
        link = idsT[i]
        '''
        urlVideo = url
        
        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'nowvideo.php' in urlVideo :
                nowID = urlVideo.split("id=")[1]
                urlVideo = 'http://embed.nowvideo.sx/embed.php?v=%s' % nowID

        elif 'verystream' in urlVideo:
                if '/e/' in urlVideo :
                        fxID = urlVideo.split("/e/")[1]
                        urlVideo = 'https://verystream.com/e/%s' % fxID
                elif 'stream' in urlVideo :
                        fxID = urlVideo.split("/stream/")[1]
                        urlVideo = 'https://verystream.com/stream/%s' % fxID

        elif 'video.tt' in urlVideo :
                vttID = urlVideo.split('e/')[1]
                urlVideo = 'http://www.video.tt/watch_video.php?v=%s' % vttID

        elif 'vcstream.to' in urlVideo :
                vttID = urlVideo.split('/')[4]
                urlVideo = 'https://vcstream.to/embed/%s' % vttID

        elif 'flashx.php' in urlVideo :
                fxID = urlVideo.split('id=')[1]
                urlVideo = 'http://www.flashx.tv/embed-%s.html' % fxID

        elif 'ok.php' in urlVideo :
                okID = urlVideo.split('id=')[1]
                urlVideo = 'https://ok.ru/videoembed/%s' % okID

        elif 'open.php' in urlVideo :
                okID = urlVideo.split('id=')[1]
                urlVideo = 'https://openload.co/embed/%s' % okID

        elif 'streamango2' in urlVideo :
                vttID = urlVideo.split('?')[1].split('=')[1].split('&')[0]
                urlVideo = 'http://streamplay.to/f/%s' % vttID

        elif 'drive.php' in urlVideo :
                okID = urlVideo.split('id=')[1]
                urlVideo = 'https://docs.google.com/file/d/%s/preview' % okID

        elif 'rvid' in urlVideo :
                fxID = urlVideo.split('id=')[1]
                urlVideo = 'https://www.raptu.com/?v=%s' % fxID

        elif 'netu.php' in urlVideo :
                okID = urlVideo.split('id=')[1]
                urlVideo = 'http://hqq.tv/player/embed_player.php?vid=%s' % okID

        elif 'thevid' in urlVideo :
                fxID = urlVideo.split('/')[4]
                urlVideo = 'https://thevid.tv/v/%s/' % fxID

        elif 'trembed' in urlVideo :
                url2Play = urlVideo
                OK = False

        elif 'megafilmeshd50' in urlVideo :
                headers = {
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
                }
                r = s.get(url=urlVideo, headers=headers)
                link = r.text
                postid = re.findall(r'<body class="movies-template-default single single-movies postid-(.*?)">', link)[0]         
                urlF = 'https://megafilmeshd50.com/wp-json/dooplayer/v2/%s/movie/1' % postid
                r = s.get(url=urlF, headers=headers)
                url2 = r.json()['embed_url']
                #js = json.loads(link)
                #url2 = js['embed_url'].encode('utf-8')
                xbmc.log('[plugin.video.megafilmesonlinehd] L315 - ' + str(url2), xbmc.LOGNOTICE)
                parse = urlparse(url2)
                host = parse.scheme + '://' + parse.netloc
                auth = parse.netloc
                path = parse.path +'?' + parse.query
                headers = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'DNT':'1',
                    'Host':'play.megafilmeshd50.com',
                    'Referer': 'https://megafilmeshd50.com/',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
                }
                response = s.get(url=url2, headers=headers)
                #xbmc.log('[plugin.video.megafilmesonlinehd] L339 - ' + str(response.text.encode('utf-8')), xbmc.LOGNOTICE)
                if response.status_code >= 200 and response.status_code <= 299:
                    # Sucesso
                    link = response.text
                    if re.search('baixar=', r.text) is None:
                        print('Não achei...')
                        url2Play = url2
                    else:
                        urlVideo = re.findall(r'baixar=\s*\"(.+?)\"', link)[-1]
                        url2Play = urlVideo
                    if re.search('source:', r.text) is None:
                        print('Não achei...')
                        url2Play = url2
                    else:
                        urlVideo = re.findall(r'source:\s*\"(.+?)\"', link)[-1]
                        url2Play = urlVideo
                else:
                    # Erros
                    url2Play = url2
                OK = False

        elif 'filmeseries' in urlVideo :
                host = urlVideo.split('/embed/')[0]
                auth = host.replace('https://','').replace('/','')
                headers = {
                        'Host': str(auth),
                        'Referer': str(host),
                        'DNT':'1',
                        'upgrade-insecure-requests': '1',
                        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                link = requests.get(url=urlVideo,headers=headers).text
                #link = openURL(urlVideo)
                xbmc.log('[plugin.video.megafilmesonlinehd] L359 - ' + str(headers), xbmc.LOGNOTICE)
                url2Play = re.findall(r'file:\s*"(.+?)",', link)[0]
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

        xbmc.log('[plugin.video.megafilmesonlinehd] L374 - ' + str(url2Play), xbmc.LOGNOTICE)
        
        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()

        if "m3u8" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstreamaddon', 'inputstream.hls')
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
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmesESeriesOnline', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        matriz = []

        '''
        try:
            conteudo = soup("div",{"class":"list_play"})
            srvsdub = conteudo[0]("a")
        except:
            pass
        try:
            conteudo = soup("div",{"class":"player"})
            srvsdub = conteudo[0]("a")
        except:
            pass

        totD = len(srvsdub)

        for i in range(totD) :
                srv = srvsdub[i].text
                srv = srv.replace('Assistir no ', '')
                titsT.append(srv)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        i = index

        urlVideo = srvsdub[i]['href']
        '''
        urlVideo = url

        xbmc.log('[plugin.video.megafilmesonlinehd] L441 ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'play.php?man=' in urlVideo :
                nowID = urlVideo.split('?')[1].split('=')[1].split('/')[0]
                urlVideo = 'http://streamango.com/embed/%s' % nowID

        elif 'play.php?vt=' in urlVideo :
                vttID = urlVideo.split('?')[1].split('=')[1].split('/')[0]
                urlVideo = 'http://vidto.me/embed-%s-640x430.html' % vttID

        elif 'strplay' in urlVideo :
                vttID = urlVideo.split('?')[1].split('=')[1].split('&')[0]
                urlVideo = 'http://streamplay.to/%s' % vttID

        elif 'flashx.php' in urlVideo :
                fxID = urlVideo.split('id=')[1]
                urlVideo = 'http://www.flashx.tv/embed-%s.html' % fxID

        elif 'ok.php' in urlVideo :
                okID = urlVideo.split('id=')[1]
                urlVideo = 'https://ok.ru/videoembed/%s' % okID

        elif 'opload' in urlVideo :
                okID = urlVideo.split('?')[1].split('=')[1].split('/')[0]
                urlVideo = 'https://openload.co/embed/%s' % okID

        elif 'vt.php' in urlVideo :
                okID = urlVideo.split('?')[1].split('=')[1].split('/')[0]
                urlVideo = 'http://vidto.me/embed-%s-640x430.html' % okID

        elif 'rvid.php' in urlVideo :
                fxID = urlVideo.split('id=')[1]
                urlVideo = 'https://www.raptu.com/?v=%s' % fxID

        elif 'netu.php' in urlVideo :
                okID = urlVideo.split('id=')[1]
                urlVideo = 'http://hqq.tv/player/embed_player.php?vid=%s' % okID

        elif 'play.php?tvid=' in urlVideo :
                fxID = urlVideo.split('?')[1].split('=')[1].split('/')[0]
                urlVideo = 'http://thevid.net/v/%s' % fxID

        elif 'thevid.net' in urlVideo :
                fxID = urlVideo.split('/e/')[1]
                urlVideo = 'http://thevid.net/v/%s' % fxID

        elif 'trembed' in urlVideo :
                url2Play = urlVideo
                OK = False

        elif 'megafilmeshd50' in urlVideo :
                headers = {
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
                }
                r = s.get(url=urlVideo, headers=headers)
                link = r.text
                postid = re.findall(r'<body class="episodes-template-default single single-episodes postid-(.*?)">', link)[0]         
                urlF = 'https://megafilmeshd50.com/wp-json/dooplayer/v2/%s/tv/1' % postid
                r = s.get(url=urlF, headers=headers)
                url2 = r.json()['embed_url']
                #js = json.loads(link)
                #url2 = js['embed_url'].encode('utf-8')
                xbmc.log('[plugin.video.megafilmesonlinehd] L315 - ' + str(url2), xbmc.LOGNOTICE)
                parse = urlparse(url2)
                host = parse.scheme + '://' + parse.netloc
                auth = parse.netloc
                path = parse.path +'?' + parse.query
                headers = {
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Connection': 'keep-alive',
                    'DNT':'1',
                    'Host':'play.megafilmeshd50.com',
                    'Referer': 'https://megafilmeshd50.com/',
                    'Upgrade-Insecure-Requests':'1',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
                }
                response = s.get(url=url2, headers=headers)
                if response.status_code >= 200 and response.status_code <= 299:
                    # Sucesso
                    link = response.text
                    urlVideo = re.findall(r'baixar=\s*\"(.+?)\"', link)[-1]
                    url2Play = urlVideo
                else:
                    # Erros
                    url2Play = url2
                OK = False

        if OK : url2Play = urlresolver.resolve(urlVideo)

        if not url2Play : return

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        listitem = xbmcgui.ListItem(name,thumbnailImage=iconimage)
        listitem.setPath(url2Play)
        listitem.setProperty('mimetype','video/mp4')
        listitem.setProperty('IsPlayable', 'true')
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
        parse = urlparse(url)
        host = parse.scheme + '://' + parse.netloc
        auth = parse.netloc
        path = parse.path +'?' + parse.query
        headers = {
                #'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                #'Connection': 'keep-alive',
                #'DNT':'1',
                #'Host': str(auth),
                'Referer': url,
                'Upgrade-Insecure-Requests':'1',
                'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
        }
        r = s.get(url=url, headers=headers)
        link = r.text
        #req = urllib2.Request(url)
        #req.add_header('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64; Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        #response = urllib2.urlopen(req)
        #link=response.read()
        #response.close()
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
        liz.setInfo(type="Video", infoLabels={"Title": name})

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)

        return ok

def getInfo(url)    :
        link = openURL(url)
        titO = re.findall('<li>Titulo original: <span>(.*?)</span>thevid', link)[0]

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        ytID = re.findall('<iframe width=".*?" height=".*?" src="https://www.youtube.com/embed/(.*?)" frameborder="0" allowfullscreen></iframe>', link)[0]

        xbmc.executebuiltin('XBMC.RunPlugin("plugin://script.extendedinfo/?info=youtubevideo&&id=%s")' % ytID)

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
        elif opcao == '8': xbmc.executebuiltin("Container.SetViewMode(550)")
        elif opcao == '9': xbmc.executebuiltin("Container.SetViewMode(560)")

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

try    : url=urllib.unquote_plus(params["url"])
except : pass
try    : name=urllib.unquote_plus(params["name"])
except : pass
try    : mode=int(params["mode"])
except : pass
try    : iconimage=urllib.unquote_plus(params["iconimage"])
except : pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)

###############################################################################################################

if   mode == None : menuPrincipal()
elif mode == 10   : getCategorias(url)
elif mode == 20   : getFilmes(url)
elif mode == 25   : getSeries(url)
elif mode == 26   : getTemporadas(url)
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
elif mode == 1000 : openConfigEI()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
