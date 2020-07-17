#####################################################################
#####################################################################
#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : Filmes e Series Online
# By AddonReneSilva - 03/05/2019
# Atualizado (1.0.0) - 03/05/2019
# Atualizado (1.0.1) - 26/05/2019
# Atualizado (1.0.2) - 05/09/2019
# Atualizado (1.0.3) - 13/10/2019
# Atualizado (1.0.4) - 13/10/2019
# Atualizado (1.0.5) - 08/02/2020
# Atualizado (1.0.6) - 27/02/2020
# Atualizado (1.0.7) - 29/05/2020
# Atualizado (1.0.8) - 10/07/2020
# Atualizado (1.0.9) - 17/07/2020
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver
import requests
import json
import resources.lib.moonwalk as moonwalk

from bs4 import BeautifulSoup
from resources.lib               import jsunpack

import socket
socket.setdefaulttimeout(60)

version      = '1.0.9'
addon_id     = 'plugin.video.gofilmes'
selfAddon    = xbmcaddon.Addon(id=addon_id)
addonfolder  = selfAddon.getAddonInfo('path')
artfolder    = addonfolder + '/resources/media/'
fanart       = addonfolder + '/resources/media/fanart.png'
addon_handle = int(sys.argv[1])
base         = base64.b64decode('aHR0cDovL2dvZmlsbWVzLm1lLw==')
sbase        = 'http://vseries.me/'

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base                              ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + '/genero/lancamentos/'     ,   20, artfolder + 'ultimos.png')
        addDir('Series'                     , sbase + '/series-hd/'             ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'            , '--'                              ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                              ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                              ,  999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo' , base                              , 1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup("div", {"class": "bgct"})
        arquivo = conteudo[0]("ul")
        categorias = arquivo[0]("li")
        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.a['title'].encode('utf-8','replace')
                titC = titC.replace('Assistir Filmes ', '').replace('Online ', '')
                titC = titC.replace('de ', '').replace('Assistir ', '')

                if not 'Lançamentos' in titC :
                    if not 'series online' in titC:
                        if not 'Filmes' in titC:
                            urlC = base + categoria.a['href']
                            imgC = "" #categoria.img["src"]
                            addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        html = openURL(url)
        soup = BeautifulSoup(html, 'html5lib')
        conteudo = soup('main',{'class':'main'})
        filmes = conteudo[0]('div',{'class':'poster'})
        totF = len(filmes)

        print totF

        for filme in filmes:
            titF = filme.a['title'].encode('utf-8').replace('Assistir ','')
            urlF = filme.a['href'].encode('utf-8')
            imgF = filme.img['data-src'].encode('utf-8')
            #xbmc.log('[plugin.video.gofilmes] L87 - ' + str(imgF), xbmc.LOGNOTICE)
            pltF = ''
            addDirF(titF, urlF, 100, imgF, False, totF, pltF)

        try :
            page = conteudo[0]('ul',{'class':'pagination'})
            pagecur = page[0]('a',{'class':'current'})
            numpage = int(pagecur[0].text)
            numpage += 1
            proxima = base+'?p='+str(numpage)
            addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
            pass

        setViewFilmes()

def getSeries(url):
        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup('div',{'class':'main'})
        filmes = conteudo[0]('div',{'class':'serie'})
        totF = len(filmes)

        for filme in filmes:
            titF = filme('div',{'class':'tt'})[0].text.encode('utf-8')
            urlF = sbase + filme.a['href'].encode('utf-8')
            imgF = filme.img['src'].encode('utf-8')
            #xbmc.log('[plugin.video.gofilmes] L116 - ' + str(urlF), xbmc.LOGNOTICE)
            addDir(titF, urlF, 26, imgF)

        try :
            page = conteudo[0]('ul',{'class':'pagination'})
            pagecur = page[0]('a',{'class':'current'})
            numpage = int(pagecur[0].text)
            numpage += 1
            proxima = sbase+'?p='+str(numpage)
            addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
            pass

        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        #setViewFilmes()

def getTemporadas(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup.find("ul", {"class": "temporadas"})
        temporadas = conteudo("li")
        totF = len(temporadas)
        img = soup.find("div", {"class": "p1"})
        urlF = url
        pltF = sinopse(urlF)
        i = 1
        while i <= totF:
            titF = str(i) + "ª Temporada"
            try:
                addDirF(titF, urlF, 27, iconimage, True, totF, pltF)
            except:
                pass
            i = i + 1

        xbmcplugin.setContent(int(sys.argv[1]), 'seasons')

def getEpisodios(name, url):
        xbmc.log('[plugin.video.gofilmes] L154 - ' + str(url), xbmc.LOGNOTICE)
        n = name.replace('ª Temporada', '')
        n = int(n)
        temp = []
        episodios = []

        html = openURL(url)
        link = unicode(html, 'utf-8', 'ignore')

        name = re.findall(r'<div class="p2">\n<h1><b>.+?</b>(.+?)<b>.+?</b></h1>\n', str(html))[0]
        soup = BeautifulSoup(html, "html5lib")
        img = soup.find("div", {"class": "p1"}).img['src']
        conteudo = soup('div',{'class':'eps'})
        xbmc.log('[plugin.video.gofilmes] L167 - ' + str(n), xbmc.LOGNOTICE)
        arquivo = conteudo[0]('div',{'class':'temp'+str(n)+'-view'})
        series = arquivo[0]('ul')

        try:
            dubs = series[0]('li')
            audio = series[0].h3.text[0]
            totF = len(dubs)
            for dub in dubs:
                titF = name + ' - '+str(n) +'x'+ dub.span.text + dub.a.text + ' ('+ audio + ')'
                titF = titF.encode('utf-8', 'ignore')
                urlF = sbase + dub.a['href']
                temp = (urlF, titF)
                episodios.append(temp)

        except:
            pass

        try:
            legs = series[1]('li')
            audio = series[1].h3.text[0]
            totF = len(legs)
            for leg in legs:
                titF = name + ' - ' +str(n) +'x'+ leg.span.text + leg.a.text + ' ('+ audio + ')'
                titF = titF.encode('utf-8', 'ignore')
                urlF = sbase + leg.a['href']
                temp = (urlF, titF)
                episodios.append(temp)

        except:
            pass

        total = len(episodios)

        for url, titulo in episodios:
                addDirF(titulo, url, 110, img, False, total)

        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.quote(texto)
                texto = str(pesquisa)
        return texto

def doPesquisaSeries():
        texto = pesquisa()
        url = sbase + 'search?q=%s' % str(texto)
        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup('div',{'class':'main'})
        filmes = conteudo[0]('div',{'class':'serie'})
        totF = len(filmes)

        hosts = []
        for filme in filmes:
            titF = filme('div',{'class':'tt'})[0].text.encode('utf-8')
            urlF = sbase + filme.a['href']
            imgF = filme.img['src']
            temp = [urlF, titF, imgF]
            hosts.append(temp)

        a = []
        for url, titulo, img in hosts:
            temp = [url, titulo, img]
            a.append(temp);
        total = len(a)

        for url2, titulo, img in a:
            addDir(titulo, url2, 26, img, False, total)
            
        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
        
def doPesquisaFilmes():
        texto = pesquisa()
        url = base + '/search.php?s=%s' % str(texto)
        html = openURL(url)
        soup = BeautifulSoup(html, 'html5lib')
        conteudo = soup('div',{'class':'main'})
        filmes = conteudo[0]('div',{'class':'poster'})
        totF = len(filmes)

        hosts = []
        for filme in filmes:
            titF = filme.a['title'].encode('utf-8')
            urlF = filme.a['href']
            imgF = filme.img['src']
            temp = [urlF, titF, imgF]
            hosts.append(temp)

        a = []
        for url, titulo, img in hosts:
            temp = [url, titulo, img]
            a.append(temp);

        total = len(a)
        for url2, titulo, img in a:
            addDirF(titulo, url2, 100, img, False, total)

        setViewFilmes()

def player(name,url,iconimage):
        xbmc.log('[plugin.video.gofilmes] L275 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('GoFilmes', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []

        link     = openURL(url)
        soup     = BeautifulSoup(link, "html5lib")
        conteudo = soup("div", {"class": "links"})
        srvsdub  = conteudo[0]('a')

        try :
            totD = len(srvsdub)
            for i in range(totD) :
                titS = srvsdub[i].text
                idS = srvsdub[i]['href']
                titsT.append(titS)
                idsT.append(idS)
        except :
            pass

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        links = conteudo[0]("a")

        if len(links) == 0 : links = conteudo[0]("a")
        i = int(index)
        urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]

        xbmc.log('[plugin.video.gofilmes] L311 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'openload' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://openload.co/embed/%s' % fxID

        elif 'ok=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://ok.ru/video/%s' % fxID

        elif 'raptu' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://www.raptu.com/?v=%s' % fxID

        elif 'vidoza' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://vidoza.net/embed-%s.html' % fxID

        elif 'vidlox' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://vidlox.tv/embed-%s' % fxID

        elif 'vcstream=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://vcstream.to/embed/%s' % fxID

        elif 'mailru=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://my.mail.ru/video/embed/%s' % fxID

        elif 'streamango=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://streamango.com/embed/%s' % fxID

        elif 'thevid' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://thevid.net/e/%s' % fxID
                linkTV  = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(linkTV)
                sUnpacked = jsunpack.unpack(aMatches[1])
                url2Play = re.findall('var ldAb="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                url2Play = 'http:%s' % url if url.startswith("//") else url
                OK = False

        elif 'gofilmes.me/play/?' in urlVideo:
                r = requests.get(urlVideo)
                html = r.content
                js = re.findall("ata\s*=\s*JSON.parse\(\'(.+)\'\);", html)[0]
                b = json.loads(js)
                url2Play = b['g']
                xbmc.log('[plugin.video.gofilmes] L365 - ' + str(url2Play), xbmc.LOGNOTICE)
                OK = False

        elif 'gofilmes.me/play/s.php' in urlVideo:
                r = requests.get(urlVideo)
                html = r.content
                #js = re.findall("ata\s*=\s*JSON.parse\(\'(.+)\'\);", html)[0]
                #b = json.loads(js)
                #url2Play = b['g']
                url2Play = re.findall('sources:\s*\[\{\'file\':\'(.+?)\',', html)[0]
                xbmc.log('[plugin.video.gofilmes] L375 - ' + str(url2Play), xbmc.LOGNOTICE)
                OK = False

        elif 'gofilmes.me/play/hd.php' in urlVideo:
                fxID = urlVideo.split('php?')[1]
                urlVideo = 'http://videoland.xyz/embed/%s' % fxID
                r = requests.get(urlVideo)
                html = r.content
                url2Play = re.findall('file\:\s*\'(.+?)\',', html)[0]
                xbmc.log('[plugin.video.gofilmes] L387 - ' + str(url2Play), xbmc.LOGNOTICE)
                OK = False

        elif 'openvid.xyz' in urlVideo:
                fxID = urlVideo.split('/v/')[1]
                urlVideo = 'https://openvid.xyz/api/source/%s' % fxID
                r = requests.post(urlVideo)
                html = r.content
                js = json.loads(html)
                s = js['data']
                qual = []
                for i in s:
                    qual.append(i['label'])
                index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)
                if index == -1 : return
                i = int(index)
                xbmc.log('[plugin.video.gofilmes] L392 - ' + str(qual[i]), xbmc.LOGNOTICE)
                url2Play = js['data'][i]['file']
                OK = False

        elif 'ruvid.nl' in urlVideo :
                fxID = urlVideo.split('v/')[-1]
                urlF = 'https://www.ruvid.nl/api/source/%s' % fxID
                data = 'r=&d=ruvid.nl'
                headers = {
                'referer': urlVideo,
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.108 Safari/537.36',
                'content-type': 'application/json',
                }
                r = requests.post(url=urlF, data=data, headers=headers)
                b = json.loads(r.text)
                url2Play = b['data'][0]['file']
                OK = False

        elif 'akugyash.com/' in urlVideo :
                okID = urlVideo.split('/')[4]
                urlVideo = 'http://akugyash.com/video/%s/iframe' % okID
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

        xbmc.log('[plugin.video.gofilmes] L436 - ' + str(urlVideo), xbmc.LOGNOTICE)

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

        listitem = xbmcgui.ListItem(name,thumbnailImage=iconimage)
        listitem.setPath(url2Play)
        listitem.setProperty('mimetype','video/mp4')
        listitem.setProperty('IsPlayable', 'true')
        playlist.add(url2Play,listitem)

        #xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
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

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.gofilmes] L472 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('GoFilmes', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []

        link = openURL(url)
        soup  = BeautifulSoup(link, "html5lib")

        try :
                conteudo = soup("div", {"class": "alinha"})
                srvsdub  = conteudo[0]("a")
                totD = len(srvsdub)
                for i in range(totD) :
                        titS = srvsdub[i].text
                        idS = srvsdub[i]["href"]
                        titsT.append(titS)
                        idsT.append(idS)
        except :
                pass

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        conteudo = soup("div", {"class": "alinha"})
        links = conteudo[0]("a")

        if len(links) == 0 : links = conteudo[0]("a")

        i = int(index)

        urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]
        
        xbmc.log('[plugin.video.gofilmes] L513 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
        '''
        if 'openload' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://openload.co/embed/%s' % fxID

        elif 'raptu.com' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://www.raptu.com/?v=%s' % fxID

        elif 'megavid' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://megavid.tv/embed-%s.html' % fxID
                linkTV  = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(linkTV)
                sUnpacked = jsunpack.unpack(aMatches[0])
                url2Play = re.findall(r'var player=new Clappr\.Player\(\{sources:\["(.*?)"\].+', sUnpacked)
                if not url2Play : url2Play = re.findall('var rick="(.*?)"', sUnpacked)
                url2Play = str(url2Play[0])
                OK = False

        elif 'vidzi' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://vidzi.tv/embed-%s.html' % fxID

        elif 'ok=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://ok.ru/video/%s' % fxID

        elif 'videoplayer=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://www.fembed.com/v/%s' % fxID

        elif 'vidoza' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://vidoza.net/embed-%s.html' % fxID

        elif 'vidlox' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://vidlox.tv/embed-%s' % fxID

        elif 'vcstream=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://vcstream.to/embed/%s' % fxID

        elif 'streamango=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://fruitstreams.com/embed/%s' % fxID

        elif 'thevid2' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://thevid.net/e/%s' % fxID
                linkTV  = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(linkTV)
                sUnpacked = jsunpack.unpack(aMatches[1])
                url2Play = re.findall('var ldAb="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                url2Play = 'http:%s' % url if url.startswith("//") else url
                OK = False

        elif 'openvid.xyz' in urlVideo:
                fxID = urlVideo.split('/v/')[1]
                urlVideo = 'https://openvid.xyz/api/source/%s' % fxID
                r = requests.post(urlVideo)
                html = r.content
                #js = re.findall("ata\s*=\s*JSON.parse\(\'(.+)\'\);", html)[0]
                js = json.loads(html)
                s = js['data']
                qual = []
                for i in s:
                    qual.append(i['label'])
                index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)
                if index == -1 : return
                i = int(index)
                xbmc.log('[plugin.video.gofilmes] L591 - ' + str(qual[i]), xbmc.LOGNOTICE)
                url2Play = js['data'][i]['file']
                OK = False

        elif 'alforenao.com/' in urlVideo :
                okID = urlVideo.split('/')[4]
                urlVideo = 'http://alforenao.com//video/%s/iframe' % okID
                xbmc.log('[plugin.video.gofilmes] L598 - ' + str(urlVideo), xbmc.LOGNOTICE)
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
        '''
        xbmc.log('[plugin.video.gofilmes] L610 - ' + str(urlVideo), xbmc.LOGNOTICE)

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
        headers = {
        "Referer": url,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
    }
        req = urllib2.Request(url, "",headers)
        req.get_method = lambda: 'GET'
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

def addDirF(name,url,mode,iconimage,pasta=True,total=1,plot='') :
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'icon': iconimage, 'thumb': iconimage })

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def getInfo(url)    :
        link = openURL(url)
        titO = re.findall('<span class="last-bread" typeof="v:Breadcrumb">(.*?)</span>', link)[0]
        titO = titO.replace('Dublado','').replace('Legendado','')

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        ytID = re.findall('<iframe width=".*?" height=".*?" src="https://www.youtube.com/embed/(.*?)rel=0&controls=0&showinfo=0" frameborder="0" allowfullscreen>.*?</iframe>', link)[0]
        ytID = ytID.replace('?','')

        xbmc.executebuiltin('XBMC.RunPlugin("plugin://plugin.video.youtube/play/?video_id=%s")' % ytID)

def setViewMenu() :
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

        opcao = selfAddon.getSetting('menuVisu')

        if   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def setViewFilmes() :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

        opcao = selfAddon.getSetting('filmesVisu')

        if   opcao ==  '0': xbmc.executebuiltin("Container.SetViewMode(50)")
        elif opcao ==  '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao ==  '2': xbmc.executebuiltin("Container.SetViewMode(500)")
        elif opcao ==  '3': xbmc.executebuiltin("Container.SetViewMode(501)")
        elif opcao ==  '4': xbmc.executebuiltin("Container.SetViewMode(502)")
        elif opcao ==  '5': xbmc.executebuiltin("Container.SetViewMode(503)")
        elif opcao ==  '6': xbmc.executebuiltin("Container.SetViewMode(508)")
        elif opcao ==  '7': xbmc.executebuiltin("Container.SetViewMode(504)")
        elif opcao ==  '8': xbmc.executebuiltin("Container.SetViewMode(503)")
        elif opcao ==  '9': xbmc.executebuiltin("Container.SetViewMode(515)")
        elif opcao == '10': xbmc.executebuiltin("Container.SetViewMode(550)")
        elif opcao == '11': xbmc.executebuiltin("Container.SetViewMode(560)")

def limpa(texto):
        texto = texto.replace('ç','c').replace('ã','a').replace('õ','o')
        texto = texto.replace('â','a').replace('ê','e').replace('ô','o')
        texto = texto.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
        texto = texto.replace(' ','-')
        texto = texto.lower()

        return texto

def sinopse(urlF):
        link = openURL(urlF)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup("div", {"class": "sinopse"})
        try:
            p = conteudo[0]
            plot = p.text.replace('kk-star-ratings','')
        except:
            plot = 'Sem Sinopse'
            pass
        return plot

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