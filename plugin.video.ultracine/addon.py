#####################################################################
#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : Ultracine
# By AddonReneSilva - 28/07/2021
# Atualizado (1.0.0) - 24/06/2021
# Atualizado (1.0.1) - 02/08/2021
# 
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver
import requests

from bs4                import BeautifulSoup
from resources.lib      import jsunpack

addon_id = 'plugin.video.ultracine'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder = addonfolder + '/resources/media/'
fanart = addonfolder + '/fanart.png'
addon_handle = int(sys.argv[1])
base = 'https://ultracine.app/'

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base + 'filmes/'                  ,    10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'filmes/'                  ,    20, artfolder + 'new.png')
        addDir('Series'                     , base + 'series/'                  ,    25, artfolder + 'series.png')
        addDir('Pesquisa Series'            , '--'                              ,    30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                              ,    35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                              ,   999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo' , base                              ,  1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('ul', {'class':'list-icon'})
        categorias = conteudo[0]('li')

        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.a.text.encode('utf-8')
                urlC = categoria.a["href"]
                urlC = 'http:%s' % urlC if urlC.startswith("//") else urlC
                urlC = base + urlC if urlC.startswith("categoria") else urlC
                imgC = artfolder + limpa(titC) + '.png'
                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        xbmc.log('[plugin.video.ultracine] L56 ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        filmes = soup('div', attrs={'class':'grid-item'})
        totF = len(filmes)

        for filme in filmes:
                titF = filme.img['alt'].encode('utf-8')
                titF = titF.replace('Assistir', '').replace('Online', '')
                imgF = filme.img['data-src']
                urlF = filme.a['href']
                addDirF(titF, urlF, 100, imgF, False, totF)
        try :
                proxima = soup("a", attrs={"rel":"next"})[0]['href']
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        filmes = soup('div', attrs={'class':'grid-item'})
        totF = len(filmes)

        for filme in filmes:
                titF = filme.img['alt'].encode('utf-8')
                titF = titF.replace('Assistir', '').replace('Online', '')
                imgF = filme.img['data-src']
                urlF = filme.a['href']
                addDirF(titF, urlF, 26, imgF, True, totF)
        try :
                proxima = soup("a", attrs={"rel":"next"})[0]['href']
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass
            
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(url):
        xbmc.log('[plugin.video.ultracine] L136 - ' + str(url), xbmc.LOGINFO)
        html = openURL(url)
        soup = BeautifulSoup(html, 'html.parser')
        conteudo = soup('div', attrs={'class':'ac-item'})
        totF = len(conteudo)
        urlF = url
        imgF = soup('div', {'class':'product-image-page'})[0].img['data-src']
        i = 0

        for i in range(totF):
            i = i + 1
            titF = str(i) + "ª Temporada"
            xbmc.log('[plugin.video.ultracine] L138 ' + str(imgF), xbmc.LOGINFO)
            addDir(titF, urlF, 27, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
        xbmc.log('[plugin.video.ultracineBiz] L144 - ' + str(url), xbmc.LOGNOTICE)
        n = name.replace('ª Temporada', '')
        n = int(n)
        temp = []
        episodios = []

        link  = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        imgF = soup('div', {'class':'product-image-page'})[0].img['data-src']
        sea = soup('div', {'class':'ac-item'})
        epi = soup('div', {'class':'lista-episodios'})
        s = len(sea)
        e = len(epi)
        t2 = (e / s)
        t1 = n * t2
        i = int(t1 - t2)
        ul = epi[i]('ul')
        filmes = ul[0]('li')
        totF = len(filmes)
        xbmc.log('[plugin.video.ultracineBiz] L128 - ' + str(totF), xbmc.LOGINFO)

        for filme in filmes:
            titF = filme.a.span.text.encode('utf-8')
            urlF = filme.a['href']
            addDirF(titF, urlF, 100, imgF, False, totF)

        xbmcplugin.setContent(int(sys.argv[1]) ,"episodes")

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.quote(texto)
                url      = base + 'busca?q=%s' % str(pesquisa)
                hosts = []

                link = openURL(url)
                soup     = BeautifulSoup(link, 'html.parser')
                filmes = soup('div', attrs={'class':'grid-item'})
                totF = len(filmes)

                for filme in filmes:
                        titF = filme.img['alt'].encode('utf-8')
                        titF = titF.replace('Assistir', '').replace('Online', '')
                        imgF = filme.img['data-src']
                        urlF = filme.a['href']
                        pltF = "" #sinopse(urlF)
                        temp = [urlF, titF, imgF]
                        hosts.append(temp)

                a = []
                for url, titulo, img in hosts:
                    temp = [url, titulo, img]
                    a.append(temp);
                return a

def doPesquisaSeries():
        a = pesquisa()
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            xbmc.log('[plugin.video.ultracine] L189 - ' + str(url2), xbmc.LOGINFO)
            if 'serie' in url2 :
                addDir(titulo, url2, 26, img, False, total)
            else :
                addDir(titulo, url2, 100, img, False, total)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        
def doPesquisaFilmes():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            if 'serie' in url2 :
                addDir(titulo, url2, 26, img, False, total)
            else :
                addDir(titulo, url2, 100, img, False, total)

        setViewFilmes()

def player(name,url,iconimage):
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('UltraCine', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)
        xbmc.log('[plugin.video.ultracine] L264 ' + str(url), xbmc.LOGNOTICE)

        titsT = []
        idsT = []
        matriz = []

        link = openURL(url)
        soup  = BeautifulSoup(link, 'html.parser')
        try:
            urlF = re.findall('<div id="Link" Class="Link"> <a href="(.*?)" target="_blanck">', link)[0]
        except:
            pass
        try:
            urlF = re.findall('<option value=".*?" data-targetiframe=".*?" data-iframe="(.*?)">', link)[0]
        except:
            pass
        print(urlF)
        link = openURL(urlF)
        soup  = BeautifulSoup(link, 'html.parser')
        urlF = soup.iframe['src']
        print(urlF)
        if '//public' in urlF : urlF = urlF.replace('//public','/public')
        fxID = urlF.split('id=')[1]
        if "&" in fxID: fxID = fxID.split('&')[0]
        host = urlF.split('/public')[0]
        t = int(round(time.time() * 1000))
        urlF = host + '/playlist/' + fxID + '/' + str(t)
        print(urlF)
        r = requests.get(url=urlF)
        titsT = []
        idsT = []
        titsT = re.findall('RESOLUTION=(.*?)\n/hls.+', r.text)
        idsT = re.findall('RESOLUTION=.*?\n/(.*?)\n', r.text)
        urlVideo = host + '/' + idsT[0]

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        xbmc.log('[plugin.video.ultracine] L297 ' + str(urlVideo), xbmc.LOGNOTICE)

        if 'bolsonaro' in urlVideo :
                url2Play = urlVideo
                OK = False

        elif 'ok' in urlVideo :
                fxID = urlVideo.split('ed/')[1]
                urlVideo = 'http://ok.ru/videoembed/%s' % fxID

        elif 'thevid' in urlVideo :
                fxID = urlVideo.split('e/')[1]
                urlVideo = 'https://thevid.net/e/%s' % fxID
                linkTV  = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(linkTV)
                #xbmc.log('[plugin.video.ultracineBiz - player_series -L313] ' + str(linkTV), xbmc.LOGNOTICE)
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
            xbmc.sleep(5000)
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
        xbmc.log('[plugin.video.ultracine] L375 ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('UltraCine', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        links = []
        hosts = []
        hostid = []
        
        link = openURL(url)
        soup  = BeautifulSoup(link, 'html.parser')
        try:
            urlF = re.findall('<div id="Link" Class="Link"> <a href="(.*?)" target="_blanck">', link)[0]
        except:
            pass
        try:
            urlF = re.findall('<option value=".*?" data-targetiframe=".*?" data-iframe="(.*?)">', link)[0]
        except:
            pass
        print(urlF)
        link = openURL(urlF)
        soup  = BeautifulSoup(link, 'html.parser')
        urlF = soup.iframe['src']
        print(urlF)
        if '//public' in urlF : urlF = urlF.replace('//public','/public')
        fxID = urlF.split('id=')[1]
        if "&" in fxID: fxID = fxID.split('&')[0]
        host = urlF.split('/public')[0]
        t = int(round(time.time() * 1000))
        urlF = host + '/playlist/' + fxID + '/' + str(t)
        print(urlF)
        r = requests.get(url=urlF)
        titsT = []
        idsT = []
        titsT = re.findall('RESOLUTION=(.*?)\n/hls.+', r.text)
        idsT = re.findall('RESOLUTION=.*?\n/(.*?)\n', r.text)
        urlVideo = host + '/' + idsT[0]

        xbmc.log('[plugin.video.ultracineBiz - player_series - L423 ] ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'bolsonaro' in urlVideo :
                url2Play = urlVideo
                OK = False

        xbmc.log('[plugin.video.ultracineBiz - player_series - L498 ] ' + str(urlVideo), xbmc.LOGNOTICE)

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
            xbmc.sleep(5000)
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
        titO = titO.split(':')[0]
        xbmc.log('[plugin.video.ultracine] L494 - ' + str(titO), xbmc.LOGINFO)

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        xbmc.log('[plugin.video.ultracine] L499 - ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        ytID = None
        try:
            ytID = re.findall('<a id="openTrailer" data-iframe="https://www.youtube.com/embed/(.*?)" href="#trailer"',link)[0]
        except:
            if not ytID :
                addon = xbmcaddon.Addon()
                addonname = addon.getAddonInfo('name')
                line1 = str("Trailer não disponível!")
                xbmcgui.Dialog().ok(addonname, line1)
                return

        #xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=youtubevideo, id=%s)' % ytID)
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play('plugin://plugin.video.youtube/play/?video_id='+ytID)

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
        soup = BeautifulSoup(link, 'html.parser')
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

xbmcplugin.endOfDirectory(int(sys.argv[1]))