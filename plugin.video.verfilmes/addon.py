#####################################################################
#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : VerFilmes
# By AddonReneSilva - 17/02/2017
# Atualizado (1.0.0) - 17/02/2017
# Atualizado (1.1.0) - 22/03/2019
# Atualizado (1.1.3) - 26/04/2019
# Atualizado (1.1.4) - 09/06/2019
# Atualizado (1.1.5) - 23/11/2019
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver
import requests

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib               import jsunpack

addon_id = 'plugin.video.verfilmes'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder = addonfolder + '/resources/img/'
fanart = addonfolder + '/fanart.png'
addon_handle = int(sys.argv[1])
base = base64.b64decode('aHR0cDovL3d3dy52ZXJmaWxtZXMuYml6Lw==')

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                    , base                                        ,    10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'categoria/lancamento-de-2019/'    ,    20, artfolder + 'lancamentos.png')
        addDir('Filmes Dublados'            , base + 'search.php?s=dublado'                ,    20, artfolder + 'pesquisa.png')
        addDir('Series'                        , base + 'categoria/series/'                ,    25, artfolder + 'legendados.png')
        addDir('Pesquisa Series'            , '--'                                        ,    30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                                        ,    35, artfolder + 'pesquisa.png')
        addDir('Configurações'                , base                                        ,  999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo'    , base                                        , 1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo   = soup("div", {"id": "sidebar"})
        categorias = conteudo[0]("li")
        totC = len(categorias)
        for categoria in categorias:
                titC = categoria.text.encode('utf-8', 'ignore')
                if not 'Lançamento' in titC :
                                urlC = categoria.a["href"]
                                imgC = artfolder + limpa(titC) + '.png'
                                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup     = BeautifulSoup(link)
        conteudo = soup("div", {"id": "postagem"})
        filmes = conteudo[0]("div",{"class":"capa"})
        urls = conteudo[0]("a")
        totF = len(filmes)

        for x in range(0, totF):
                titF = filmes[x].img["title"].encode('utf-8','replace')
                urlF = urls[x].get("href").encode('utf-8','replace')
                pltF = "" #sinopse(urlF)
                imgF = filmes[x].img["src"].encode('utf-8', 'ignore')
                addDirF(titF, urlF, 100, imgF, False, totF, pltF)
        try :
                prox = re.findall('<a href="(.*?)/page/(.*?)">.*?</a>', link)
                i = len(prox)
                i = int(i)
                i = (i-1)
                proxima = prox[i][0] + "/page/" + prox[i][1]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup("div", {"id": "postagem"})
        filmes = conteudo[0]("div",{"class":"capa"})
        urls = conteudo[0]("a")
        totF = len(filmes)

        for x in range(0, totF):
                titF = filmes[x].img["title"].encode('utf-8','replace')
                urlF = urls[x].get("href").encode('utf-8','replace')
                pltF = "" #sinopse(urlF)
                imgF = filmes[x].img["src"].encode('utf-8', 'ignore')
                imgF = imgF.split('src=')[1]
                imgF = imgF.split('&h=')[0]
                addDirF(titF, urlF, 26, imgF, True, totF, pltF)
        try :
                prox = re.findall('<a href="(.*?)/page/(.*?)">.*?</a>', link)
                i = len(prox)
                i = int(i)
                i = (i-1)
                proxima = prox[i][0] + "/page/" + prox[i][1]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass
            
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(url):
        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup("div", {"class": "conteudo"})
        linhas = conteudo[0]("ul", {"class": "itens"})
        temporadas = linhas[0]("li",{"id":"tempnresponsive"})
        totF = len(temporadas)
        imgF = []
        img = soup.find("div", {"class": "playingconteudo"})
        imgF = img.img['src']
        imgF = imgF.split('src=')[1]
        imgF = imgF.split('&h=')[0]
        urlF = url
        i = 0

        for i in range(totF):
            i = i + 1
            titF = str(i) + "ª Temporada"
            xbmc.log('[plugin.video.verfilmes] L138 ' + str(imgF), xbmc.LOGNOTICE)
            addDir(titF, urlF, 27, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
        xbmc.log('[plugin.video.verfilmesBiz] L144 - ' + str(url), xbmc.LOGNOTICE)
        n = name.replace('ª Temporada', '')
        n = int(n)
        temp = []
        episodios = []

        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link)
        conteudo = soup("div", {"class": "videos"})
        arquivo = conteudo[0]("li", {"class": "video" + str(n) + "-code"})
        perfil = soup('div',{'id':'perfil_conteudo'})

        sname = perfil[0].h1.text.encode('utf-8')

        sname = sname.split('-')[0].strip()

        try:
            temporadas = arquivo[0]('table')
            filmes = temporadas[0]('a')
            audio = str(arquivo[0].span.text)

            totF = len(filmes)

            for filme in filmes:
                    titF = filme.text.decode('unicode-escape').encode('utf-8')
                    titF = titF.replace('Assistir ','').replace('Filme ','').replace('Episdio', 'Episodio') + " " +audio #" Dublado"
                    titF = sname + " "+str(n) + "T " + titF
                    urlF = filme.get("href").encode('utf-8', 'ignore')
                    urlF = base + urlF
                    temp = (titF, urlF)
                    episodios.append(temp)
        except:
            pass

        try:
            temporadas = arquivo[0]('table')
            filmes = temporadas[1]('a')
            audio = str(temporadas[1].span.text)

            totF = len(filmes)

            for filme in filmes:
                    titF = filme.text.decode('unicode-escape').encode('utf-8')
                    titF = titF.replace('Assistir ','').replace('Filme ','').replace('Episdio', 'Episodio') + " " +audio #" Legendado"
                    titF = sname + " "+str(n) + "T " + titF
                    urlF = filme.get("href").encode('utf-8', 'ignore')
                    urlF = base + urlF
                    temp = (titF, urlF)
                    episodios.append(temp)
        except:
            pass

        audio = []
        imgF = []
        img = soup.find("div", {"class": "playingconteudo"})
        imgF = img.img['src']
        imgF = imgF.split('src=')[1]
        imgF = imgF.split('&h=')[0]

        total = len(episodios)

        for titF, urlF in episodios:
                addDirF(titF, urlF, 110, imgF, False, totF)

        #xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
        xbmcplugin.setContent( int(sys.argv[1]) ,"episodes" )

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.quote(texto)
                url      = base + 'search.php?s=%s' % str(pesquisa)
                hosts = []

                link = openURL(url)
                #link = unicode(link, 'utf-8', 'ignore')
                soup     = BeautifulSoup(link)

                conteudo = soup("div", {"id": "postagem"})
                filmes = conteudo[0]("div", {"class":"capa"})
                urls = conteudo[0]("a")
                totF = len(filmes)

                for x in range(0, totF):
                    titF = filmes[x].img["title"].encode('utf-8','replace')
                    urlF = urls[x].get("href").encode('utf-8','replace')
                    pltF = sinopse(urlF)
                    imgF = filmes[x].img["src"].encode('utf-8', 'ignore')
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

        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

def doPesquisaFilmes():
        a = pesquisa()
        xbmc.log('[plugin.video.verfilmes] L248 - ' + str(a), xbmc.LOGNOTICE)
        if a is None:
            xbmcgui.Dialog().ok('VerFilmes', 'Conteudo temporariamente indisponivel,desculpe o transtorno.')
            return
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 100, img, False, total)

        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

def player(name,url,iconimage):
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('VerFilmes', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)
        xbmc.log('[plugin.video.verfilmes] L264 ' + str(url), xbmc.LOGNOTICE)

        titsT = []
        matriz = []

        link = openURL(url)
        soup  = BeautifulSoup(link)
        conteudo = soup("div", {"class":"opcoes"})
        srvsdub = conteudo[0]('a')
        totD = len(srvsdub)
        titsT = []
        for i in range(totD) :
                        titS = srvsdub[i].text
                        titsT.append(titS)
                        print titsT

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        i = int(index)

        links  = conteudo[0]('a')

        if len(links) == 0 : links = conteudo[0]("a")

        urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]

        link = openURL(urlVideo)
        soup  = BeautifulSoup(link)
        conteudo = soup.findAll("iframe")
        urlVideo = conteudo[2].get('src')

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        xbmc.log('[plugin.video.verfilmes] L297 ' + str(urlVideo), xbmc.LOGNOTICE)

        if 'openload2' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://openload.co/embed/%s' % fxID

        elif 'ok' in urlVideo :
                fxID = urlVideo.split('ed/')[1]
                urlVideo = 'http://ok.ru/videoembed/%s' % fxID

        elif 'thevid' in urlVideo :
                fxID = urlVideo.split('e/')[1]
                urlVideo = 'https://thevid.net/e/%s' % fxID
                linkTV  = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(linkTV)
                #xbmc.log('[plugin.video.verfilmesBiz - player_series -L313] ' + str(linkTV), xbmc.LOGNOTICE)
                sUnpacked = jsunpack.unpack(aMatches[1])
                url2Play = re.findall('var ldAb="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                url2Play = 'http:%s' % url if url.startswith("//") else url

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

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.verfilmes] L375 ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('VerFilmes', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        links = []
        hosts = []
        hostid = []
        '''
        matriz = []
        link = openURL(url)
        soup  = BeautifulSoup(link)
        conteudo = soup("div", {"class":"itens"})
        srvsdub = conteudo[0]('a')
        totD = len(srvsdub)

        titsT = []

        for i in range(totD) :
                titS = srvsdub[i].text
                titS = titS.replace('Assistir no', '')
                titsT.append(titS)
                print titsT
        '''
        url2 = url.replace('?','&')
        url3 = url2.split('eps/&')[1]
        srvs = url3.split('&')

        for i in srvs :
                if '=' in i :
                        n = i.split('=')[0]
                        if 'verystream' not in n :
                                titsT.append(n)
                                hostid.append(i)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        i = int(index)

        #links  = conteudo[0]('a')

        #if len(links) == 0 : links = conteudo[0]("a")

        #urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]
        urlVideo = hostid[i]
   
        xbmc.log('[plugin.video.verfilmesBiz - player_series - L423 ] ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'opload2' in urlVideo :
                fxID = urlVideo.split('=')[1]
                fxID = fxID.split('/')[0]
                urlVideo = 'https://openload.co/embed/%s' % fxID

        elif 'mango2=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://streamango.com/embed/%s' % fxID

        elif 'oload.fun' in urlVideo :
                fxID = urlVideo.split('/')[4]
                xbmc.log('[plugin.video.verfilmesBiz - player_series - L432] ' + str(fxID), xbmc.LOGNOTICE)
                urlVideo = 'https://oload.fun/embed/%s' % fxID

        elif 'ok2' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://ok.ru/videoembed%s' % fxID

        elif 'vidto2' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://vidto.me/embed-%s-850x550.html' % fxID

        elif 'vidzi' in urlVideo :
                fxID = urlVideo.split('-')[1]
                urlVideo = 'http://vidzi.tv/%s.html' % fxID

        elif 'rv.opensv.biz' in urlVideo :
                fxID = urlVideo.split('e/')[1]
                fxID = fxID.replace('html','')
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID

        elif 'tvid=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                fxID = fxID.split('&')[0]
                fxID = fxID.replace('html','')
                urlVideo = 'https://thevid.net/e/%s' % fxID

        elif 'verystream=' in urlVideo:
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://verystream.com/e/%s' % fxID

        elif 'vcdn=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://www.fembed.com/v/%s' % fxID

        elif 'rvid2=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                fxID = fxID.split('&')[0]
                fxID = fxID.replace('html','')
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID

        elif 'vcstream=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                fxID = fxID.split('&')[0]
                urlVideo = 'https://vcstream.to/embed/%s' % fxID

        elif 'thevid' in urlVideo :
                fxID = urlVideo.split('e/')[1]
                urlVideo = 'https://thevid.net/e/%s' % fxID
                '''
                linkTV  = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(linkTV)
                #xbmc.log('[plugin.video.verfilmesBiz - player_series -L438] ' + str(linkTV), xbmc.LOGNOTICE)
                sUnpacked = jsunpack.unpack(aMatches[1])
                url2Play = re.findall('var ldAb="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                url2Play = 'http:%s' % url if url.startswith("//") else url

                OK = False
                '''
        xbmc.log('[plugin.video.verfilmesBiz - player_series - L498 ] ' + str(urlVideo), xbmc.LOGNOTICE)

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                return
                pass

        if not url2Play : return

        legendas = '-'

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        listItem = xbmcgui.ListItem(name,thumbnailImage=iconimage)
        listItem.setPath(url2Play)
        listItem.setProperty('mimetype','video/mp4')
        listItem.setProperty('IsPlayable', 'true')
        playlist.add(url2Play,listItem)

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
        req = urllib2.Request(url)
        req.add_header('Referer', url)
        req.add_header('Method', 'GET')
        req.add_header('Upgrade-Insecure-Requests', '1')
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36')
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
        u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'icon': iconimage, 'thumb': iconimage })

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR lime]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=99)'%(sys.argv[0], urllib.quote_plus(url))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def getInfo(url)    :
        link = openURL(url)
        titO = re.findall(r'<meta property="og:title" content="(.*?)" />', link)[0]
        titO = titO.replace('Assistir','').replace('Dublado','').replace('Legendado','').replace('Online','')
        titO = titO.replace('- Todas as Temporadas','')

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        ytID = re.findall('<a href="https://www.youtube.com/embed/(.+?)?autoplay=1" rel="nofollow" class="trailer" target="\_blank" title=".+?"><img src="img/trailer.png" /></a>', link)[0]
        ytID = ytID.replace('?','')

        if not ytID :
            addon = xbmcaddon.Addon()
            addonname = addon.getAddonInfo('name')
            line1 = str("Trailer não disponível!")
            xbmcgui.Dialog().ok(addonname, line1)
            return

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=youtubevideo, id=%s)' % ytID)

def setViewMenu() :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

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

def sinopse(urlF):
        link = openURL(urlF)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup("div", {"class": "perfil_sinopse"})
        #print conteudo
        plot = conteudo[0].span.text
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