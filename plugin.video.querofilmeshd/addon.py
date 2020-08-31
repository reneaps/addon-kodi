#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : QueroFilmesHD
# By AddonBrasil - 08/08/2020
# Atualizado (1.0.0) - 08/08/2020
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests
import resources.lib.moonwalk as moonwalk

from bs4                import BeautifulSoup
from resources.lib      import jsunpack
from time               import time

version   = '1.0.0'
addon_id  = 'plugin.video.querofilmeshd'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/fanart.png'
base        = base64.b64decode('aHR0cHM6Ly9xdWVyb2ZpbG1lc2hkLm9ubGluZS8=')

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base + ''                     ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'filme/'               ,   20, artfolder + 'lancamentos.png')
        addDir('Filmes Dublados'            , base + '?s=dublado'           ,   20, artfolder + 'pesquisa.png')
        addDir('Seriados'                   , base + 'genero/series/'       ,   25, artfolder + 'legendados.png')
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
        xbmc.log('[plugin.video.querofilmeshd] L62 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup('div',{'class':'abaViewerContainer active'})
        filmes=conteudo[0]('article',{'class':'LancasterAbasItem'})
        totF = len(filmes)

        for filme in filmes:
                a = filme('a')
                urlF = a[0]['href'].encode('utf-8')
                titF = a[1].text.encode("utf-8")
                imgF = filme.img['src'].encode('utf-8')
                if 'url=' in imgF : imgF = imgF.split('=')[3]
                imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
                pltF = titF
                addDirF(titF, urlF, 100, imgF, False, totF, pltF)

        try :
                proxima = re.findall('<link rel="next" href="(.+?)" />', link)[0]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.querofilmeshd] L89 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup('div',{'class':'abaViewerContainer active'})
        filmes=conteudo[0]('article',{'class':'LancasterAbasItem'})
        totF = len(filmes)

        for filme in filmes:
                a = filme('a')
                urlF = a[0]['href'].encode('utf-8')
                titF = a[1].text.encode("utf-8")
                imgF = filme.img['src'].encode('utf-8')
                if 'url=' in imgF : imgF = imgF.split('=')[3]
                imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
                pltF = titF
                addDirF(titF, urlF, 26, imgF, True, totF, pltF)

        try :
                proxima = re.findall('<link rel="next" href="(.+?)" />', link)[0]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        #xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        setViewFilmes()

def getTemporadas(name,url,iconimage):
        xbmc.log('[plugin.video.querofilmeshd] L117 - ' + str(url), xbmc.LOGNOTICE)
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
        xbmc.log('[plugin.video.querofilmeshd] L137 - ' + str(url), xbmc.LOGNOTICE)
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
            if 'url=' in imgF : imgF = imgF.split('=')[3]
            imgF = imgF.replace('w154', 'w300')
            imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
            imgF = base + imgF if imgF.startswith("/wp-content") else imgF
            xbmc.log('[plugin.video.querofilmeshd] L161 - ' + str(imgF), xbmc.LOGNOTICE)
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
                        if 'url=' in imgF : imgF = imgF.split('=')[3]
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
        xbmc.log('[plugin.video.querofilmeshd] L224 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('QueroFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
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
                        'Host': 'www.querofilmeshd.online',
                        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF = 'https://querofilmeshd.online/wp-admin/admin-ajax.php'
                xbmc.log('[plugin.video.querofilmeshd] L251 - ' + str(dooplay), xbmc.LOGNOTICE)
                data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.content
                try:
                    soup = BeautifulSoup(html, "html5lib")
                    urlF = soup.iframe['src']
                    urlVideo = urlF[0]
                except:
                    pass
                try:
                    b = json.loads(html)
                    urlF = str(b['embed_url'])
                    urlVideo = urlF
                except:
                    pass
                '''
                html = requests.get(urlF).content
                match = re.findall(r'{\n\t\t\t\t\t\t\tidS:\s*"(.*?)"\n\t\t\t\t\t\t}', html)
                idS = match[0]
                headers = {'Referer': urlF,
                           'Accept': '*/*',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'origin': 'https://player.querofilmeshd.online',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF = 'https://player.querofilmeshd.online/CallPlayer'
                data = urllib.urlencode({'id': idS})
                html = requests.post(url=urlF, data=data, headers=headers).content
                _html = str(html)
                b = json.loads(_html.decode('hex'))
                urlF = b['url']
                '''
                xbmc.log('[plugin.video.querofilmeshd] L285 - ' + str(urlF), xbmc.LOGNOTICE)
                urlVideo = urlF
        except:
            pass
        '''
        xbmc.log('[plugin.video.querofilmeshd] L290 - ' + str(urlF), xbmc.LOGNOTICE)
        html = openURL(urlF)
        urlVideo = urlF
        try:
            urlVideo = re.findall(r'var JWp = \{[\'"]mp4file[\'"]: [\'"](.+?)[\'"],', html)[0]
            xbmc.log('[plugin.video.querofilmeshd] L295 - ' + str(html), xbmc.LOGNOTICE)
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
            xbmc.log('[plugin.video.querofilmeshd] L308 - ' + str(url2Play), xbmc.LOGNOTICE)
        except:
            pass
        try:
            urlVideo = re.findall(r'file: "(.+?)",', html)[2]
            url2Play = urlVideo
            OK = False
            xbmc.log('[plugin.video.querofilmeshd] L315 - ' + str(url2Play), xbmc.LOGNOTICE)
        except:
            pass
        '''
        xbmc.log('[plugin.video.querofilmeshd] L319 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'video.php' in urlVideo :
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.iframe["src"]
                urlVideo = urlF
                xbmc.log('[plugin.video.querofilmeshd] L328 - ' + str(urlVideo), xbmc.LOGNOTICE)

        elif 'embed.mystream.to' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.source["src"]
                url2Play = urlF
                xbmc.log('[plugin.video.querofilmeshd] L335 - ' + str(urlVideo), xbmc.LOGNOTICE)
                OK = False

        elif 'playercdn.net' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.source["src"]
                url2Play = urlF
                xbmc.log('[plugin.video.querofilmeshd] L343- ' + str(urlVideo), xbmc.LOGNOTICE)
                OK = False

        elif 'player.querofilmeshd.online' in urlVideo:
                r = requests.get(urlVideo)
                html = r.content
                soup = BeautifulSoup(html, 'html.parser')
                match = re.findall(r'\("SvplayerID",{\n\t\t\t\t\t\t\tidS: "(.*?)"\n\t\t\t\t\t\t}\)', html)
                for x in match:
                    idsT.append(x)
                match = re.findall(r'\(SvID ==\s*(.*?)\) \{', html)
                for x in match:
                    x = 'Player ' + x
                    titsT.append(x)

                if not titsT : return

                index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                if index == -1 : return

                i = int(index)
                idS = idsT[i]

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'player.querofilmeshd.online',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                xbmc.log('[plugin.video.querofilmeshd] L374 - ' + str(idS), xbmc.LOGNOTICE)
                urlF ='https://player.querofilmeshd.online/CallPlayer'
                data = urllib.urlencode({'id': idS})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.content
                _html = str(html)
                b = json.loads(_html.decode('hex'))
                xbmc.log('[plugin.video.querofilmeshd] L381 - ' + str(_html), xbmc.LOGNOTICE)
                try:
                        urlF = b['url']
                        url2Play = urlF
                        OK = False
                except:
                        pass
                try:
                        c = b['video']
                        urlF = c['file']
                        url2Play = urlF
                        OK = False
                except:
                        pass

                xbmc.log('[plugin.video.querofilmeshd] L396 - ' + str(urlVideo), xbmc.LOGNOTICE)

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
                        xbmc.log('[plugin.video.querofilmeshd] L409 - ' + str(url2Play), xbmc.LOGNOTICE)
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
                        xbmc.log('[plugin.video.querofilmeshd] L439 - ' + str(urlVideo), xbmc.LOGNOTICE)
                        OK = True

                elif 'actelecup.com' in urlVideo :
                        xbmc.log('[plugin.video.querofilmeshd] L443 - ' + str(urlVideo), xbmc.LOGNOTICE)
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

        elif 'index.html' in urlVideo :
                host = urlVideo.split('/public')[0]
                fxID = urlVideo.split('id=')[1]
                t = int(round(time() * 1000))
                headers = {'Referer': urlVideo,
                           'Accept-Encoding': 'gzip, deflate, br',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:74.0) Gecko/20100101 Firefox/74.0',
                        }
                dados = urllib.urlencode(headers)
                urlF = host + '/playlist/' + fxID + '/' + str(t) + '.m3u8'
                r = requests.get(urlF)
                idsT = re.findall('RESOLUTION=.*?\n(.*?)\n',r.text)[0]
                #url2Play = host + idsT + '|' + dados
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

        xbmc.log('[plugin.video.querofilmeshd] L480 - ' + str(url2Play), xbmc.LOGNOTICE)

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
                listitem.setMimeType('application/x-mpegurl')
                listitem.setProperty('inputstreamaddon','inputstream.adaptive')
                listitem.setProperty('inputstream.adaptive.manifest_type','hls')
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
        xbmc.log('[plugin.video.querofilmeshd] L532 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('QueroFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []

        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        dados = soup('li',{'id':'player-option-1'})
        xbmc.log('[plugin.video.querofilmeshd] L547 - ' + str(dados), xbmc.LOGNOTICE)
        if not dados :
                dialog = xbmcgui.Dialog()
                dialog.ok(name, " ainda não liberado, aguarde... ")
                return

        dooplay = []
        dtype = dados[0]['data-type']
        dpost = dados[0]['data-post']
        dnume = dados[0]['data-nume']

        dooplay = re.findall(r'<li id=[\'"]player-option-1[\'"] class=[\'"]dooplay_player_option[\'"] data-type=[\'"](.+?)[\'"] data-post=[\'"](.+?)[\'"] data-nume=[\'"](.+?)[\'"]>', link)

        for dtype, dpost, dnume in dooplay:
            print dtype, dpost, dnume

        try:
                headers = {'Referer': url,
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'Host': 'www.querofilmeshd.online',
                        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF = 'https://querofilmeshd.online/wp-admin/admin-ajax.php'
                xbmc.log('[plugin.video.querofilmeshd] L570 - ' + str(dooplay), xbmc.LOGNOTICE)
                data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.content
                try:
                    soup = BeautifulSoup(html, "html5lib")
                    urlF = soup.iframe['src']
                    urlVideo = urlF
                except:
                    pass
                try:
                    b = json.loads(html)
                    urlF = str(b['embed_url'])
                    urlVideo = urlF
                except:
                    pass
                xbmc.log('[plugin.video.querofilmeshd] L586 - ' + str(urlVideo), xbmc.LOGNOTICE)
        except:
            pass
        try:
            b = json.loads(html)
            urlF = b['embed_url']
            html = requests.get(urlF).content
            xbmc.log('[plugin.video.querofilmeshd] L593 - ' + str(urlF), xbmc.LOGNOTICE)
            match = re.findall(r'<button class="btn btn-lg" idS="(.*?)" id=".*?" auth="0"><i id=".*?" class="glyphicon glyphicon-play-circle"></i> Iframe</button>', html)
            idS = match[0]
            xbmc.log('[plugin.video.querofilmeshd] L596 - ' + str(idS), xbmc.LOGNOTICE)
            headers = {'Referer': urlF,
                       'Accept': '*/*',
                       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                       'Host': 'player.querofilmeshd.online',
                       'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0',
                        'x-requested-with': 'XMLHttpRequest'
            }
            urlB = 'https://player.querofilmeshd.online//CallEpi'
            data = urllib.urlencode({'id': idS})
            r = requests.post(url=urlB, data=data, headers=headers)
            xbmc.log('[plugin.video.querofilmeshd] L607 - ' + str(r.text), xbmc.LOGNOTICE)
            _html = str(html)
            b = json.loads(_html.decode('hex'))
            urlF = b['url']
            xbmc.log('[plugin.video.querofilmeshd] L611 - ' + str(urlF), xbmc.LOGNOTICE)
            urlVideo = urlF
        except:
            pass

        if 'querofilmeshd.online' in urlVideo:
                r = requests.get(urlVideo)
                html = r.content
                #xbmc.log('[plugin.video.querofilmeshd] L619 - ' + str(html), xbmc.LOGNOTICE)
                soup = BeautifulSoup(html, 'html.parser')
                try:
                    match = re.findall(r'\("SvplayerID",{\n\t\t\t\t\t\t\tidS: "(.*?)"\n\t\t\t\t\t\t}\)', html)
                    for x in match:
                        idsT.append(x)
                except:
                    pass
                try:
                    match = re.findall('<button class="btn btn-lg" idS="(.*?)" id="btn-(.*?)" auth="0"><i id=".*?" class="glyphicon glyphicon-play-circle"></i> Iframe</button>', html)
                    for x,y in match:
                        y = 'Player ' + y
                        titsT.append(y)
                        idsT.append(x)
                except:
                    pass

                if not titsT : return

                index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                if index == -1 : return

                i = int(index)
                idS = idsT[i]

                headers = {'Referer': url,
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Host': 'player.querofilmeshd.online',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                urlF ='https://player.querofilmeshd.online/CallEpi'
                data = urllib.urlencode({'idS': idS})
                r = requests.post(url=urlF, data=data, headers=headers)
                xbmc.log('[plugin.video.querofilmeshd] L655 - ' + str(data), xbmc.LOGNOTICE)
                html = r.content
                _html = str(html)
                b = json.loads(_html.decode('hex'))
                try:
                        urlF = b['url']
                        url2Play = urlF
                        OK = False
                except:
                        pass
                try:
                        c = b['video']
                        urlF = c['file']
                        url2Play = urlF
                        OK = False
                except:
                        pass

                xbmc.log('[plugin.video.querofilmeshd] L673 - ' + str(urlF), xbmc.LOGNOTICE)
                '''
                idF = urlF.split('id=')[-1]
                urlF = 'https://player.filmesonlinetv.org/hls/%s/%s.m3u8' % (idF,idF)
                xbmc.log('[plugin.video.querofilmeshd] L677 - ' + str(urlF), xbmc.LOGNOTICE)
                r = requests.get(urlF)
                html = r.text
                html = html.replace('redirect/','')
                #xbmc.log('[plugin.video.querofilmeshd] L681 - ' + str(html), xbmc.LOGNOTICE)
                '''
                urlVideo = urlF
                url2Play = urlVideo
                OK = False

                xbmc.log('[plugin.video.querofilmeshd] L687 - ' + str(urlVideo), xbmc.LOGNOTICE)

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
                        xbmc.log('[plugin.video.querofilmeshd] L714 - ' + str(urlVideo), xbmc.LOGNOTICE)
                        OK = True

                        if 'alfastream.cc' in urlVideo:
                                if 'actelecup.com' in urlVideo:
                                        xbmc.log('[plugin.video.querofilmeshd] L719 - ' + str(urlVideo), xbmc.LOGNOTICE)
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

        xbmc.log('[plugin.video.querofilmeshd] L731 ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if OK : url2Play = urlresolver.resolve(urlVideo)

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
                listitem.setMimeType('application/x-mpegurl')
                listitem.setProperty('inputstreamaddon','inputstream.adaptive')
                listitem.setProperty('inputstream.adaptive.manifest_type','hls')
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
