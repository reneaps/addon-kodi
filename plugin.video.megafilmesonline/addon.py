#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : MegaFilmesOnline
# By AddonBrasil - 11/12/2015
# Atualizado (1.0.1) - 15/12/2015
# Atualizado (1.1.0) - 12/03/2016
# Atualizado (2.0.0) - 03/08/2018
# Atualizado (2.0.9) - 15/05/2019
# Atualizado (2.1.0) - 19/06/2019
# Atualizado (2.1.1) - 20/07/2019
# Atualizado (2.1.2) - 21/11/2019
# Atualizado (2.1.3) - 26/12/2019
# Atualizado (2.1.4) - 01/04/2020
# Atualizado (2.1.5) - 22/04/2020
# Atualizado (2.1.6) - 09/05/2020
# Atualizado (2.1.7) - 16/07/2020
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib               import jsunpack
from time                        import time

version   = '2.1.6'
addon_id  = 'plugin.video.megafilmesonline'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder  = selfAddon.getAddonInfo('path')
artfolder    = addonfolder + '/resources/img/'
fanart       = addonfolder + '/fanart.png'
base         = base64.b64decode('aHR0cHM6Ly9tZWdhaGRmaWxtZXMudHYv')

############################################################################################################

def menuPrincipal():
        addDir('Categorias'                    , base + ''                      ,   10, artfolder + 'categorias.png')
        addDir('Lançamentos'                   , base + 'filmes/'               ,   20, artfolder + 'lancamentos.png')
        addDir('Filmes Dublados'               , base + '?s=dublado'            ,   20, artfolder + 'pesquisa.png')
        addDir('Seriados'                      , base + 'series/'               ,   25, artfolder + 'legendados.png')
        addDir('Pesquisa Series'               , '--'                           ,   30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'               , '--'                           ,   35, artfolder + 'pesquisa.png')
        addDir('Configurações'                 , base                           ,  999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo'    , base                           , 1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        xbmc.log('[plugin.video.megafilmesonline] L51 ' + str(url), xbmc.LOGNOTICE)
        soup = BeautifulSoup(link)
        conteudo   = soup("div", {"class": "wrap"})
        categorias = conteudo[3]("div", {"class": "cats itemSliderC owl-carousel"})

        categorias = categorias[0]("a")
        totC = len(categorias)
        for categoria in categorias:
                #xbmc.log('[plugin.video.megafilmesonline] L50 ' + str(categoria['href']), xbmc.LOGNOTICE)
                titC = categoria.text.encode('utf-8','replace')
                urlC = categoria["href"]
                imgC = artfolder + limpa(titC) + '.png'
                addDir(titC,urlC,20,imgC)

        setViewMenu()

def getFilmes(url):
        xbmc.log('[plugin.video.megafilmesonline] L65 ' + str(url), xbmc.LOGNOTICE)
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup('div',{'class':'generalMoviesList'})
        filmes = conteudo[0]('a')
        totF = len(filmes)
        for filme in filmes:
                titF = filme.div.span.text.encode('utf-8')
                urlF = filme["href"].encode('utf-8')
                imgF = filme.div.img["data-original"].encode('utf-8')
                addDirF(titF, urlF, 100, imgF, False, totF)

        try :
                proxima = re.findall('193</a><a class="item click" href="(.*?)">&gt;</a>', link)[0]
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link)
        conteudo = soup('div',{'class':'generalMoviesList'})
        filmes = conteudo[0]('a')
        totF = len(filmes)
        for filme in filmes:
                titF = filme.div.span.text.encode('utf-8')
                urlF = filme["href"].encode('utf-8')
                imgF = filme.div.img["data-original"].encode('utf-8')
                addDir(titF, urlF, 26, imgF)

        try :
                proxima = re.findall('>8</a><a class="item click" href="(.*?)">&gt;</a>', link)[0]
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

def getTemporadas(name, url, iconimage):
        xbmc.log('[plugin.video.megafilmesonline] L114 ' + str(url), xbmc.LOGNOTICE)
        link  = openURL(url)
        soup = BeautifulSoup(link)
        conteudo = soup('div',{'id':'playerArea'})
        urlF = conteudo[0].iframe['src']

        #imgF = ""
        #imgF = re.findall(r'<meta property="og:image" content="(.*?)" />', link)
        imgF = iconimage

        link  = openURL(urlF)
        soup = BeautifulSoup(link)
        conteudo = soup('div',{'class':'seasonList'})
        seasons = conteudo[0]('div',{'class':'item'})
        totD = len(seasons)

        i = 1
        while i <= totD:
            titF = name + "&" + str(i) + "ª Temporada"
            try:
                addDir(titF, urlF, 27, imgF)
            except:
                pass
            i = i + 1

def getEpisodios(name, url, iconimage):
        xbmc.log('[plugin.video.megafilmesonline] L134 ' + str(url), xbmc.LOGNOTICE)
        sea = name.split('&')[-1]
        texto = name.split('&')[0]
        texto = texto.replace('ç','c').replace('ã','a').replace('õ','o')
        texto = texto.replace('â','a').replace('ê','e').replace('ô','o')
        texto = texto.replace('á','a').replace('é','e').replace('í','i')
        name = texto.replace('ó','o').replace('ú','u')
        n = sea.replace('ª Temporada', '')
        n = int(n)
        n = (n-1)
        s = n
        temp = []
        episodios = []

        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')

        soup = BeautifulSoup(link)
        
        '''
        conteudo = soup('div',{'id':'playerArea'})
        urlF = conteudo[n].iframe['src']        
        imgF = ""

        link  = openURL(urlF)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        '''
        imgF = iconimage
        conteudo = soup('div',{'class':'seasonList'})
        epis = conteudo[0]('div',{'class':'item'})
        b = epis[n]['onclick']
        episode = re.findall('getEpisodeList\((.*?)\)', b)[0]
        episode = episode.split(',')
        #listaepis = soup('div',{'class':'episodeList'})
        tmdb = episode[1]
        tmdb = tmdb.replace(' ', '').replace("'",'')
        season = episode[2]
        season = season.replace(' ', '')
        headers = {'Referer': url,
                   'content-type': 'application/json; charset=UTF-8',
                   'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        urlV = 'https://megahdfilmes.tv/wp-json/api/tvshows?what=epsodes&tmdb=%s&season=%s&version=5' % (tmdb,season)
        r = requests.get(urlV,headers)
        js = json.loads(r.text)
        js = js['episodes']
        xbmc.log('[plugin.video.megafilmesonline] L173 ' + str(js), xbmc.LOGNOTICE)
        for i in js:
                titF = name + ' ' + 'T' + str(n+1) + 'E' + i['ep']
                urlF = i['player'][0]['url']
                if urlF == "" : titF = titF + ">>Indisponivel"
                temp = (urlF, titF)
                episodios.append(temp)

        total = len(episodios)

        for url, titulo in episodios:
                #xbmc.log('[plugin.video.megafilmesonline] L186 ' + str(url), xbmc.LOGNOTICE)
                addDirF(titulo, url, 110, imgF, False, total)

def pega(post_id,idname):
    data = urllib.urlencode({'id':post_id,'players':idname})
    urlF = 'https://www.filmesonlinehdx.org/wp-content/themes/vizeratt/inc/parts/single/player_post.php'
    req = urllib2.Request(url=urlF,data=data)
    req.add_header('Referer',url)
    req.add_header('content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36')
    response = urllib2.urlopen(req)
    content = response.read()
    response.close()
    soup = BeautifulSoup(content)
    #xbmc.log('[plugin.video.megafilmesonline] L200 ' + str(soup), xbmc.LOGNOTICE)
    okID = soup.a['href']
    okID = okID.split('token=')[1]
    urlF = base64.b64decode(okID)
    #xbmc.log('[plugin.video.megafilmesonline] L205 ' + str(urlF), xbmc.LOGNOTICE)
    if 'video.php?v=' in urlF :
            okID = urlF.split('video.php?v=')[1]
            okID = okID.split('&')[0]
            #xbmc.log('[plugin.video.megafilmesonline] L208 ' + str(okID), xbmc.LOGNOTICE)
            urlF = base64.b64decode(okID)
    return urlF


def pesquisa():
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto     = keyb.getText()
                pesquisa = urllib.quote(texto)
                url         = base + '?s=%s' % str(pesquisa)

                hosts = []
                link  = openURL(url)
                link = unicode(link, 'utf-8', 'ignore')
                soup = BeautifulSoup(link)
                conteudo = soup('div',{'class':'generalMoviesList'})
                filmes = conteudo[0]('a')
                totF = len(filmes)

                for filme in filmes:
                        titF = filme.div.span.text.encode('utf-8')
                        urlF = filme["href"].encode('utf-8')
                        imgF = filme.div.img["data-original"].encode('utf-8')
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

def doPesquisaFilmes():
        a = pesquisa()
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 100, img, False, total)
        setViewFilmes()

def player(name,url,iconimage):
        xbmc.log('[plugin.video.megafilmesonline] L256 ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MegaFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        link  = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link)
        conteudo = soup('div',{'class':'playerBtn stream'})
        len(conteudo)
        b = conteudo[0]['onclick']
        c = re.findall('getPlayer\(\'(.*?)\',.+\)', b)[0]
        url2 = 'https://megahdfilmes.tv/api-embed/?action=modal&what=iframe&type=stream&id=%s' % c
        urlF = base64.b64decode(c)
        fxID = urlF.split('/e/')[-1]
        #urlF = 'https://player-megahdfilmes.com/api/source/%s' % fxID
        urlF = 'https://streamtape.com/e/%s' % fxID
        headers = {'Referer': url2,
                    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        }
        r = requests.get(urlF,headers)
        urlF = re.findall(r'<div id="videolink" style="display:none;">(.*?)</div>', r.text)[0]
        urlF = 'http:%s' % urlF if urlF.startswith("//") else urlF
        xbmc.log('[plugin.video.megafilmesonline] L286 - ' + str(urlF), xbmc.LOGNOTICE)
        #dados = {}
        #dados = r.text
        #js = json.loads(dados)
        #js = js['data']   
        try:
            lg = json.loads(dados)
            lg['captions']
            lgID = lg['captions'][0]['id']
            lgHA = lg['captions'][0]['hash']
            legendas = 'https://player-megahdfilmes.com/asset/userdata/260169/caption/%s/%s.srt' % (lgHA,lgID)
            xbmc.log('[plugin.video.megafilmesonline] L282 - ' + str(legendas), xbmc.LOGNOTICE)
        except:
            legendas = False
            pass
        qual = []
        urlVideo = []
        '''
        for i in js:
                urlVideo.append(i['file'])
                qual.append(str(i['label']))
        if qual == None : return
        '''
        qual = ['Player 1']
        urlVideo = urlF

        index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)

        if index == -1 : return

        i = index

        #url2Play = urlVideo[i]
        url2Play = urlVideo
        
        OK = False
    
        xbmc.log('[plugin.video.megafilmesonline] L303 ' + str(url2Play), xbmc.LOGNOTICE)

        mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
        
     
        if OK : url2Play = urlresolver.resolve(urlVideo)

        xbmc.log('[plugin.video.megafilmesonline] L310 ' + str(url2Play), xbmc.LOGNOTICE)

        if not url2Play : return

        if not legendas : legendas = '-'

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
        xbmc.log('[plugin.video.megafilmesonline] L347 ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('MegaFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)

        titsT = []
        idsT = []

        urlF = url
        fxID = urlF.split('/v/')[-1]
        urlF = 'https://player-megahdfilmes.com/api/source/%s' % fxID
        r = requests.post(urlF)
        dados = {}
        dados = r.text
        js = json.loads(dados)
        js = js['data']   
        try:
            lg = json.loads(dados)
            lg['captions']
            lgID = lg['captions'][0]['id']
            lgHA = lg['captions'][0]['hash']
            legendas = 'https://player-megahdfilmes.com/asset/userdata/260169/caption/%s/%s.srt' % (lgHA,lgID)
            xbmc.log('[plugin.video.megafilmesonline] L370 - ' + str(legendas), xbmc.LOGNOTICE)
        except:
            legendas = False
            pass
        qual = []
        urlVideo = []
        for i in js:
                urlVideo.append(i['file'])
                qual.append(str(i['label']))
        if qual == None : return

        index = xbmcgui.Dialog().select('Selecione uma das qualidades suportadas :', qual)

        if index == -1 : return

        #xbmc.log('[plugin.video.megafilmesonline] L532 - ' + str(urlVideo), xbmc.LOGNOTICE)
        i = index

        xbmc.log('[plugin.video.megafilmesonline] L388 - ' + str(i), xbmc.LOGNOTICE)

        url2Play = urlVideo[i]
        
        OK = False

        if OK : url2Play = urlresolver.resolve(urlVideo)

        if not url2Play : return

        if not legendas : legendas = '-'

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

        liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)

        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type = "Video", infoLabels = {"title": name})

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

        return ok

def addDirF(name,url,mode,iconimage,pasta=True,total=1) :
        u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name, iconImage="iconimage", thumbnailImage=iconimage)

        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type="Video", infoLabels={"Title": name})

        cmItems = []

        cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
        cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))

        liz.addContextMenuItems(cmItems, replaceItems=False)

        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)

        return ok

def getInfo(url)    :
        link = openURL(url)
        titO = re.findall('<h2 class="title">(.*?)</h2>', link)[0]

        xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
        link = openURL(url)
        ytID = re.findall('<a id="open-trailer" class="btn iconized trailer" data-trailer="https://www.youtube.com/embed/(.*?)rel=0&amp;controls=1&amp;showinfo=0&autoplay=0"><b>Trailler</b> <i class="icon fa fa-play"></i></a>', link)[0]
        ytID = ytID.replace('?','')

        xbmc.executebuiltin('XBMC.RunPlugin("plugin://script.extendedinfo/?info=youtubevideo&&id=%s")' % ytID)

def setViewMenu() :
        xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

        opcao = selfAddon.getSetting('menuVisu')

        if     opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
        elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
        elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def setViewFilmes() :
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')

        opcao = selfAddon.getSetting('filmesVisu')

        if     opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
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
        texto = texto.replace('á','a').replace('é','e').replace('í','i')
        texto = texto.replace('ó','o').replace('ú','u')
        texto = texto.replace(' ','-')
        texto = texto.lower()

        return texto

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

params      = get_params()
url          = None
name      = None
mode      = None
iconimage = None

try       : url=urllib.unquote_plus(params["url"])
except : pass
try       : name=urllib.unquote_plus(params["name"])
except : pass
try       : mode=int(params["mode"])
except : pass
try       : iconimage=urllib.unquote_plus(params["iconimage"])
except : pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)

###############################################################################################################

if     mode == None : menuPrincipal()
elif mode == 10      : getCategorias(url)
elif mode == 20      : getFilmes(url)
elif mode == 25      : getSeries(url)
elif mode == 26      : getTemporadas(name, url, iconimage)
elif mode == 27      : getEpisodios(name, url, iconimage)
elif mode == 30      : doPesquisaSeries()
elif mode == 35      : doPesquisaFilmes()
elif mode == 40      : getFavoritos()
elif mode == 41      : addFavoritos(name,url,iconimage)
elif mode == 42      : remFavoritos(name,url,iconimage)
elif mode == 43      : cleanFavoritos()
elif mode == 98      : getInfo(url)
elif mode == 99      : playTrailer(name,url,iconimage)
elif mode == 100     : player(name,url,iconimage)
elif mode == 110     : player_series(name, url, iconimage)
elif mode == 999     : openConfig()
elif mode == 1000    : openConfigEI()

xbmcplugin.endOfDirectory(int(sys.argv[1]))