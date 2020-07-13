#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : MidiaFlixHD
# By AddonBrasil - 11/12/2015
# Atualizado (1.0.0) - 29/06/2018
# Atualizado (1.0.1) - 22/07/2018
# Atualizado (1.0.2) - 23/04/2019
# Atualizado (1.0.3) - 07/05/2019
# Atualizado (1.0.4) - 13/05/2019
# Atualizado (1.0.5) - 03/08/2019
# Atualizado (1.0.6) - 18/03/2020
# Atualizado (1.0.7) - 30/03/2020
# Atualizado (1.0.8) - 31/03/2020
# Atualizado (1.0.9) - 05/04/2020
# Atualizado (1.1.0) - 11/07/2020
# Atualizado (1.1.1) - 13/07/2020
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests
import resources.lib.moonwalk as moonwalk

from bs4 import BeautifulSoup
#from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib               import jsunpack
from time                        import time

version   = '1.1.1'
addon_id  = 'plugin.video.midiaflixhd'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/fanart.png'
base        = base64.b64decode('aHR0cHM6Ly93d3cubWlkaWFmbGl4aGQubmV0Lw==')

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base + ''                     ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'filmes/'              ,   20, artfolder + 'lancamentos.png')
        addDir('Filmes Dublados'            , base + '?s=dublado'           ,   20, artfolder + 'pesquisa.png')
        addDir('Seriados'                   , base + 'series/'              ,   25, artfolder + 'legendados.png')
        addDir('Pesquisa Series'            , '--'                          ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                          ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                          ,  999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo' , base                          , 1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo   = soup("ul",{"class":"sub-menu"})
        categorias = conteudo[0]("li")

        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.a.text.encode('utf-8','')
                urlC = categoria.a["href"]
                urlC = 'http:%s' % urlC if urlC.startswith("//") else urlC
                urlC = base + urlC if urlC.startswith("categoria") else urlC
                imgC = artfolder + limpa(titC) + '.png'
                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        xbmc.log('[plugin.video.midiaflixhd] L74 ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        try:
                conteudo = soup("div",{"class":"animation-2 items"})
                filmes = conteudo[0]('div',{'class':'poster'})
        except:
                filmes = soup("article",{"class":"item movies"})
                #filmes = conteudo[0]('div',{'class':'poster'})
                dtinfo = soup.findAll('div', {'class':'animation-1 dtinfo'})
                texto = dtinfo[0]('div', {'class':'texto'})
                pass
        i = 0
        totF = len(filmes)

        for filme in filmes:
                titF = filme.img["alt"].encode("utf-8")
                urlF = filme.a["href"].encode('utf-8')
                urlF = base + urlF if urlF.startswith("/filmes") else urlF
                urlF = base + "filmes/" + urlF if urlF.startswith("assistir") else urlF
                imgF = filme.img["src"].encode('utf-8')
                imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
                imgF = base + imgF if imgF.startswith("/wp-content") else imgF
                imgF = base + imgF if imgF.startswith("wp-content") else imgF
                try:
                    texto = dtinfo[i]('div', {'class':'texto'})
                    pltF = texto[0].text #sinopse(urlF)
                except:
                    pltF = ""
                    pass
                i = i + 1
                addDirF(titF, urlF, 100, imgF, False, totF, pltF)

        try :
                proxima = re.findall('<link rel="next" href="(.+?)">', link)[0]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup("div",{"id":"archive-content"})
        filmes = conteudo[0]('div',{'class':'poster'})
        dtinfo = soup.findAll('div', {'class':'animation-1 dtinfo'})
        texto = dtinfo[0]('div', {'class':'texto'})

        i = 0
        totF = len(filmes)

        for filme in filmes:
                titF = filme.img["alt"].encode("utf-8")
                titF = titF.replace('assistir','').replace('online','')
                titF = titF.replace('Assistir','').replace('Online','')
                titF = titF.replace('á','a')
                urlF = filme.a["href"].encode('utf-8')
                urlF = base + urlF if urlF.startswith("/series") else urlF
                urlF = base + "series/" + urlF if urlF.startswith("assistir") else urlF
                imgF = filme.img["src"].encode("utf-8")
                imgF = imgF.replace('w185', 'w300')
                imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
                imgF = base + imgF if imgF.startswith("/wp-content") else imgF
                texto = dtinfo[i]('div', {'class':'texto'})
                pltF = texto[0].text #sinopse(urlF)
                i = i + 1
                addDirF(titF, urlF, 26, imgF, True, totF, pltF)

        try :
                proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        #xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        setViewFilmes()

def getTemporadas(name,url,iconimage):
        xbmc.log('[plugin.video.midiaflixhd] L155 ' + str(url), xbmc.LOGNOTICE)
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
        xbmc.log('[plugin.video.midiaflixhd] L175 ' + str(url), xbmc.LOGNOTICE)
        n = name.replace('ª Temporada', '')
        n = int(n)
        n = (n-1)
        temp = []
        episodios = []

        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', {'class':'se-c'})
        episodes = conteudo[n]('ul', {'class':'episodios'})
        itens = episodes[0]('li')

        totF = len(itens)

        for i in itens:
            urlF = i.a['href']
            #if not url in urlF : urlF = base + urlF
            imgF = i.img['src']
            imgF = imgF.replace('w154', 'w300')
            imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
            imgF = base + imgF if imgF.startswith("/wp-content") else imgF
            xbmc.log('[plugin.video.midiaflixhd] L198 - ' + str(imgF), xbmc.LOGNOTICE)
            titA = i(class_='numerando')[0].text.encode('utf-8').replace('-','x')
            titB = i(class_='episodiotitle')[0].a.text.encode('utf-8')
            titF = titA + ' - ' + titB
            addDirF(titF, urlF, 110, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.quote(texto)
                url      = base + '?s=%s' % str(pesquisa)

                hosts = []
                link = openURL(url)
                link = unicode(link, 'utf-8', 'ignore')
                soup = BeautifulSoup(link, 'html.parser')
                filmes = soup.findAll('div', {'class':'image'})
                totF = len(filmes)
                for filme in filmes:
                        titF = filme.img["alt"].encode('utf-8')
                        urlF = filme.a["href"].encode('utf-8')
                        urlF = base + urlF if urlF.startswith("/filmes") else urlF
                        urlF = base + urlF if urlF.startswith("filmes") else urlF
                        urlF = base + urlF if urlF.startswith("/series") else urlF
                        urlF = base + urlF if urlF.startswith("series") else urlF
                        urlF = base + "filmes/" + urlF if urlF.startswith("assistir") else urlF
                        imgF = filme.img["src"].encode('utf-8')
                        imgF = imgF.replace('w92', 'w400')
                        imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
                        imgF = base + imgF if imgF.startswith("/wp-content") else imgF
                        imgF = base + imgF if imgF.startswith("wp-content") else imgF
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
            addDir(titulo, url2, 26, img, False, total)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def doPesquisaFilmes():
        a = pesquisa()
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 100, img, False, total)
        setViewFilmes()

def player(name,url,iconimage):
        xbmc.log('[plugin.video.midiaflixhd] L260 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MidiaFlixHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []

        link = openURL(url)
        dooplay = re.findall(r'<li id=[\'"]player-option-1[\'"] class=[\'"]dooplay_player_option[\'"] data-type=[\'"](.+?)[\'"] data-post=[\'"](.+?)[\'"] data-nume=[\'"](.+?)[\'"]>', link)

        for dtype, dpost, dnume in dooplay:
                print dtype, dpost, dnume
        try:
            p = soup('p', limit=5)[0]
            plot = p.text.replace('kk-star-ratings','')
        except:
            plot = 'Sem Sinopse'
            pass
        try:
                headers = {'Referer': url,
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Host': 'www.midiaflixhd.net',
                        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF = 'https://www.midiaflixhd.net/wp-admin/admin-ajax.php'
                xbmc.log('[plugin.video.midiaflixhd] L287 - ' + str(dooplay), xbmc.LOGNOTICE)
                data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.content
                xbmc.log('[plugin.video.midiaflixhd] L291 - ' + str(html), xbmc.LOGNOTICE)
        except:
            pass

        try:
            soup = BeautifulSoup(html, 'html.parser')
            urlF = soup.iframe['src']
        except:
            urlF = soup.a['href']
            fxID = urlF.split('l=')[1]
            urlF = base64.b64decode(fxID)
            xbmc.log('[plugin.video.midiaflixhd] L302 - ' + str(urlF), xbmc.LOGNOTICE)
            pass

        xbmc.log('[plugin.video.midiaflixhd] L305 - ' + str(urlF), xbmc.LOGNOTICE)
        html = openURL(urlF)
        urlVideo = urlF
        try:
            urlVideo = re.findall(r'var JWp = \{[\'"]mp4file[\'"]: [\'"](.+?)[\'"],', html)[0]
            xbmc.log('[plugin.video.midiaflixhd] L310 - ' + str(html), xbmc.LOGNOTICE)
            url2Play = urlVideo
            OK = False
            print urlVideo
        except:
            pass
        try:
            urlVideo = re.findall("addiframe\('(.*?)'\);", html)[0]
            html = openURL(urlVideo)
            url2Play = re.findall(r'\[\{\"type\": "video/mp4", \"label\": "HD", \"file\": "(.+?)"\}\],', html)[0]
            r = urllib2.urlopen(url2Play)
            url2Play = r.geturl()
            OK = False
            xbmc.log('[plugin.video.midiaflixhd] L323 - ' + str(url2Play), xbmc.LOGNOTICE)
        except:
            pass
        try:
            urlVideo = re.findall(r'file: "(.+?)",', html)[2]
            url2Play = urlVideo
            OK = False
            xbmc.log('[plugin.video.midiaflixhd] L330 - ' + str(url2Play), xbmc.LOGNOTICE)
        except:
            pass

        xbmc.log('[plugin.video.midiaflixhd] L334 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'video.php' in urlVideo :
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.iframe["src"]
                urlVideo = urlF
                xbmc.log('[plugin.video.midiaflixhd] L343 - ' + str(urlVideo), xbmc.LOGNOTICE)

        elif 'embed.mystream.to' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.source["src"]
                url2Play = urlF
                xbmc.log('[plugin.video.midiaflixhd] L350 - ' + str(urlVideo), xbmc.LOGNOTICE)
                OK = False

        elif 'playercdn.net' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.source["src"]
                url2Play = urlF
                xbmc.log('[plugin.video.midiaflixhd] L358 - ' + str(urlVideo), xbmc.LOGNOTICE)
                OK = False

        elif 'play.midiaflixhd.com' in urlVideo:
                r = requests.get(urlVideo)
                html = r.content
                soup = BeautifulSoup(html, 'html.parser')
                match = re.findall('\tidS:\s*"(.+?)"\r', html)
                for x in match:
                    idsT.append(x)
                match = re.findall('\t<button id="Servidores" class="button-xlarge pure-button" svid=".+?">(.+?)</button>\r', html)
                for x in match:
                    titsT.append(x)

                if not titsT : return

                index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                if index == -1 : return

                i = int(index)
                idS = idsT[i]

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'play.midiaflixhd.com',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF ='https://play.midiaflixhd.com/CallPlayer'
                data = urllib.urlencode({'id': idS})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.content
                _html = str(html)
                b = json.loads(_html.decode('hex'))
                try:
                        urlF = b['url']
                        urlVideo = urlF
                except:
                        c = b['video'][0]
                        urlF = c['file']
                        url2Play = urlF
                        OK = False
                        pass
                
                xbmc.log('[plugin.video.midiaflixhd] L404 - ' + str(urlVideo), xbmc.LOGNOTICE)

                if 'letsupload.co' in urlVideo:
                        nowID = urlVideo.split("=")[1]
                        urlVideo = "https://letsupload.co/plugins/mediaplayer/site/_embed.php?u=%s" % nowID
                        r = requests.get(urlVideo)
                        url2Play = re.findall(r'file: "(.+?)",', r.text)[0]
                        OK = False

                elif 'embed.mystream.to' in urlVideo:
                        html = openURL(urlVideo)
                        e = re.findall('<meta name="twitter:image" content="(.+?)">', html)[0]
                        url2Play = e.replace('/img', '').replace('jpg','mp4')
                        xbmc.log('[plugin.video.midiaflixhd] L417 - ' + str(url2Play), xbmc.LOGNOTICE)
                        OK = False

                elif 'gofilmes.me' in urlVideo:
                        headers = {
                                'Referer': urlVideo,
                                'authority': 'gofilmes.me',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                        }
                        r = requests.get(url=urlVideo, headers=headers)
                        e = re.findall('sources:\s*\[\{[\'"]file[\'"]:[\'"](.+?)[\'"], type:[\'"]mp4[\'"], default:[\'"]true[\'"]\}\],', r.content)[0]
                        url2Play = e #+ '%7C' + urllib.urlencode(headers)       
                        OK = False

                elif '4toshare' in urlVideo :
                        r = requests.get(urlVideo)
                        e = re.findall('{src:\s*"(.+?)", type: "(.+?)", res:\s*.+?, label: "(.+?)"}', r.text)
                        headers = {
                                'Referer': urlVideo,
                                'Host': 's2.4toshare.com',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
            }
                        url2Play = e[0][0] + '%7C' + urllib.urlencode(headers)
                        OK = False

                elif 'video.php' in urlVideo :
                        fxID = urlVideo.split('u=')[1]
                        urlVideo = base64.b64decode(fxID)
                        xbmc.log('[plugin.video.midiaflixhd] L447 - ' + str(urlVideo), xbmc.LOGNOTICE)
                        OK = True

                elif 'actelecup.com' in urlVideo :
                        xbmc.log('[plugin.video.midiaflixhd] L451 - ' + str(urlVideo), xbmc.LOGNOTICE)
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

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        xbmc.log('[plugin.video.midiaflixhd] L472 - ' + str(url2Play), xbmc.LOGNOTICE)

        if not url2Play : return

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        listitem = xbmcgui.ListItem(name,thumbnailImage=iconimage)
        listitem.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
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


def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.midiaflixhd] L511 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MidiaFlixHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []

        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        dados = soup('li',{'id':'player-option-1'})
        xbmc.log('[plugin.video.midiaflixhd] L526 - ' + str(dados), xbmc.LOGNOTICE)
        if not dados :
                dialog = xbmcgui.Dialog()
                dialog.ok(name, " ainda não liberado, aguarde... ")
                return 
                
        dooplay = []
        dtype = dados[0]['data-type']
        dpost = dados[0]['data-post']
        dnume = dados[0]['data-nume']
        #dooplay = re.findall(r'<li id=[\'"]player-option-1[\'"] class=[\'"]dooplay_player_option.+?[\'"] data-type=[\'"](.+?)[\'"] data-post=[\'"](.+?)[\'"] data-nume=[\'"](.+?)[\'"]>', link)
        #try:
        #for dtype, dpost, dnume in dooplay:
                #print dtype, dpost, dnume
        headers = {'Referer': url,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Host': 'www.midiaflixhd.net',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
        }
        urlF = 'https://www.midiaflixhd.net/wp-admin/admin-ajax.php'
        data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
        xbmc.log('[plugin.video.midiaflixhd] L547 - ' + str(data), xbmc.LOGNOTICE)
        r = requests.post(url=urlF, data=data, headers=headers)
        html = r.content
        soup = BeautifulSoup(html, 'html.parser')
        try:
            urlF = soup.iframe['src']
            xbmc.log('[plugin.video.midiaflixhd] L553 - ' + str(urlF), xbmc.LOGNOTICE)
        except:
            urlF = soup.a['href']
            fxID = urlF.split('l=')[1]
            urlF2 = base64.b64decode(fxID)
            xbmc.log('[plugin.video.midiaflixhd] L558 - ' + str(urlF2), xbmc.LOGNOTICE)
            pass

        urlVideo = urlF2

        if 'play.midiaflixhd.com' in urlVideo:
                html = requests.get(urlVideo).text
                match = re.findall('idS="(.+?)"', html)
                for x in match:
                    idsT.append(x)
                match = re.findall('<button class="btn btn-l.+?" idS=".+?" id="btn-(.+?)"><i id="icon-0" class="glyphicon glyphicon-play-circle"></i> Others</button>', html)
                for x in match:
                        titsT.append(x)

                if not titsT : return

                index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                if index == -1 : return

                i = int(index)
                idS = idsT[i]

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'play.midiaflixhd.com',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF ='https://play.midiaflixhd.com/CallEpi'
                data = urllib.urlencode({'idS': idS})
                r = requests.post(url=urlF, data=data, headers=headers)
                xbmc.log('[plugin.video.midiaflixhd] L591 - ' + str(data), xbmc.LOGNOTICE)

                xbmc.log('[plugin.video.midiaflixhd] L593 - ' + str(r.text), xbmc.LOGNOTICE)

                html = r.content
                _html = str(html)
                b = json.loads(_html.decode('hex'))
                c = b['video']
                urlF = c[0]['file']
                urlVideo = urlF

                xbmc.log('[plugin.video.midiaflixhd] L602 - ' + str(urlVideo), xbmc.LOGNOTICE)

                if 'letsupload.co' in urlVideo:
                        nowID = urlVideo.split("=")[1]
                        urlVideo = "https://letsupload.co/plugins/mediaplayer/site/_embed.php?u=%s" % nowID
                        r = requests.get(urlVideo)
                        url2Play = re.findall(r'file: "(.+?)",', r.text)[0]
                        OK = False
                
                if 'videok7.online' in urlVideo :
                        url2Play = urlVideo
                        OK = False
                
                if 'saborcaseiro' in urlVideo :
                        url2Play = urlVideo
                        OK = False
                
                if 'apiblogger.xyz' in urlVideo :
                        headers = {'Referer': urlF2,
                                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                        }
                        url2Play = urlVideo + "|" + urllib.urlencode(headers)
                        OK = False

                elif 'video.php' in urlVideo :
                        fxID = urlVideo.split('=')[1]
                        urlVideo = base64.b64decode(fxID)
                        xbmc.log('[plugin.video.midiaflixhd] L629 - ' + str(urlVideo), xbmc.LOGNOTICE)
                        OK = True

                        if 'alfastream.cc' in urlVideo:
                                if 'actelecup.com' in urlVideo:
                                        xbmc.log('[plugin.video.midiaflixhd] L634 - ' + str(urlVideo), xbmc.LOGNOTICE)
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

        xbmc.log('[plugin.video.midiaflixhd] L646 ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if OK : url2Play = urlresolver.resolve(urlVideo)

        if not url2Play : return

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        listitem = xbmcgui.ListItem(name, thumbnailImage=iconimage)
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

def addDirF(name,url,mode,iconimage,pasta=True,total=1,plot='') :
        u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name, iconImage="iconimage", thumbnailImage=iconimage)

        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)

        return ok

def getInfo(url):
        link = openURL(url)
        titO = re.findall('<meta property="og:title" content="(.*?)" />', link)[0]

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        #ytID = re.findall('<a id="open-trailer" class="btn iconized trailer" data-trailer="https://www.youtube.com/embed/(.*?)rel=0&amp;controls=1&amp;showinfo=0&autoplay=0"><b>Trailler</b> <i class="icon fa fa-play"></i></a>', link)[0]
        ytID = '' #SytID.replace('?','')

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
        soup = BeautifulSoup(link, 'html.parser')
        #conteudo = soup("div", {"id": "info"})
        try:
            p = soup('p', limit=5)[0]
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
elif mode == 1000 : openConfigEI()

xbmcplugin.endOfDirectory(int(sys.argv[1]))
