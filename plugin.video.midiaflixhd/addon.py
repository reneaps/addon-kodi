#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : MidiaFlixHD
# By AddonBrasil - 11/12/2015
# Atualizado (1.0.0) - 29/06/2018
# Atualizado (1.0.6) - 18/03/2020
# Atualizado (1.0.7) - 30/03/2020
# Atualizado (1.0.8) - 31/03/2020
# Atualizado (1.0.9) - 05/04/2020
# Atualizado (1.1.0) - 11/07/2020
# Atualizado (1.1.1) - 13/07/2020
# Atualizado (1.1.2) - 29/08/2020
# Atualizado (1.1.3) - 23/07/2021
# Atualizado (1.1.4) - 10/09/2021
# Atualizado (1.1.5) - 22/09/2021
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests
import resources.lib.moonwalk as moonwalk

from bs4                import BeautifulSoup
from urlparse           import urlparse
from resources.lib      import jsunpack

version   = '1.1.5'
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
        xbmc.log('[plugin.video.midiaflixhd] L71 ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        try:
            conteudo = soup('div', attrs={'class':'animation-2 items full'})
            filmes = conteudo[0]('article')
        except:
            pass
        try:
            conteudo = soup('div', attrs={'class':'items full'})
            filmes = conteudo[0]('article')
        except:
            pass
        i = 0
        totF = len(filmes)

        for filme in filmes:
                titF = filme.img["alt"].encode("utf-8")
                urlF = filme.a["href"]
                urlF = base + urlF if urlF.startswith("/filmes") else urlF
                urlF = base + "filmes/" + urlF if urlF.startswith("assistir") else urlF
                imgF = filme.img["data-src"]
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
                proxima = re.findall('<link rel="next" href="(.*?)"\s*/>', link)[0]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', attrs={'class':'animation-2 items full'})
        filmes = conteudo[0]('article')
        i = 0
        totF = len(filmes)

        for filme in filmes:
                urlF = filme.select('.poster')[0].a['href']
                imgF = filme.select('.poster')[0].img['data-src']
                titF = filme.select('.poster')[0].img['alt'].encode('utf-8')
                try:
                    texto = dtinfo[i]('div', {'class':'texto'})
                    pltF = texto[0].text #sinopse(urlF)
                except:
                    pltF = ""
                    pass
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
        xbmc.log('[plugin.video.midiaflixhd] L146 ' + str(url), xbmc.LOGNOTICE)
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
        xbmc.log('[plugin.video.midiaflixhd] L166 ' + str(url), xbmc.LOGNOTICE)
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
            xbmc.log('[plugin.video.midiaflixhd] L189 - ' + str(imgF), xbmc.LOGNOTICE)
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
        xbmc.log('[plugin.video.midiaflixhd] L251 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MidiaFlixHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        sub = None

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
                xbmc.log('[plugin.video.midiaflixhd] L279 - ' + str(dooplay), xbmc.LOGNOTICE)
                data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
                r = requests.post(url=urlF, data=data, headers=headers)
                html = r.content
                xbmc.log('[plugin.video.midiaflixhd] L283 - ' + str(html), xbmc.LOGNOTICE)
        except:
            pass

        try:
            soup = BeautifulSoup(link, 'html.parser')
            urlF = soup.iframe['src']
        except:
            pass

        try:
            urlF = soup.a['href']
            fxID = urlF.split('l=')[1]
            urlF = base64.b64decode(fxID)
            xbmc.log('[plugin.video.midiaflixhd] L297 - ' + str(urlF), xbmc.LOGNOTICE)
        except:
            pass

        try:
            b = json.loads(html)
            urlF = str(b['embed_url'])
            #urlVideo = urlF
        except:
            pass

        try:
            soup = BeautifulSoup(link, 'html.parser')
            conteudo = soup.select('.source-box')
            #print(link)
            for i in conteudo:
                if 'auth' in str(i) :
                    uri = i.a['href']
                    uri = uri.split('auth=')[-1]
                    urlF = base64.b64decode(uri)
                    b = json.loads(urlF)
                    urlF = b['url']
                    print(urlF)
        except:
            pass

        xbmc.log('[plugin.video.midiaflixhd] L323 - ' + str(urlF), xbmc.LOGNOTICE)
        html = openURL(urlF)
        urlVideo = urlF
        try:
            urlVideo = re.findall(r'var JWp = \{[\'"]mp4file[\'"]: [\'"](.+?)[\'"],', html)[0]
            xbmc.log('[plugin.video.midiaflixhd] L328 - ' + str(html), xbmc.LOGNOTICE)
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
            xbmc.log('[plugin.video.midiaflixhd] L341 - ' + str(url2Play), xbmc.LOGNOTICE)
        except:
            pass
        try:
            urlVideo = re.findall(r'file: "(.+?)",', html)[2]
            url2Play = urlVideo
            OK = False
            xbmc.log('[plugin.video.midiaflixhd] L348 - ' + str(url2Play), xbmc.LOGNOTICE)
        except:
            pass

        xbmc.log('[plugin.video.midiaflixhd] L352 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'video.php' in urlVideo :
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.iframe["src"]
                urlVideo = urlF
                xbmc.log('[plugin.video.midiaflixhd] L361 - ' + str(urlVideo), xbmc.LOGNOTICE)

        elif 'embed.mystream.to' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.source["src"]
                url2Play = urlF
                xbmc.log('[plugin.video.midiaflixhd] L368 - ' + str(urlVideo), xbmc.LOGNOTICE)
                OK = False

        elif 'playercdn.net' in urlVideo:
                html = openURL(urlVideo)
                soup = BeautifulSoup(html, 'html.parser')
                urlF = soup.source["src"]
                url2Play = urlF
                xbmc.log('[plugin.video.midiaflixhd] L376 - ' + str(urlVideo), xbmc.LOGNOTICE)
                OK = False

        elif 'play.midiaflixhd.com' in urlVideo:
                r = requests.get(urlVideo)
                html = r.content
                soup = BeautifulSoup(html, 'html.parser')
                #xbmc.log('[plugin.video.midiaflixhd] L383 - ' + str(html), xbmc.LOGNOTICE)
                match = re.findall(r'\("SvplayerID",{\r\n\t\t\t\t\t\t\tidS: "(.*?)"\r\n\t\t\t\t\t\t}\);', html)
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
                        sub = b['subtitle']
                        url2Play = urlF
                        OK = False
                        pass

                xbmc.log('[plugin.video.midiaflixhd] L424 - ' + str(urlVideo), xbmc.LOGNOTICE)

                if 'letsupload.co' in urlVideo:
                        nowID = urlVideo.split("=")[1]
                        urlVideo = "https://letsupload.co/plugins/mediaplayer/site/_embed.php?u=%s" % nowID
                        r = requests.get(urlVideo)
                        url2Play = re.findall(r'file: "(.+?)",', r.text)[0]
                        OK = False

                elif 'evoload' in urlVideo:
                        code = urlVideo.split('e/')[-1]
                        urlC = 'https://csrv.evosrv.com/captcha?m412548'
                        captcha = openURL(urlC)
                        urlF = 'https://evoload.io/SecurePlayer'
                        data = {"code":code,"token":"ok","csrv_token":captcha,"pass":"7dczpuzsmak","reff":""}
                        headers = {
                                "referrer": urlVideo,
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                                "Accept": "application/json, text/plain, */*",
                                "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                                "Content-Type": "application/json;charset=utf-8",
                                "X-XSRF-TOKEN": ""
                            }
                        link = requests.post(url=urlF, data=json.dumps(data), headers=headers)
                        r = json.loads(link.text).get('stream')
                        urlF = r.get('backup') if r.get('backup') else r.get('src')
                        url2Play = urlF
                        xbmc.log('[plugin.video.midiaflixhd] L451 - ' + str(url2Play), xbmc.LOGNOTICE)
                        OK = False

                elif 'gdriveplayer.to' in urlVideo:
                        urlVideo = 'https:%s' % urlVideo if urlVideo.startswith("//") else urlVideo
                        url2Play = urlVideo
                        OK = False

                elif 'superflix' in urlVideo:
                        url2Play = urlF
                        OK = False

                elif 'embed.mystream.to' in urlVideo:
                        html = openURL(urlVideo)
                        e = re.findall('<meta name="twitter:image" content="(.+?)">', html)[0]
                        url2Play = e.replace('/img', '').replace('jpg','mp4')
                        xbmc.log('[plugin.video.midiaflixhd] L467 - ' + str(url2Play), xbmc.LOGNOTICE)
                        OK = False

                elif 'gofilmes.me' in urlVideo:
                        headers = {
                                'Referer': urlVideo,
                                'authority': 'gofilmes.me',
                                'Upgrade-Insecure-Requests': '1',
                                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                        }
                        r = requests.get(url=urlVideo, headers=headers)
                        e = re.findall('var \$data = JSON.parse\(\'(.*?)\'\);', r.text)
                        if len(e) > 0 :
                            b = json.loads(e[0])
                            xbmc.log('[plugin.video.midiaflixhd] L481 - ' + str(b['g']), xbmc.LOGINFO)
                            f = b['g']
                        else:
                            e = re.findall('sources:\s*\[\{[\'"]file[\'"]:[\'"](.+?)[\'"], type:[\'"]mp4[\'"], default:[\'"]true[\'"]\}\],', r.text)
                        if len(e) == 0 :
                            xbmc.log('[plugin.video.midiaflixhd] L486 - ' + str(r.text), xbmc.LOGINFO)
                            f = re.findall(r'<source src="(.*?)" size="720" />', r.text)
                            url2Play = f[0]
                        else:
                            url2Play = f #+ '%7C' + urllib.urlencode(headers)
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
                        xbmc.log('[plugin.video.midiaflixhd] L508 - ' + str(urlVideo), xbmc.LOGNOTICE)
                        OK = True

                elif 'actelecup.com' in urlVideo :
                        xbmc.log('[plugin.video.midiaflixhd] L512 - ' + str(urlVideo), xbmc.LOGNOTICE)
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
                        urlF = urlVideo
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
                        xbmc.log('[plugin.video.midiaflixhd] L536 - ' + str(urlF), xbmc.LOGNOTICE)

                        r = requests.get(url=urlF)
                        titsT = re.findall('RESOLUTION=(.*?)\n/hls.+', r.text)
                        idsT = re.findall('RESOLUTION=.*?\n/(.*?)\n', r.text)

                        if not titsT : return

                        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

                        if index == -1 : return
                        i = index
                        urlVideo = host + '/' + idsT[i]
                        url2Play = urlVideo
                        OK = False

                elif 'mrdhan.com' in urlVideo or 'vfilmesonline' in urlVideo :
                        pu = urlparse(urlVideo)
                        p = r'(?://|\.)((mrdhan|vfilmesonline)\.(com|net))/(?:f|e|v)/(.+)'
                        match = re.search(p, urlVideo)
                        ul = match.group()
                        fxID = ul.split('/v/')[-1]
                        urlF = pu.scheme + '://' + pu.netloc + '/api/source/%s' % fxID
                        headers = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                                "Accept": "*/*",
                                "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
                                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                "X-Requested-With": "XMLHttpRequest",
                                "Alt-Used": "mrdhan.com"
                            }
                        payload = "r=&d=mrdhan.com"
                        r = requests.post(url=urlF, data=payload)
                        js = json.loads(r.text)
                        links = js['data']
                        qual = []
                        for link in links:
                            qual.append(link['label'])
                        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', qual)
                        if index == -1 : return
                        i = int(index)
                        url2Play = links[i]['file']
                        OK = False

                elif 'megafilmeshd50' in urlVideo:
                        link = openURL(urlVideo)
                        soup = BeautifulSoup(link, 'html.parser')
                        filme = soup('video')
                        url2Play = filme[0].source['src']
                        xbmc.log('[plugin.video.midiaflixhd] L585 - ' + str(url2Play), xbmc.LOGINFO)
                        OK = False

                elif 'filmesmp4' in url or 'pandafiles' in urlVideo :
                        if 'pandafiles' in urlVideo :
                                u = re.findall('https://pandafiles.com/embed-(.*?).html', urlVideo)[0]
                                urlF = 'https://filmesmp4.com/03/?dub=%s' % u
                                print('1 ->',urlF)
                        if 'filmesmp4' in urlVideo :
                                u = urlVideo.split('=')[-1]
                                urlF = 'https://filmesmp4.com/03/?dub=%s' % u
                                print('2 -> ',urlF)
                        link = openURL(urlF)
                        try:
                                soup = BeautifulSoup(link, 'html.parser')
                                urlF = soup.iframe['src']
                                url2Play = urlF
                                print(url2Play)
                        except:
                                pass
                        try:
                                soup = BeautifulSoup(link, 'html.parser')
                                urlF = soup.iframe['src']
                                link = openURL(urlF)
                                soup = BeautifulSoup(link, 'html.parser')
                                video = soup.body('source')
                                urlV = video[0]['src']
                                url2Play = urlV
                                print(url2Play)
                        except:
                                pass

                        OK = False

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        xbmc.log('[plugin.video.midiaflixhd] L628 - ' + str(url2Play), xbmc.LOGNOTICE)

        if not url2Play : return

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

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

        return OK

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.midiaflixhd] L671 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MidiaFlixHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []
        sub = None

        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        dados = soup('li',{'id':'player-option-1'})
        xbmc.log('[plugin.video.midiaflixhd] L687 - ' + str(dados), xbmc.LOGNOTICE)
        if not dados :
                dialog = xbmcgui.Dialog()
                dialog.ok(name, " ainda não liberado, aguarde... ")
                return

        dooplay = []
        dtype = dados[0]['data-type']
        dpost = dados[0]['data-post']
        dnume = dados[0]['data-nume']
        dooplay = re.findall(r'<li id=[\'"]player-option-1[\'"] class=[\'"]dooplay_player_option.+?[\'"] data-type=[\'"](.+?)[\'"] data-post=[\'"](.+?)[\'"] data-nume=[\'"](.+?)[\'"]>', link)

        for dtype, dpost, dnume in dooplay:
            print dtype, dpost, dnume

        try:
            headers = {'Referer': url,
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'Host': 'www.midiaflixhd.net',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
            }
            urlF = 'https://www.midiaflixhd.net/wp-admin/admin-ajax.php'
            data = urllib.urlencode({'action': 'doo_player_ajax', 'post': dpost, 'nume': dnume, 'type': dtype})
            xbmc.log('[plugin.video.midiaflixhd] L710 - ' + str(data), xbmc.LOGNOTICE)
            r = requests.post(url=urlF, data=data, headers=headers)
            html = r.content
            soup = BeautifulSoup(html, 'html.parser')
        except:
            pass

        try:
            urlF = soup.iframe['src']
            xbmc.log('[plugin.video.midiaflixhd] L719 - ' + str(urlF), xbmc.LOGNOTICE)
        except:
            pass

        try:
            urlF = soup.a['href']
            fxID = urlF.split('l=')[1]
            urlF = base64.b64decode(fxID)
        except:
            pass

        try:
            soup = BeautifulSoup(link, 'html.parser')
            conteudo = soup.select('.source-box')
            #print(link)
            titsT = []
            for i in conteudo:
                    if 'auth' in str(i) :
                            uri = i.a['href']
                            uri = uri.split('auth=')[-1]
                            urlF = base64.b64decode(uri)
                            b = json.loads(urlF)
                            urlF = b['url']
                            au = urlF.split('/')[-1]
                            idsT.append(urlF)
                            if 'dub' == au : au = titsT.append("Dublado")
                            if 'leg' == au : au = titsT.append("Legendado")

            if not titsT : return

            index = xbmcgui.Dialog().select('Selecione uma das opções :', titsT)

            if index == -1 : return

            i = int(index)
            urlF = idsT[i]
        except:
                pass

        xbmc.log('[plugin.video.midiaflixhd] L758 - ' + str(urlF), xbmc.LOGNOTICE)

        urlVideo = urlF

        if 'play.midiaflixhd.com' in urlVideo:
                html = requests.get(urlVideo).text
                match = re.findall('id[sS]="(.+?)"', html)
                idsT = []
                titsT = []
                for x in match:
                    idsT.append(x)
                match = re.findall('<button class=".+?" idS=".+?" id="btn-(.+?)"><i id=".+?" class="glyphicon glyphicon-play-circle"></i>.+?</button>', html)
                for x in match :
                        x = int(x)+1
                        s = 'Player ' + str(x)
                        titsT.append(s)

                if not titsT : return

                index = xbmcgui.Dialog().select('Selecione uma das opções :', titsT)

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
                xbmc.log('[plugin.video.midiaflixhd] L794 - ' + str(data), xbmc.LOGNOTICE)

                xbmc.log('[plugin.video.midiaflixhd] L796 - ' + str(r.text), xbmc.LOGNOTICE)

                html = r.content
                _html = str(html)
                b = json.loads(_html.decode('hex'))
                if 'video' in str(b) :
                    c = b['video']
                    urlF = c[0]['file']
                    if 'subtitle' in str(b) : sub = b['subtitle']
                else:
                    urlF = b['url']
                xbmc.log('[plugin.video.midiaflixhd] L807 - ' + str(b), xbmc.LOGNOTICE)

                headers = {'referer': urlVideo,
                            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
                r = requests.get(url=urlF,allow_redirects=False,headers=headers)
                if r.status_code >= 300 and r.status_code <= 399:
                    #Sucesso
                    urlF = r.headers['Location']
                else :
                    #Erros
                    return

                r = requests.get(url=urlF,allow_redirects=False,headers=headers)
                if r.status_code >= 300 and r.status_code <= 399:
                    #Sucesso
                    urlF = r.headers['Location']
                else :
                    #Erros
                    return

                urlVideo = urlF

                xbmc.log('[plugin.video.midiaflixhd] L829 - ' + str(urlVideo), xbmc.LOGNOTICE)

                if 'letsupload.co' in urlVideo:
                        nowID = urlVideo.split("=")[1]
                        urlVideo = "https://letsupload.co/plugins/mediaplayer/site/_embed.php?u=%s" % nowID
                        r = requests.get(urlVideo)
                        url2Play = re.findall(r'file: "(.+?)",', r.text)[0]
                        OK = False

                elif 'videok7.online' in urlVideo :
                        url2Play = urlVideo
                        OK = False

                elif 'saborcaseiro' in urlVideo :
                        url2Play = urlVideo
                        OK = False

                elif 'apiblogger.xyz' in urlVideo :
                        headers = {'Referer': urlF2,
                                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                        }
                        url2Play = urlVideo + "|" + urllib.urlencode(headers)
                        OK = False

                elif 'googlevideo.com' in urlVideo :
                        url2Play = urlVideo
                        OK = False

                elif 'video.php' in urlVideo :
                        fxID = urlVideo.split('=')[1]
                        urlVideo = base64.b64decode(fxID)
                        xbmc.log('[plugin.video.midiaflixhd] L860 - ' + str(urlVideo), xbmc.LOGNOTICE)
                        OK = True

                        if 'alfastream.cc' in urlVideo:
                                if 'actelecup.com' in urlVideo:
                                        xbmc.log('[plugin.video.midiaflixhd] L865 - ' + str(urlVideo), xbmc.LOGNOTICE)
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

        xbmc.log('[plugin.video.midiaflixhd] L877 ' + str(urlVideo), xbmc.LOGNOTICE)

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
