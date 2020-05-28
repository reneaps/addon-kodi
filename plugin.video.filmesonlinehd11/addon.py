#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : FilmesOnLineHD11
# By AddonReneSilva - 02/11/2016
# Atualizado (1.0.1) - 02/11/2016
# Atualizado (1.1.0) - 04/05/2018
# Atualizado (1.1.5) - 09/10/2019
# Atualizado (1.1.6) - 09/10/2019
# Atualizado (1.1.7) - 12/01/2020
# Atualizado (1.1.8) - 03/04/2020
# Atualizado (1.1.9) - 04/04/2020
# Atualizado (1.2.0) - 28/05/2020
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver
import json
import requests
import resources.lib.moonwalk as moonwalk

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib               import jsunpack

addon_id  = 'plugin.video.filmesonlinehd11'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/img/'
fanart      = addonfolder + '/fanart.png'
base        = base64.b64decode('aHR0cHM6Ly93d3cuZmlsbWVzb25saW5laGQxMi5jYy8=')
#base        = base64.b64decode('aHR0cDovL3d3dy5maWxtZXNvbmxpbmVoZDExLmNj')
############################################################################################################

def menuPrincipal():
        addDir('Categorias'                    , base                            ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                   , base + 'lancamentos/'           ,   20, artfolder + 'new.png')
        addDir('Filmes Dublados'               , base + 'search?q=dublado'       ,   20, artfolder + 'pesquisa.png')
        addDir('Seriados'                      , base + 'series/'                ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'               , '--'                            ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'               , '--'                            ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'                 , base                            ,  999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo'    , base                            , 1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        xbmc.log('[plugin.video.filmesonlinehd11] L46 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup('div', {'class':'ui genre centered cards'})
        categorias = conteudo[0]('a')

        for categoria in categorias:
                titC = categoria.text.encode('utf-8','replace')
                urlC = categoria["href"]
                imgC = artfolder + limpa(titC) + '.png'
                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        xbmc.log('[plugin.video.filmesonlinehd11] L62 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup("div", {"class": "ui inverted raised segment"})
        if not conteudo :
            conteudo = soup("div", {"class": "ui five special doubling cards"})
        filmes   = conteudo[0]("a", {"class": "ui card"})
        if not conteudo : return

        totF = len(filmes)
        
        for filme in filmes:
                titF = filme.img["alt"].encode('utf-8').replace('Assistir ', '')
                titF = cap_name(titF)
                if not 'temporada' in titF.lower() :
                    urlF = filme["href"].encode('utf-8')
                    imgF = filme.img["data-src"].encode('utf-8')
                    addDirF(titF, urlF, 100, imgF, False, totF)

        try :
                proxima = re.findall('<a rel="next" class="item" href="(.*?)">Pr.*?<i class="angle right icon"></i></a>', link)[0]
                #getFilmes(proxima)
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.filmesonlinehd11] L92 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup.findAll("div", {"class": "ui five special doubling cards"})
        filmes   = conteudo[0]("a", {"class": "ui card"})

        for filme in filmes:
                titF = filme.img["alt"].encode('utf-8').replace('Assistir ', '').capitalize()
                urlF = filme["href"].encode('utf-8')
                imgF = filme.img["data-src"]
                addDir(titF, urlF, 26, imgF)
        try :
                proxima = re.findall('<a rel="next" class="item" href="(.*?)">Pr.+<i class="angle right icon"></i></a>', link)[0]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getTemporadas(url):
        xbmc.log('[plugin.video.filmesonlinehd11] L113 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup.findAll("div", {"class":"ui embed dimmable"})

        urlF  = conteudo[0]["data-url"]
        xbmc.log('[plugin.video.filmesonlinehd11] L120 - ' + str(urlF), xbmc.LOGNOTICE)

        img = soup.find("div", {"class": "ui embed dimmable"})
        if not img:
            img = soup.find("div", {"class": "peli"})
        imgF = re.findall(r'<div class="ui embed dimmable" data-url=".+?" data-placeholder="(.+?)" data-icon="circle play', str(img))
        imgF = imgF[0]
        imgF = imgF

        link = openURL(urlF)
        dados = {}
        dados = re.findall("links=(.*?);", link)[0]
        srvsdub = json.loads(dados)
        if 'Todas As Temporadas' in srvsdub[0]["Nome"] :
                urlF = srvsdub[0]["Url"]
                link = openURL(urlF)

        #xbmc.log('[plugin.video.filmesonlinehd11] L137 - ' + str(link), xbmc.LOGNOTICE)

        try:
            dados = {}
            dados = re.findall("links=(.*?);", link)[0]
            srvsdub = json.loads(dados)
            totF = len(srvsdub)
            for i in range(totF):
                    titF = srvsdub[i]["Nome"].encode('utf-8').capitalize()
                    urlF = srvsdub[i]["Url"]
                    addDir(titF, urlF, 28, imgF, False, totF)
        except:
            pass

        try:
            seasons = re.findall(r'seasons\: \[(.+?)\],',link)[0]
            seasons = seasons.split(",")
            totF = len(seasons)
            for i in seasons:
                    titF = i.encode('utf-8').capitalize()
                    titF = titF + "a Temporada"
                    addDir(titF, url, 28, imgF, False, totF)
        except:
            pass

def getServidores(name, url, iconimage):
        xbmc.log('[plugin.video.filmesonlinehd11] L163 - ' + str(url), xbmc.LOGNOTICE)
        imgF = iconimage
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        try:
            dados = {}
            dados = re.findall("links=(.*?);", link)[0]
            srvsdub = json.loads(dados)
            totD = len(srvsdub)
            #xbmc.log('[plugin.video.filmesonlinehd11] L172 - ' + str(dados), xbmc.LOGNOTICE)
            for i in range(totD):
                    titF = srvsdub[i]["Nome"].encode('utf-8')
                    titF = titF  if titF.startswith("Ep") else titF + " - Episodio"
                    urlF = srvsdub[i]["Url"]
                    addDirF(titF, urlF, 110, imgF, False, totD)
        except:
            pass

def getEpisodios(name, url, iconimage):
        xbmc.log('[plugin.video.filmesonlinehd11] L182 - ' + str(url), xbmc.LOGNOTICE)
        imgF = iconimage
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup     = BeautifulSoup(link)
        conteudo = soup.findAll("div", {"class":"ui embed dimmable"})

        try:
            link = openURL(urlF)
            link = unicode(link, 'utf-8', 'ignore')
            #xbmc.log('[plugin.video.filmesonlinehd11] L194 - ' + str(link), xbmc.LOGNOTICE)
        except:
            pass

        try:
            dados = {}
            dados = re.findall("links=(.*?);", link)[0]
            #xbmc.log('[plugin.video.filmesonlinehd11] L201 - ' + str(dados), xbmc.LOGNOTICE)
            srvsdub = json.loads(dados)
            Sea = srvsdub[0]["Nome"].encode('utf-8')
            Sea = Sea.lower()
            if 'temporada' in Sea or 'assistir por' in Sea: 
                    totD = len(srvsdub)
                    for i in range(totD):
                            titF = srvsdub[i]["Nome"].encode('utf-8')
                            titF = titF
                            urlF = srvsdub[i]["Url"]
                            addDir(titF, urlF, 27, imgF, False, totD)
            elif 'epis' in Sea or 'ep ' in Sea:
                totD = len(srvsdub)
                for i in range(totD):
                        titF = srvsdub[i]["Nome"].encode('utf-8')
                        titF = titF if titF.startswith("Ep") else titF + " - Episodio" 
                        urlF = srvsdub[i]["Url"]
                        addDirF(titF, urlF, 110, imgF, False, totD)
        except:
            pass
        '''
        try:
            episodes = re.findall(r'episodes\: \[(.+?)\],',link)[0]
            episodes = episodes.split(",")
            ref = re.findall(r'ref\: \'(.+?)\'',link)[0]
            #ref = re.findall(r'ref\: encodeURIComponent\(\'(.+?)\'\)',link)[0]
            serial = re.findall(r'serial_token\: \'(.+?)\'',link)[0]
            #serial = re.findall(r'video_token\: \'(.+?)\'', link)[0]
            totD = len(episodes)
            for i in episodes:
                    titF = i.encode('utf-8')
                    titF = titF + " - Episodio"
                    urlF = "https://actelecup.com/serial/%s" % serial + "/iframe?nocontrols_translations=1&ref=%s" % ref
                    addDirF(titF, urlF, 110, imgF, False, totD)
        except:
            pass
        '''

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()
        a = []
        hosts = []

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.quote(texto)
                url      = base + '/search?q=%s' % str(pesquisa)

                link  = openURL(url)
                link = unicode(link, 'utf-8', 'ignore')
                soup     = BeautifulSoup(link)
                conteudo = soup("div", {"class": "ui five special doubling cards"})
                filmes   = conteudo[0]("a", {"class": "ui card"})

                for filme in filmes:
                        titF = filme.img["alt"].encode('utf-8').replace('Assistir ', '')
                        urlF = filme["href"]
                        imgF = filme.img["data-src"]
                        temp = (urlF,titF,imgF)
                        hosts.append(temp)

                a = []
                for url, titulo, img in hosts:
                    temp = [url, titulo, img]
                    a.append(temp);
                return a
        return

def doPesquisaSeries():
        a = pesquisa()
        if not a: return
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 26, img, False, total)

def doPesquisaFilmes():
        a = pesquisa()
        if not a: return
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 100, img, False, total)

def player(name,url,iconimage):
        xbmc.log('[plugin.video.filmesonlinehd11] L284 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmesOnlineHD11', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []

        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup("div", {"class": "ui embed dimmable"})
        urlF = conteudo[0]['data-url']

        link = openURL(urlF)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        dados = {}
        dados = re.findall("links=(.*?);", link)[0]

        srvsdub = json.loads(dados)
        totD = len(srvsdub)

        for i in range(totD) :
                srv = srvsdub[i]["Nome"]
                srv = srv.replace('Assistir Por ', '').replace('Assistir por ', '')
                titsT.append(srv)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        i = index

        urlVideo = srvsdub[i]["Url"]
        print urlVideo
        xbmc.log('[plugin.video.filmesonlinehd11] L322 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'nowvideo.php' in urlVideo :
                nowID = urlVideo.split("id=")[1]
                urlVideo = 'http://embed.nowvideo.sx/embed.php?v=%s' % nowID

        elif 'mix' in urlVideo :
                data = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(data)
                sUnpacked = jsunpack.unpack(aMatches[0])
                xbmc.log('[plugin.video.overflix] L335 - ' + str(sUnpacked), xbmc.LOGNOTICE)
                url2Play = re.findall('MDCore.furl="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                url2Play = 'http:%s' % url if url.startswith("//") else url
                OK = False

        elif 'jawcloud' in urlVideo :
                headers = {'Referer': urlVideo,

                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',

                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',

                           'upgrade-insecure-requests': '1',

                           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'

                }
                r = requests.get(url=urlVideo,headers=headers)
                link = r.content
                #xbmc.log('[plugin.video.filmesonlinehd11] L355 - ' + str(link), xbmc.LOGNOTICE)
                link = unicode(link, 'utf-8', 'ignore')
                ref = re.findall(r'source src=\s*\"(.+?)\"',link)[-1]
                fxID = ref #.split(',')[-1]
                #fxID = fxID.split(']')[-1]
                url2Play = fxID
                OK = False
                xbmc.log('[plugin.video.filmesonlinehd11] L362 - ' + str(fxID), xbmc.LOGNOTICE)

        elif 'flashx.php' in urlVideo :
                fxID = urlVideo.split('id=')[1]
                urlVideo = 'http://www.flashx.tv/embed-%s.html' % fxID

        elif 'ok.ru' in urlVideo :
                okID = urlVideo.split('embed/')[1]
                urlVideo = 'https://ok.ru/videoembed/%s' % okID

        elif 'vcdn.io' in urlVideo :
                okID = urlVideo.split('v/')[1]
                urlVideo = 'https://www.fembed.com/v/%s' % okID

        elif 'woof.tube' in urlVideo:
                okID = urlVideo.split('/e/')[1]
                if '/e/' in urlVideo : 
                        fxID = urlVideo.split("/e/")[1]
                        urlVideo = 'https://verystream.com/e/%s' % fxID
                elif 'stream' in urlVideo : 
                        fxID = urlVideo.split("/stream/")[1]
                        urlVideo = 'https://verystream.com/stream/%s' % fxID

        elif 'fsst.online' in urlVideo :
                link = openURL(urlVideo)
                #xbmc.log('[plugin.video.filmesonlinehd11] L387 - ' + str(link), xbmc.LOGNOTICE)
                link = unicode(link, 'utf-8', 'ignore')
                ref = re.findall(r'file\:\s*\"(.+?)\"',link)[-1]
                fxID = ref.split(',')[-1]
                fxID = fxID.split(']')[-1]
                url2Play = fxID
                OK = False
                xbmc.log('[plugin.video.filmesonlinehd11] L394 - ' + str(fxID), xbmc.LOGNOTICE)

        elif '2actelecup.com' in urlVideo :
                okID = urlVideo.split('/')[4]
                urlVideo = 'http://actelecup.com/video/%s/iframe' % okID
                xbmc.log('[plugin.video.filmesonlinehd11] L399 - ' + str(urlVideo), xbmc.LOGNOTICE)

                link = openURL(urlVideo)
                #xbmc.log('[plugin.video.filmesonlinehd11] L402 - ' + str(link), xbmc.LOGNOTICE)
                link = unicode(link, 'utf-8', 'ignore')
                ref = re.findall(r'ref\: \'(.+?)\'',link)[0]
                #serial = re.findall(r'serial_token\: \'(.+?)\'',link)[0]
                serial = re.findall(r'video_token\: \'(.+?)\'', link)[0]
                urlR = 'https://actelecup.com/video/%s/iframe?nocontrols_translations=1&ref=%s&autoplay=1&start_time=null' % (serial, ref)
                #xbmc.log('[plugin.video.filmesonlinehd11] L408- ' + str(urlR), xbmc.LOGNOTICE)
                #urlF = 'https://actelecup.com/manifest/index.m3u8?tok=%s' % ref
                urlF = 'https://actelecup.com/manifest/mp4.json?tok=%s' % ref
                xbmc.log('[plugin.video.filmesonlinehd11] L411 - ' + str(urlF), xbmc.LOGNOTICE)
                #url  = 'https://actelecup.com/manifest/mp4.json?tok=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzb3VyY2UiOiJzZXNzaW9uIiwiZXhwIjoxNTU1NTQyOTgzLCJ2IjoiOGQ1MmJmNGQ3MTMxYTk5YyIsImEiOnRydWUsInAiOjE2ODksImgiOiI1NDE0NTNhNWQxNzEzYTY3Y2FkZjZkYWJjOWE1ZTRlYmVmMTZlZTdiYWUwMzAyN2U4YjkxNDM2OGUxNGJkN2ZmIn0.HJ1p7ZG2NdkSoyQ4vO1pICox0H4_G__rC-MJqIhHDcc'

                headers = {
                     'content-type': 'application/json; charset=utf-8',
                     'Referer': urlR,
                     'Host': 'actelecup.com',
                     'Connection': 'keep-alive',
                     'Upgrade-Insecure-Requests': '1',
                      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
                }
                r = requests.get(url=urlF, headers=headers)
                dados = {}
                dados = r.text
                js = json.loads(dados)
                #xbmc.log('[plugin.video.filmesonlinehd11] L427 - ' + str(js), xbmc.LOGNOTICE)
                qual = []
                urlVideo = []
                for i in js:
                        urlVideo.append(js[i])
                        qual.append(str(i))
                if qual == None : return
                index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)

                if index == -1 : return
                xbmc.log('[plugin.video.filmesonlinehd11] L436 - ' + str(urlVideo), xbmc.LOGNOTICE)
                i = int(qual[index])
                i = index
                #xbmc.log('[plugin.video.filmesonlinehd11] L439 - ' + str(i), xbmc.LOGNOTICE)
                url2Play = urlVideo[i]

                OK = False
                xbmc.log('[plugin.video.filmesonlinehd11] L443 - ' + str(url2Play), xbmc.LOGNOTICE)

        elif 'iframe' in urlVideo :
                #okID = urlVideo.split('/')[4]
                #urlVideo = 'https://acterbiz.com/video/%s/iframe' % okID
                #xbmc.log('[plugin.video.filmesonlinehd11] L448 - ' + str(urlVideo), xbmc.LOGNOTICE)
                urlVideo = moonwalk.get_playlist(urlVideo)
                urlVideo = urlVideo[0]
                qual = []
                for i in urlVideo:
                        qual.append(str(i))
                index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)
                if index == -1 : return
                i = int(qual[index])
                url2Play = urlVideo[i]
                OK = False
                #xbmc.log('[plugin.video.filmesonlinehd11] L459 - ' + str(urlVideo), xbmc.LOGNOTICE)

        elif 'thevid' in urlVideo :
                okID = urlVideo.split('/e/')[1]
                urlVideo = 'http://thevid.tv/e/%s' % okID


        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        if url2Play : xbmc.log('[plugin.video.filmesonlinehd11] L475 - ' + str(url2Play), xbmc.LOGNOTICE)

        if not url2Play : return

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()


        if "m3u8" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/vnd.apple.mpegurl')
                listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
                listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
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
        #return ok

def player_series(name,url,iconimage):
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmesOnlineHD11', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        xbmc.log('[plugin.video.filmesonlinehd11] L533 - ' + str(url), xbmc.LOGNOTICE)

        #link  = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        #soup = BeautifulSoup(link)
        xbmc.log('[plugin.video.filmesonlinehd11] L538 - ' + str(url), xbmc.LOGNOTICE)
        urlVideo = url

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'nowvideo.php' in urlVideo :
                nowID = urlVideo.split("id=")[1]
                urlVideo = 'http://embed.nowvideo.sx/embed.php?v=%s' % nowID

        elif 'fsst.online' in urlVideo :
                link = openURL(urlVideo)
                #xbmc.log('[plugin.video.filmesonlinehd11] L549 - ' + str(link), xbmc.LOGNOTICE)
                link = unicode(link, 'utf-8', 'ignore')
                ref = re.findall(r'file\:\s*\"(.+?)\"',link)[-1]
                fxID = ref.split(',')[-1]
                fxID = fxID.split(']')[-1]
                url2Play = fxID
                OK = False
                xbmc.log('[plugin.video.filmesonlinehd11] L556 - ' + str(fxID), xbmc.LOGNOTICE)

        elif 'video.tt' in urlVideo :
                vttID = urlVideo.split('e/')[1]
                urlVideo = 'http://www.video.tt/watch_video.php?v=%s' % vttID

        elif 'jawcloud' in urlVideo :
                headers = {'Referer': urlVideo,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'upgrade-insecure-requests': '1',
                           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
                }
                r = requests.get(url=urlVideo,headers=headers)
                link = r.content
                #xbmc.log('[plugin.video.filmesonlinehd11] L571 - ' + str(link), xbmc.LOGNOTICE)
                link = unicode(link, 'utf-8', 'ignore')
                ref = re.findall(r'source src=\s*\"(.+?)\"',link)[-1]
                fxID = ref #.split(',')[-1]
                #fxID = fxID.split(']')[-1]
                url2Play = fxID
                OK = False
                xbmc.log('[plugin.video.filmesonlinehd11] L578 - ' + str(fxID), xbmc.LOGNOTICE)

        elif 'flashx.php' in urlVideo :
                fxID = urlVideo.split('id=')[1]
                urlVideo = 'http://www.flashx.tv/playvid-%s.html' % fxID

        elif 'ok.ru' in urlVideo :
                fxID = urlVideo.split('embed')[1]
                urlVideo = 'https://ok.ru/videoembed%s' % fxID

        elif 'iframe' in urlVideo :
                okID = urlVideo.split('/')[4]
                urlVideo = 'https://acterbiz.com/video/%s/iframe' % okID
                #xbmc.log('[plugin.video.filmesonlinehd11] L582 - ' + str(urlVideo), xbmc.LOGNOTICE)
                urlVideo = moonwalk.get_playlist(urlVideo)
                #xbmc.log('[plugin.video.filmesonlinehd11] L584 - ' + str(urlVideo), xbmc.LOGNOTICE)
                urlVideo = urlVideo[0]
                qual = []
                for i in urlVideo:
                        qual.append(str(i))
                if qual == None : return
                index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)
                if index == -1 : return
                i = int(qual[index])
                url2Play = urlVideo[i]
                OK = False

        elif 'thevid.net' in urlVideo :
                linkTV  = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(linkTV)
                sUnpacked = jsunpack.unpack(aMatches[1])
                url2Play = re.findall('var vurl3="(.*?)"', sUnpacked)
                url2Play = str(url2Play[0])

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

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/vnd.apple.mpegurl')
                listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
                listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
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

        return OK

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
        req.add_header('Referer', url)
        #req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

def addDir(name, url, mode, iconimage, total=1, pasta=True):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name)

        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'icon': iconimage, 'thumb': iconimage })

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def addDirF(name,url,mode,iconimage,pasta=True,total=1) :
        u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name)

        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'icon': iconimage, 'thumb': iconimage })

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)

        return ok

def getInfo(url)    :
        link = openURL(url)
        titO = re.findall('<h1 class="ui inverted header">(.*?)</h1>', link)[0]
        xbmc.log('[plugin.video.filmesonlinehd11] L737 - ' + str(titO), xbmc.LOGNOTICE)
        titO = titO.split('-')[0]

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        soup = BeautifulSoup(link)
        y = soup("div",{"class":"socialButtons"})
        urlF = y[0]('button', {'class':'blue ui compact button'})

        a = urlF[0]['data-lity-target']
        ytID = a.split("v=")[1]
        #ytID = re.findall(r'<button title=".+?" class=".+?" data-lity="data-lity" data-lity-target="https:\/\/www.youtube.com\/watch?v=(.+?)"><i class="icon ion-ios-film"></i> <br />.+?</button>', str(link))

        if not ytID :
            addon = xbmcaddon.Addon()
            addonname = addon.getAddonInfo('name')
            line1 = str("Trailer não disponível!")
            line2 = str(ytID)
            xbmcgui.Dialog().ok(addonname, line1, line2)
            return

        #xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=youtubevideo, id=%s)' % ytID)
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play('plugin://plugin.video.youtube/play/?video_id='+ytID)

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

def cap_name(name):
        items = []
        p = ['da', 'de', 'di', 'do', 'du', 'para']
        for item in name.split():
            if not item in p:
                item = item.capitalize()
            items.append(item)
        return ' '.join(items)

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
elif mode == 27   : getServidores(name, url, iconimage)
elif mode == 28   : getEpisodios(name, url, iconimage)
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