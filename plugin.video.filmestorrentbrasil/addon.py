#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : FilmestorrentBrasil
# By AddonBrasil - 08/08/2020
# Atualizado (1.1.0) - 01/10/2022
# Atualizado (1.1.1) - 03/10/2022
# Atualizado (1.1.2) - 02/03/2023
# Atualizado (1.1.3) - 03/03/2023
# Atualizado (1.1.4) - 03/03/2023
# Atualizado (1.1.5) - 20/03/2023
# Atualizado (1.1.6) - 16/08/2023
# Atualizado (1.1.7) - 02/12/2023
# Atualizado (1.1.8) - 25/12/2023
# Atualizado (1.1.9) - 26/12/2023
# Atualizado (1.2.0) - 27/12/2023
# Atualizado (1.2.1) - 22/01/2024
# Atualizado (1.2.2) - 17/02/2024
# Atualizado (1.2.3) - 20/02/2024
# Atualizado (1.2.4) - 15/04/2024
# Atualizado (1.2.5) - 15/01/2025
# Atualizado (1.2.6) - 85/01/2025
#####################################################################

import urllib, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from bs4                import BeautifulSoup
from resources.lib      import jsunpack

addon_id  = 'plugin.video.filmestorrentbrasil'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = xbmcaddon.Addon()
_handle = int(sys.argv[1])

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/fanart.png'
base        = 'https://www.starckfilmes.com.br'

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base + ''                     ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + '/?type=filme'         ,   20, artfolder + 'new.png')
        addDir('Seriados'                   , base + '/?type=série'         ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'            , '--'                          ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                          ,   35, artfolder + 'pesquisa.png')
        #addDir('Configurações'              , base                          ,  999, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('nav')
        categorias = conteudo[0]('li')

        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.a.text.encode('utf-8')
                urlC = categoria.a["href"]
                urlC = 'http:%s' % urlC if urlC.startswith("//") else urlC
                urlC = base + urlC if urlC.startswith("/") else urlC
                imgC = artfolder + limpa(titC) + '.png'
                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L77 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div',{'class':'home post-catalog'})
        filmes = conteudo[0]('div',{'class':'item'})

        totF = len(filmes)

        for filme in filmes:
            titF = ""
            try:
                urlF = filme('a')[0]['href']
                titF = filme('a')[1].text.encode('utf-8')
                imgF = filme('div',{'class':'post-image-sub'})[0].get('data-bk')
                urlF = base + urlF if urlF.startswith("/") else urlF
                pltF = titF
                addDirF(titF, urlF, 100, imgF, False, totF)
            except:
                pass

        try :
                proxima = re.findall(r'<div class="prev-active"><a href="(.*?)">.*?</a></div>', str(soup))
                if len(proxima) > 1:
                    proxima = proxima[1]
                else:
                    proxima = proxima[0]
                proxima = base + proxima if proxima.startswith("/") else proxima
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        xbmc.log('[plugin.video.filmestorrentbrasil] L110- ' + str(url), xbmc.LOGNOTICE)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup('div', {'class':'home post-catalog'})
        filmes = conteudo[0]('div', {'class':'item'})

        totF = len(filmes)

        for filme in filmes:
                urlF = filme('a')[0]['href']
                titF = filme('a')[1].text.encode('utf-8')
                imgF = filme('div',{'class':'post-image-sub'})[0].get('data-bk')
                urlF = base + urlF if urlF.startswith("/") else urlF
                pltF = titF
                addDirF(titF, urlF, 27, imgF, True, totF)

        try :
                proxima = re.findall(r'<div class="prev-active"><a href="(.*?)">.*?</a></div>', str(soup))
                if len(proxima) > 1:
                    proxima = proxima[1]
                else:
                    proxima = proxima[0]
                proxima = base + proxima if proxima.startswith("/") else proxima
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        #setViewFilmes()

def getTemporadas(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L143 - ' + str(url), xbmc.LOGNOTICE)
        html = openURL(url)
        soup = BeautifulSoup(html, 'html.parser')
        conteudo = soup('div', {'id':'seasons'})
        seasons = conteudo[0]('div', {'class': 'se-c'})
        totF = len(seasons)
        imgF = iconimage
        urlF = url
        i = 1
        while i <= totF:
                titF = str(i) + "ª Temporada"
                try:
                    addDir(titF, urlF, 27, iconimage, totF, True)
                except:
                    pass
                i = i + 1

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L163 - ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        soup = BeautifulSoup(link, 'html.parser')
        links = soup('p')
        if not 'magnet' in str(links) : links = soup('div',{'class':'buttons-content'})
        totF = len(links)
        imgF = iconimage
        try:
            imgF = links[1].img['src']
        except:
            pass

        for link in links:
            if 'campanha' in str(link):
                #if titF: titF = 'Epis'
                u = link.a['href']
                fxID = u.split('?id=')[-1]
                urlF = base64.b64decode(fxID).decode('utf-8')
                urlF = base + urlF if urlF.startswith("/") else urlF
                titF = name.split("emporada")[0] + " | " + str(titF)
                addDirF(titF, urlF, 110, imgF, False, totF)
            elif 'magnet' in str(link):
                urlF = link.a['href']
                urlF = base + urlF if urlF.startswith("/") else urlF
                titF = str(link.text.encode('utf-8'))
                titF = titF.replace('\n','')
                t = ":"
                r = titF.find(t)
                titF = titF[0:r]
                #addDirF(name+"|"+titF, urlF, 110, imgF, False, totF)
                addDirF(titF, urlF, 110, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')

def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto    = keyb.getText()
                pesquisa = urllib.quote(texto)
                url      = base + '?s=%s' % str(pesquisa)

                #xbmc.log('[plugin.video.filmestorrentbrasil] L241 - ' + str(url), xbmc.LOGNOTICE)
                hosts = []
                temp = []
                link = openURL(url)
                soup = BeautifulSoup(link, "html.parser")
                conteudo = soup('div',{'class':'home post-catalog'})
                filmes = conteudo[0]('div',{'class':'item'})

                totF = len(filmes)

                for filme in filmes:
                        titF = ""
                        try:
                            urlF = filme('a')[0]['href']
                            titF = filme('a')[1].text.encode('utf-8')
                            imgF = filme('div',{'class':'post-image-sub'})[0].get('data-bk')
                            urlF = base + urlF if urlF.startswith("/") else urlF
                            temp = [urlF, titF, imgF]
                            hosts.append(temp)
                        except:
                            pass

                return hosts

def doPesquisaSeries():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            addDirF(titulo, url2, 27, img, True, total)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def doPesquisaFilmes():
        a = pesquisa()
        if a is None : return
        total = len(a)
        for url2, titulo, img in a:
            addDirF(titulo, url2, 100, img, False, total)

def player(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L286 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmestorrentBrasil', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        sub = None

        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        conteudo = soup("div",{"class":"container"})
        conteudo[1]("div",{"class":"buttons-content"})
        buttons = conteudo[1]("div",{"class":"buttons-content"})
        links=[]
        for i in buttons:
                if 'magnet' in str(i):
                    links.append(i)
        n = 1

        for link in links:
            if 'campanha' in str(link) :
                urlF = link.a['href']
                print(urlF)
                idS = urlF.split('id=')[-1]
                urlVideo = base64.b64decode(idS).decode('utf-8')
                titS = "Server_" + str(n)
                n = n + 1
                titsT.append(titS)
                idsT.append(urlVideo)
            if 'magnet' in str(link):
                urlF = link.a['href']
                urlVideo = urlF
                if '&dn=' in str(urlF) :
                    titF = urlF.split('&dn=')[1].split('&tr=')[0]
                    titF = urllib.unquote(titF)
                    titS = titF[0:50]
                else:
                    titS = link.text.replace('\n','') #"Server_" +str(n)
                n = n + 1
                titsT.append(titS)
                idsT.append(urlVideo)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das opcoes :', titsT)

        if index == -1 : return

        i = int(index)
        urlVideo = idsT[i]

        xbmc.log('[plugin.video.filmestorrentbrasil] L334 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name + ' Por favor aguarde...')

        if 'magnet' in urlVideo :
                #urlVideo = urllib.unquote(urlVideo)
                if "&amp;" in str(urlVideo) : urlVideo = urlVideo.replace("&amp;","&")
                url2Play = 'plugin://plugin.video.elementum/play?uri={0}'.format(urllib.quote_plus(urlVideo))
                OK = False

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        xbmc.log('[plugin.video.filmestorrentbrasil] L353 - ' + str(url2Play), xbmc.LOGNOTICE)

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
                listitem.setArt({"Poster": iconimage})
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
                listitem.setArt({"Poster": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('video/mp4')
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()

        while xbmcPlayer.play(playlist) :
            xbmc.sleep(20000)
            if not xbmcPlayer.isPlaying():
                xbmcPlayer.stop()

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(requests.get(legendas).text)
                    sub_file_xml.close()
                    xmltosrt.main(sfile_xml)
                    xbmcPlayer.setSubtitles(sfile)
            else:
                xbmcPlayer.setSubtitles(legendas)

        return OK

def player_series(name,url,iconimage):
        xbmc.log('[plugin.video.filmestorrentbrasil] L413 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmestorrentBrasil', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        sub = None

        urlVideo = url

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name+ ' Por favor aguarde...')

        if 'magnet' in urlVideo :
                #urlVideo = urllib.unquote(urlVideo)
                if "&amp;" in str(urlVideo) : urlVideo = urlVideo.replace("&amp;","&")
                url2Play = 'plugin://plugin.video.elementum/play?uri={0}'.format(urlVideo)
                OK = False

        xbmc.log('[plugin.video.filmestorrentbrasil] L413 - ' + str(url2Play), xbmc.LOGINFO)

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        if not url2Play : return

        if sub is None:
            legendas = '-'
        else:
            legendas = sub

        mensagemprogresso.update(75, 'Abrindo Sinal para ' + name + ' Por favor aguarde...')

        playlist = xbmc.PlayList(1)
        playlist.clear()

        if "m3u8" in url2Play:
                #ip = addon.getSetting("inputstream")
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setArt({"Poster": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('application/x-mpegURL')
                listitem.setProperty('inputstream','inputstream.hls')
                listitem.setContentLookup(False)
                playlist.add(url2Play,listitem)
        else:
                listitem = xbmcgui.ListItem(name, path=url2Play)
                listitem.setArt({"thumb": iconimage, "icon": iconimage})
                listitem.setArt({"Poster": iconimage})
                listitem.setProperty('IsPlayable', 'true')
                listitem.setMimeType('video/mp4')
                playlist.add(url2Play,listitem)

        xbmcPlayer = xbmc.Player()

        while xbmcPlayer.play(playlist) :
            xbmc.sleep(20000)
            if not xbmcPlayer.isPlaying():
                xbmcPlayer.stop()

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        if legendas != '-':
            if 'timedtext' in legendas:
                    import os.path
                    sfile = os.path.join(xbmc.translatePath("special://temp"),'sub.srt')
                    sfile_xml = os.path.join(xbmc.translatePath("special://temp"),'sub.xml')#timedtext
                    sub_file_xml = open(sfile_xml,'w')
                    sub_file_xml.write(requests.get(legendas).text)
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
        import sys, platform, subprocess
        os = ""
        user_agent = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
        #user_agent = "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"

        if hasattr(sys, 'getandroidapilevel'):
            os = "Android"
        else:
            os = platform.system()

        xbmc.log('[plugin.video.filmestorrentbrasil] L515 - ' + str(os), xbmc.LOGNOTICE)

        if os == 'Windows' :
            result = subprocess.check_output(["curl","-A", user_agent, url], shell=True)
            return result
        elif os == "Android" :
            result = subprocess.run(["curl","-k","-A", user_agent, url], capture_output=True,text=True,encoding='UTF-8').stdout
            return result
        else:
            headers= {
                    "Upgrade-Insecure-Requests": "1",
                    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0"
                     }
            link = requests.get(url=url, headers=headers).text
            return link

def postURL(url):
        headers = {'Referer': base,
                   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                   'Host': base,
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
        }
        response = requests.post(url=url, data='', headers=headers)
        link = response.text
        return link

def addDir(name, url, mode, iconimage, total=1, pasta=True):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)

        ok = True

        liz = xbmcgui.ListItem(name)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({'icon': iconimage, 'thumb': iconimage })

        #dialog = xbmcgui.Dialog()
        #dialog.ok("addDir Erro:", str(u))

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok


def addDirF(name,url,mode,iconimage,pasta=True,total=1) :
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)
        u = u+"&mode="+str(mode)+"&name="+name+"&iconimage="
        u = u+urllib.quote_plus(iconimage)
        #u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})
        liz.setArt({ 'fanart': iconimage, 'icon': iconimage, 'thumb': iconimage })

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def getInfo(url):
        link = openURL(url)
        titO = re.findall('<meta property="og:title" content="(.*?)" />', link)[0]

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        soup = BeautifulSoup(link, "html.parser")
        #xbmc.log('[plugin.video.filmestorrentbrasil] L589 - ' + str(url), xbmc.LOGINFO)
        #ytID = re.findall(r'data-litespeed-src="https:\/\/www.youtube.com\/embed\/(.*?).feature=oembed"', str(link))[0]
        urlF = soup.iframe['src']
        ytID = urlF.split('/')[4]
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmestorrentBrasil', 'Obtendo Fontes para ' + name + ' Por favor aguarde...')
        mensagemprogresso.update(0)

        mensagemprogresso.update(100, 'Resolvendo fonte para ' + name+ ' Por favor aguarde...')
        mensagemprogresso.close()

        if not ytID :
            addon = xbmcaddon.Addon()
            addonname = addon.getAddonInfo('name')
            line1 = str("Trailer não disponível!")
            xbmcgui.Dialog().ok(addonname, line1)
            return

        mensagemprogresso.update(100)
        mensagemprogresso.close()

        xbmc.executebuiltin('RunPlugin(plugin://plugin.video.youtube/play/?video_id=%s)' % ytID)

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
