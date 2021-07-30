#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : Ultracine
# By AddonBrasil - 08/08/2020
# Atualizado (2.0.0) - 28/07/2021
#####################################################################

import urllib, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from bs4                import BeautifulSoup
from resources.lib      import jsunpack

version   = '2.0.0'
addon_id  = 'plugin.video.ultracine'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = xbmcaddon.Addon()
_handle = int(sys.argv[1])

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/fanart.png'
base = base64.b64decode('aHR0cHM6Ly91bHRyYWNpbmUuYXBwLw==')

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base + ''                     ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'filmes/'              ,   20, artfolder + 'lancamentos.png')
        addDir('Filmes Dublados'            , base + 'busca?q=dublado'      ,   20, artfolder + 'pesquisa.png')
        addDir('Series'                     , base + 'categoria/series/'    ,   25, artfolder + 'legendados.png')
        addDir('Pesquisa Filmes'            , '--'                          ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                          ,  999, artfolder + 'config.png', 1, False)

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

def getFilmes(name,url,iconimage):
        xbmc.log('[plugin.video.ultracine] L65 - ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        filmes = soup('div', attrs={'class':'grid-item'})
        totF = len(filmes)

        for filme in filmes:
                titF = filme.img['alt'].encode('utf-8')
                titF = titF.replace('Assistir', '')
                imgF = filme.img['data-src']
                urlF = filme.a['href']
                pltF = "" #sinopse(urlF)
                addDirF(titF, urlF, 100, imgF, False, totF, pltF)
        try :
                proxima = soup("a", attrs={"rel":"next"})[0]['href']
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.ultracine] L100- ' + str(url), xbmc.LOGINFO)
        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, "html.parser")
        filmes = soup('div', attrs={'class':'grid-item'})
        totF = len(filmes)

        for filme in filmes:
                titF = filme.img['alt'].encode('utf-8')
                titF = titF.replace('Assistir', '')
                imgF = filme.img['data-src']
                urlF = filme.a['href']
                pltF = "" #sinopse(urlF)
                addDirF(titF, urlF, 26, imgF, True, totF, pltF)
        try :
                proxima = soup("a", attrs={"rel":"next"})[0]['href']
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass
            
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(name,url,iconimage):
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
            xbmc.log('[plugin.video.ultracine] L138 ' + str(imgF), xbmc.LOGNOTICE)
            addDir(titF, urlF, 27, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url,iconimage):
        xbmc.log('[plugin.video.ultracine] L156 - ' + str(url), xbmc.LOGINFO)
        n = name.replace('ª Temporada', '')
        n = int(n)
        n = (n-1)
        temp = []
        episodios = []

        link = openURL(url)
        #link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        imgF = soup('div', {'class':'product-image-page'})[0].img['data-src']
        sea = soup('div', {'class':'ac-item'})
        epi = soup('div', {'class':'lista-episodios'})
        t1 = n * 2
        i = int(t1 - 2)
        xbmc.log('[plugin.video.ultracineBiz] L128 - ' + str(epi), xbmc.LOGNOTICE)
        ul = epi[i]('ul')
        filmes = ul[0]('li')

         try:
            totF = len(filmes)

            for filme in filmes:
                    titF = filme.a.span.text.encode('utf-8')
                    urlF = filme.a['href']
                    temp = (titF, urlF)
                    episodios.append(temp)
        except:
            pass

        total = len(episodios)

        for titF, urlF in episodios:
                addDirF(titF, urlF, 110, imgF, False, totF)

        xbmcplugin.setContent(int(sys.argv[1]) ,"episodes")

 def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.parse.quote(texto)
                url      = base + 'busca?q=%s' % str(pesquisa)

                xbmc.log('[plugin.video.ultracine] L198 - ' + str(url), xbmc.LOGINFO)
                hosts = []
                temp = []
                link = openURL(url)
                soup = BeautifulSoup(link, 'html.parser')
                filmes = soup('div', attrs={'class':'grid-item'})
                totF = len(filmes)

                for filme in filmes:
                        titF = filme.img['alt'].encode('utf-8')
                        titF = titF.replace('Assistir', '')
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
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            xbmc.log('[plugin.video.ultracine] L237 - ' + str(url2), xbmc.LOGINFO)
            addDir(titulo, url2, 26, img, False, total)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def doPesquisaFilmes():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 100, img, False, total)

def player(name,url,iconimage):
        xbmc.log('[plugin.video.ultracine] L249 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('ultracine', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        sub = None

        link = openURL(url)
        soup  = BeautifulSoup(link)
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
        soup = BeautifulSoup(link, 'html.parser')
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

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name +' Por favor aguarde...')

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        xbmc.log('[plugin.video.ultracine] L364 - ' + str(url2Play), xbmc.LOGINFO)

        if not url2Play : return

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' +name+' Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.hls')
                #listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
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
                    sub_file_xml.write(urllib.parse.urlopen(legendas).read())
                    sub_file_xml.close()
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)


def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.ultracine] L421 - ' + str(url), xbmc.LOGINFO)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('ultracine', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []
        sub = None

        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')

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
        soup  = BeautifulSoup(link)
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

        xbmc.log('[plugin.video.ultracine] L375 - ' + str(urlVideo), xbmc.LOGINFO)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name+ ' Por favor aguarde...')

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

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name+ ' Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.hls')
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
                    sub_file_xml.write(urllib.parse.urlopen(legendas).read())
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

def openURL(url):
        headers= {'authority': 'ultracine.org',
                'Referer': url,
                'accept-encoding':'gzip, deflate, br',
                'scheme': 'https',
                'content-type': 'text/html; charset=UTF-8',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36'
        }
        link = requests.get(url).text
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

        xbmc.log('[plugin.video.ultracine] L644 ' + str(u), xbmc.LOGINFO)

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

try    : url=urllib.parse.unquote_plus(params["url"])
except : pass
try    : name=urllib.parse.unquote_plus(params["name"])
except : pass
try    : mode=int(params["mode"])
except : pass
try    : iconimage=urllib.parse.unquote_plus(params["iconimage"])
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
elif mode == 27   : getEpisodios(name,url,iconimage)
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