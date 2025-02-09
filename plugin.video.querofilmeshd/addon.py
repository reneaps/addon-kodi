#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : QueroFilmesHD
# By AddonBrasil - 08/08/2020
# Atualizado (1.0.0) - 08/08/2020
# Atualizado (1.0.2) - 11/11/2020
# Atualizado (1.0.3) - 06/02/2021
# Atualizado (1.0.4) - 21/06/2021
# Atualizado (1.0.5) - 23/06/2021
# Atualizado (1.0.6) - 25/06/2021
# Atualizado (1.0.7) - 18/08/2021
# Atualizado (1.0.8) - 23/08/2021
# Atualizado (1.0.9) - 24/08/2021
# Atualizado (1.1.0) - 10/09/2021
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from urlparse           import urlparse
from bs4                import BeautifulSoup
from resources.lib      import jsunpack

version   = '1.1.0'
addon_id  = 'plugin.video.querofilmeshd'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/fanart.png'
base        = 'https://querofilmeshd.org/'

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base + ''                     ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'filme/'               ,   20, artfolder + 'lancamentos.png')
        addDir('Seriados'                   , base + 'genero/series/'       ,   25, artfolder + 'legendados.png')
        addDir('Pesquisa Series'            , '--'                          ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                          ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                          ,  999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo' , base                          , 1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo   = soup("ul",{"class":"sub-menu"})
        categorias = conteudo[0]("li")

        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.a.text
                urlC = categoria.a["href"]
                urlC = 'http:%s' % urlC if urlC.startswith("//") else urlC
                urlC = base + urlC if urlC.startswith("categoria") else urlC
                imgC = artfolder + limpa(titC) + '.png'
                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        xbmc.log('[plugin.video.querofilmeshd] L65 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html.parser")
        try:
            conteudo = soup('div',{'class':'items normal'})
            filmes=conteudo[0]('article',{'class':'item movies'})
        except:
            pass
        try:
            conteudo = soup('div',{'class':'animation-2 items normal'})
            filmes=conteudo[0]('article',{'class':'item movies'})
        except:
            pass
        totF = len(filmes)

        for filme in filmes:
                a = filme('a')
                urlF = a[0]['href']
                titF = a[1].text.encode("utf-8")
                imgF = filme.img['data-src']
                if 'url=' in imgF : imgF = imgF.split('=')[3]
                imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
                pltF = titF
                addDirF(titF, urlF, 100, imgF, False, totF)

        try :
                proxima = re.findall('<link rel="next" href="(.+?)" />', link)[0]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.querofilmeshd] L100- ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html.parser")
        try:
            conteudo = soup('div',{'class':'items normal'})
            filmes=conteudo[0]('article',{'class':'item tvshows'})
        except:
            pass
        try:
            conteudo = soup('div',{'class':'animation-2 items normal'})
            filmes=conteudo[0]('article',{'class':'item tvshows'})
        except:
            pass

        totF = len(filmes)

        for filme in filmes:
                a = filme('a')
                urlF = a[0]['href']
                titF = a[1].text.encode("utf-8")
                imgF = filme.img['data-src']
                imgF = imgF.replace('/w185/','/w300_and_h450_bestv2/')
                if 'url=' in imgF : imgF = imgF.split('=')[3]
                imgF = 'https:%s' % imgF if imgF.startswith("//") else imgF
                pltF = titF
                addDirF(titF, urlF, 26, imgF, True, totF)

        try :
                proxima = re.findall('<link rel="next" href="(.+?)" />', link)[0]
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
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.quote(texto)
                url      = base + '?s=%s' % str(pesquisa)

                xbmc.log('[plugin.video.querofilmeshd] L198 - ' + str(url), xbmc.LOGNOTICE)
                hosts = []
                temp = []
                link = openURL(url)
                soup = BeautifulSoup(link, 'html.parser')
                filmes = soup.findAll('div', {'class':'image'})
                totF = len(filmes)
                for filme in filmes:
                        titF = filme.img["alt"].encode('utf-8')
                        urlF = filme.a["href"]
                        urlF = base + urlF if urlF.startswith("/filmes") else urlF
                        urlF = base + urlF if urlF.startswith("filmes") else urlF
                        urlF = base + urlF if urlF.startswith("/series") else urlF
                        urlF = base + urlF if urlF.startswith("series") else urlF
                        urlF = base + "filmes/" + urlF if urlF.startswith("assistir") else urlF
                        imgF = filme.img["src"]
                        if 'url=' in imgF : imgF = imgF.split('=')[3]
                        imgF = imgF.replace('w92', 'w400')
                        imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
                        imgF = base + imgF if imgF.startswith("/wp-content") else imgF
                        imgF = base + imgF if imgF.startswith("wp-content") else imgF
                        temp = [urlF, titF, imgF]
                        hosts.append(temp)

                return hosts

def doPesquisaSeries():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            xbmc.log('[plugin.video.querofilmeshd] L230 - ' + str(url2), xbmc.LOGNOTICE)
            if 'tvshows' in str(url2) : 
                addDir(titulo, url2, 26, img, False, total)
            else:
                addDir(titulo, url2, 100, img, False, total)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def doPesquisaFilmes():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            if 'tvshows' in str(url2) : 
                addDir(titulo, url2, 26, img, False, total)
            else:
                addDir(titulo, url2, 100, img, False, total)

def player(name,url,iconimage):
        xbmc.log('[plugin.video.querofilmeshd] L248 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('QueroFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        sub = None


        link = openURL(url)
        dooplay = re.findall(r'<li id=[\'"]player-option-1[\'"] class=[\'"]dooplay_player_option[\'"] data-type=[\'"](.+?)[\'"] data-post=[\'"](.+?)[\'"] data-nume=[\'"](.+?)[\'"]>', link)

        for dtype, dpost, dnume in dooplay:
                print(dtype, dpost, dnume)
        try:
            p = soup('p', limit=5)[0]
            plot = p.text.replace('kk-star-ratings','')
        except:
            plot = 'Sem Sinopse'
            pass
            
        headers = {'Referer': url,
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'origin': base,
                'Connection': 'keep-alive',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
        }
        urlF = base + 'wp-admin/admin-ajax.php'
        xbmc.log('[plugin.video.querofilmeshd] L279 - ' + str(urlF), xbmc.LOGNOTICE)
        data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
        r = requests.post(url=urlF, data=data, headers=headers)
        html = r.content
        xbmc.log('[plugin.video.querofilmeshd] L283 - ' + str(html), xbmc.LOGNOTICE)
        try:
            soup = BeautifulSoup(html, "html.parser")
            urlF = soup.iframe['src']
            urlVideo = urlF[0]
        except:
            pass
        try:
            b = json.loads(html)
            urlF = str(b['embed_url'])
            urlVideo = url
        except:
            pass
        xbmc.log('[plugin.video.querofilmeshd] L297 - ' + str(urlF), xbmc.LOGNOTICE)
        if urlF != "" : html = openURL(urlF)
        #xbmc.log('[plugin.video.querofilmeshd] L299 - ' + str(html), xbmc.LOGNOTICE)
        try:
            urlF = re.findall(r"<iframe class='metaframe rptss' src='(.*?)' frameborder='0' scrolling='no' allow='autoplay; encrypted-media' allowfullscreen></iframe>", link)[0]
            html = requests.get(urlF).text
        except:
            pass
        xbmc.log('[plugin.video.querofilmeshd] L305 - ' + str(urlF), xbmc.LOGNOTICE)
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
        xbmc.log('[plugin.video.querofilmeshd] L317 - ' + str(html), xbmc.LOGNOTICE)
        _html = str(html)
        b = json.loads(_html.decode('hex'))
        xbmc.log('[plugin.video.querofilmeshd] L321 - ' + str(b), xbmc.LOGNOTICE)
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
        t = int(round(time.time() * 1000))
        urlVideo = host + '/' + idsT[i]
        urlVideo = str(urlVideo)
        if 'assistirfilmes' in str(urlVideo) : 
            urlVideo = urlVideo.replace(".m3u8", "?v=") + str(t)
        url2Play = urlVideo
        OK = False

        xbmc.log('[plugin.video.querofilmeshd] L352 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
        
        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        xbmc.log('[plugin.video.querofilmeshd] L515 - ' + str(url2Play), xbmc.LOGNOTICE)

        if not url2Play : return

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
        xbmc.log('[plugin.video.querofilmeshd] L572 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('QueroFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []
        sub = None

        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        dados = soup('li',{'id':'player-option-1'})
        xbmc.log('[plugin.video.querofilmeshd] L437 - ' + str(dados), xbmc.LOGNOTICE)
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
            print(dtype, dpost, dnume)
        if url is not None :
            d = urlparse(url)
            host = d.netloc
        headers = {"Referer": url,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                "Accept": "*/*",
                "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "X-Requested-With": "XMLHttpRequest",
                "Alt-Used": host
        }
        try:
                urlF = base + 'wp-admin/admin-ajax.php'
                #xbmc.log('[plugin.video.querofilmeshd] L470 - ' + str(urlF), xbmc.LOGNOTICE)
                data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.content
                print(html)
                xbmc.log('[plugin.video.querofilmeshd] L474 - ' + str(data)+"\n"+ str(html), xbmc.LOGNOTICE)
                try:
                    soup = BeautifulSoup(html, "html.parser")
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

                xbmc.log('[plugin.video.querofilmeshd] L488 - ' + str(urlF), xbmc.LOGNOTICE)
                if urlF != "" : html = openURL(urlF)
                #xbmc.log('[plugin.video.querofilmeshd] L490 - ' + str(link), xbmc.LOGNOTICE)
                try:
                    urlF = re.findall(r"<iframe class='metaframe rptss' src='(.*?)' frameborder='0' scrolling='no' allow='autoplay; encrypted-media' allowfullscreen></iframe>", link)[0]
                    xbmc.log('[plugin.video.querofilmeshd] L493 - ' + str(urlF), xbmc.LOGNOTICE)
                    html = requests.get(urlF).text
                except:
                    pass
                xbmc.log('[plugin.video.querofilmeshd] L496 - ' + str(urlF), xbmc.LOGNOTICE)
                idS = re.findall(r'idS[=:]\s*"(.*?)"', html)[0]
                if idS is not None :
                    d = urlparse(urlF)
                    host = d.netloc
                headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Connection': 'keep-alive',
                           'Host': host,
                           'Upgrade-Insecure-Requests': '1',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                if 'querofilmeshd' in urlF : urlF = base + 'CallPlayer'
                elif 'uauflix' in urlF : urlF = 'https://player.uauflix.online//CallEpi'
                data = urllib.urlencode({'idS': idS})
                html = requests.post(url=urlF, data=data, headers=headers).text
                xbmc.log('[plugin.video.querofilmeshd] L508 - ' + str(data), xbmc.LOGNOTICE)
                _html = str(html)
                b = json.loads(_html.decode('hex'))
                xbmc.log('[plugin.video.querofilmeshd] L512 - ' + str(b), xbmc.LOGNOTICE)
                urlF = b['url']
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

                xbmc.log('[plugin.video.querofilmeshd] L539 - ' + str(urlVideo), xbmc.LOGNOTICE)
        except:
            pass

        xbmc.log('[plugin.video.querofilmeshd] L543 ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if OK : url2Play = urlresolver.resolve(urlVideo)

        if not url2Play : return

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
        req.add_header('Referer', base)
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
