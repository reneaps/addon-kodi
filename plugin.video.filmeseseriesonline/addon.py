#####################################################################
#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : Filmes e Series Online
# By AddonReneSilva - 01/10/2016
# Atualizado (1.0.0) - 01/10/2016
# Atualizado (1.2.0) - 01/05/2018
# Atualizado (1.2.1) - 03/06/2018
# Atualizado (1.2.2) - 28/07/2018
# Atualizado (1.2.3) - 10/03/2019
# Atualizado (1.2.4) - 07/04/2019
# Atualizado (1.2.5) - 16/04/2019
# Atualizado (1.2.6) - 02/05/2019
# Atualizado (1.2.7) - 13/05/2019
# Atualizado (1.2.8) - 14/05/2019
# Atualizado (1.3.0) - 31/08/2019
# Atualizado (1.3.1) - 08/09/2019
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver

from bs4                import BeautifulSoup
from resources.lib      import jsunpack

import socket
socket.setdefaulttimeout(60)

version      = '1.3.0'
addon_id     = 'plugin.video.filmeseseriesonline'
selfAddon    = xbmcaddon.Addon(id=addon_id)
addonfolder  = selfAddon.getAddonInfo('path')
artfolder    = addonfolder + '/resources/media/'
fanart       = addonfolder + '/resources/media/fanart.png'
addon_handle = int(sys.argv[1])
base         = base64.b64decode('aHR0cHM6Ly9maWxtZXNvbmxpbmVzZXJpZXMubmV0')

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                 , base                              ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + '/filmes/lancamentos/'      ,   20, artfolder + 'ultimos.png')
        addDir('Filmes em HD'               , base + '/filmes/filmes-hd/'       ,   20, artfolder + 'filmes.png')
        addDir('Filmes Dublados'            , base + '/?s=dublado&tipo=video'   ,   20, artfolder + 'filmes.png')
        addDir('Series'                     , base + '/series-hd/'              ,   25, artfolder + 'series.png')
        addDir('Pesquisa Series'            , '--'                              ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                              ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                              ,  999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo' , base                              , 1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup("div", {"class": "container"})
        arquivo = conteudo[4]("div", {"class": "lista-amigos"})
        categorias = arquivo[0]("a")

        totC = len(categorias)

        for categoria in categorias:
                titC = categoria.span.text.encode('utf-8','replace')
                titC = titC.replace('Assistir Filmes ', '').replace('Online ', '')
                titC = titC.replace('de ', '').replace('Assistir ', '')

                if not 'Lançamento' in titC :
                    if not 'Séries' in titC:
                        if not 'Filmes' in titC:
                            urlC = categoria["href"]
                            imgC = "" #categoria.img["src"]
                            addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup("div", {"class": "filmes"})
        filmes = conteudo[0]("div", {"class": "item"})

        totF = len(filmes)

        for filme in filmes:
                titF = filme.a.text.encode('utf-8','replace')
                titF = titF.replace('Assistir ','').replace('Filme ','')
                urlF = filme.a["href"].encode('utf-8', 'ignore')
                pltF = sinopse(urlF)
                imgF = filme.img["src"].encode('utf-8', 'ignore')
                addDirF(titF, urlF, 100, imgF, False, totF, pltF)

        try :
                proxima = re.findall('<a class="next page-numbers" href="(.*?)"', link)[0]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup("div", {"class": "filmes"})
        filmes = conteudo[0]("div", {"class": "item"})

        totF = len(filmes)

        for filme in filmes:
                titF = filme.a.text.encode('utf-8','replace')
                titF = titF.replace('Assistir ','').replace('Filme ','')
                urlF = filme.a["href"].encode('utf-8', 'ignore')
                imgF = filme.img["src"].encode('utf-8', 'ignore')
                addDir(titF, urlF, 26, imgF)

        try :
                proxima = re.findall('<a class="next page-numbers" href="(.*?)"', link)[0]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')

def getTemporadas(url):
        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup.find("ul", {"class": "tabs"})
        temporadas = conteudo("li")
        totF = len(temporadas)
        img = soup.find("div", {"class": "capa-thumb"})
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
        n = re.findall(r'(.+?)ª Temporada', name)[0]
        n = int(n)
        if n > 0 : n = (n-1)
        temp = []
        episodios = []

        html  = openURL(url)
        link = unicode(html, 'utf-8', 'ignore')

        name = re.findall(r'<div class="content clearfix"><h2 style="font-family: Open Sans; font-size: 16px;">(.+?)<\/h2>', str(html))[0]
        soup = BeautifulSoup(link, "html5lib")
        conteudo = soup('div',{'class':'tab_content'})
        texto = str(conteudo)
        texto1 = texto.replace('<div class="tab_content"></div>','')
        texto2 = BeautifulSoup(texto1, "html5lib")
        conteudo = texto2('div',{'class':'tab_content'})
        arquivo = conteudo[n]('div',{'class':'um_terco'})

        imgF = ""
        img = soup.find("div", {"class": "capa-post"})
        imgF = img.img['src']
        img = imgF

        try:
            dublados = arquivo[0]('li')
            au = arquivo[0].text
            result= re.split(r'Epi', au)
            audio = result[0].encode('utf-8', 'ignore')
            audio = audio.replace('\\xaa','ª')

            for link in dublados:
                if link.a.text != "" :
                    url = link.a["href"].encode('utf-8', 'ignore')
                    titulo = link.a.text.encode('utf-8', 'ignore').replace('\\xf3','ó')
                    titulo = name+" "+audio+" "+titulo
                    temp = (url, titulo)
                    episodios.append(temp)

        except:
            pass
        try:
            legendados = arquivo[1]('li')
            au = arquivo[1].text
            result= re.split(r'Epi', au)
            audio = result[0].encode('utf-8')
            audio = audio.replace('\\xaa','ª')

            for link in legendados:
                if link.a.text != "" :
                    url = link.a["href"].encode('utf-8', 'ignore')
                    titulo = link.a.text.encode('utf-8', 'ignore').replace('\\xf3','ó')
                    titulo = name +" "+audio+" "+titulo
                    temp = (url, titulo)
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
                url      = base + '?s=%s&tipo=video' % str(pesquisa)

                link  = openURL(url)
                link = unicode(link, 'utf-8', 'ignore')

                soup = BeautifulSoup(link, "html5lib")
                conteudo = soup("div", {"class": "filmes"})
                filmes = conteudo[0]("div", {"class": "item"})

                totF = len(filmes)
                hosts = []
                for filme in filmes:
                    titF = filme.a.text.encode('utf-8','replace')
                    titF = titF.replace('Assistir ','').replace('Filme ','')
                    urlF = filme.a["href"].encode('utf-8', 'ignore')
                    imgF = filme.img["src"].encode('utf-8', 'ignore')
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
        total = len(a)
        for url2, titulo, img in a:
            addDirF(titulo, url2, 100, img, False, total)

        setViewFilmes()

def player(name,url,iconimage):
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmesESeriesOnline', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []

        link     = openURL(url)
        soup     = BeautifulSoup(link, "html5lib")
        conteudo = soup("div", {"class": "embeds-servidores"})
        srvsdub  = conteudo[0]("iframe")
        url = srvsdub[0]['src']

        link = openURL(url)
        soup  = BeautifulSoup(link, "html5lib")

        try :
            conteudo = soup("div", {"class": "geral"})
            srvsdub  = conteudo[0]("a")
            totD = len(srvsdub)
            for i in range(totD) :
                titS = srvsdub[i].text
                idS = srvsdub[i]["id"]
                titsT.append(titS)
                idsT.append(idS)
        except :
            pass

        try :
            conteudo = soup("div", {"class": "geral'"})
            srvsleg  = conteudo[0]("a")
            totL = len(srvsleg)
            for i in range(totL) :
                titS = srvsdub[i].text
                idS = srvsleg[i]["id"]
                titsT.append(titS)
                idsT.append(idS)
        except :
            pass

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        conteudo = soup("div", {"class": "geral"})
        links = conteudo[0]("a")

        if len(links) == 0 : links = conteudo[0]("a")
        i = int(index)
        urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]

        xbmc.log('[plugin.video.filmeseseriesonline] L332 - ' + str(urlVideo), xbmc.LOGNOTICE)

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

        elif 'rapidvideo' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://www.rapidvideo.com/?v=%s' % fxID

        elif 'videoplayer=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://www.fembed.com/v/%s' % fxID

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

        elif 'vidoza' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://vidoza.net/embed-%s.html' % fxID

        elif 'vidlox' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'http://vidlox.tv/embed-%s' % fxID

        elif 'vcstream=' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://vcstream.to/embed/%s' % fxID

        elif 'verystream' in urlVideo:
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://verystream.com/e/%s' % fxID

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
                url2Play = re.findall('var vldAb="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                url2Play = 'http:%s' % url if url.startswith("//") else url

                OK = False

        xbmc.log('[plugin.video.filmeseseriesonline] L393 - ' + str(urlVideo), xbmc.LOGNOTICE)

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
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('FilmesESeriesOnline', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []
        links = []
        hosts = []

        link = openURL(url)
        soup  = BeautifulSoup(link, "html5lib")

        try :
                conteudo = soup("div", {"class": "geral"})
                srvsdub  = conteudo[0]("a")
                totD = len(srvsdub)
                for i in range(totD) :
                        titS = srvsdub[i].text
                        idS = srvsdub[i]["id"]
                        titsT.append(titS)
                        idsT.append(idS)
        except :
                pass

        try :
                conteudo = soup("div", {"class": "geral'"})
                srvsleg  = conteudo[0]("a")
                totL = len(srvsleg)
                for i in range(totL) :
                        titS = srvsdub[i].text
                        idS = srvsleg[i]["id"]
                        titsT.append(titS)
                        idsT.append(idS)
        except :
                pass

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return

        conteudo = soup("div", {"class": "geral"})
        links = conteudo[0]("a")

        if len(links) == 0 : links = conteudo[0]("a")

        i = int(index)

        urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]

        xbmc.log('[plugin.video.filmeseseriesonline] L492 - ' + str(urlVideo), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

        if 'openload' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://openload.co/embed/%s' % fxID

        elif 'raptu.com' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://www.raptu.com/?v=%s' % fxID

        elif 'rapidvideo' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://www.rapidvideo.com/?v=%s' % fxID

        elif 'verystream' in urlVideo:
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://verystream.com/e/%s' % fxID

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

        elif 'thevid' in urlVideo :
                fxID = urlVideo.split('=')[1]
                urlVideo = 'https://thevid.net/e/%s' % fxID
                linkTV  = openURL(urlVideo)
                sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
                aMatches = re.compile(sPattern).findall(linkTV)
                sUnpacked = jsunpack.unpack(aMatches[1])
                url2Play = re.findall('var vldAb="(.*?)"', sUnpacked)
                url = str(url2Play[0])
                url2Play = 'http:%s' % url if url.startswith("//") else url

                OK = False

        xbmc.log('[plugin.video.filmeseseriesonline] L558 - ' + str(urlVideo), xbmc.LOGNOTICE)

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
        req = urllib2.Request(url)
        req.add_header('Referer',url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

def addDir(name, url, mode, iconimage, total=1, pasta=True):
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True
        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels={"title": name})
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)
        return ok

def addDirF(name,url,mode,iconimage,pasta=True,total=1,plot='') :
        u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name, iconImage="iconimage", thumbnailImage=iconimage)

        liz.setProperty('fanart_image', iconimage)
        #liz.setInfo(type="Video", infoLabels={"Title": name})
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})

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

        #xbmc.executebuiltin('XBMC.RunPlugin("plugin://script.extendedinfo/?info=youtubevideo&&id=%s")' % ytID)
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
        #conteudo = soup("div", {"class": "content clearfix"})
        try:
            p = soup('p', limit=5)[1]
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