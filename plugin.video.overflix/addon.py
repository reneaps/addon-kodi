#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : OverFlix
# By AddonBrasil - 08/05/2019
# Atualizado (1.0.0) - 08/05/2019
# Atualizado (1.0.1) - 10/05/2019
# Atualizado (1.0.1) - 12/05/2019
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests
import resources.lib.moonwalk as moonwalk

from bs4 import BeautifulSoup
from resources.lib import jsunpack
from time import time

version   = '1.0.2'
addon_id  = 'plugin.video.overflix'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/resources/fanart.png'
base        = base64.b64decode('aHR0cHM6Ly9vdmVyZmxpeC5uZXQv')
sbase       = 'navegar/series-2/?alphabet=all&sortby=v_started&sortdirection=desc'
v_views     = 'navegar/filmes-1/?alphabet=all&sortby=v_views&sortdirection=desc'

############################################################################################################

def menuPrincipal():
        addDir('Categorias Filmes'          , base + 'navegar/filmes-1/'             ,        10, artfolder + 'categorias.png')
        addDir('Categorias Series'          , base + sbase                           ,        10, artfolder + 'categorias.png')
        addDir('Lançamentos'                , base + 'categoria/50-lancamentos/'     ,        20, artfolder + 'lancamentos.png')
        addDir('Filmes Dublados'            , base + 'categoria/56-filmes-dublados/' ,        20, artfolder + 'pesquisa.png')
        addDir('Filmes Mais Assistidos'     , base + v_views                         ,        20, artfolder + 'pesquisa.png')
        addDir('Series'                     , base + sbase                           ,        25, artfolder + 'legendados.png')
        addDir('Pesquisa Series'            , '--'                                   ,        30, artfolder + 'pesquisa.png')
        addDir('Pesquisa Filmes'            , '--'                                   ,        35, artfolder + 'pesquisa.png')
        addDir('Configurações'              , base                                   ,       999, artfolder + 'config.png', 1, False)
        addDir('Configurações ExtendedInfo' , base                                   ,      1000, artfolder + 'config.png', 1, False)

        setViewMenu()

def getCategorias(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        if 'filmes' in url :
            conteudo   = soup("ul",{"id":"elNavigation_18_menu"})
        if 'series' in url :
            conteudo   = soup("ul",{"id":"elNavigation_19_menu"})
        categorias = conteudo[0]("li")

        for categoria in categorias:
                titC = categoria.a.text.encode('utf-8','')
                urlC = categoria.a["href"]
                imgC = artfolder + limpa(titC) + '.png'
                if 'filmes' in url:
                    addDir(titC,urlC,20,imgC)
                elif 'series' in url:
                    addDir(titC,urlC,25,imgC)

        setViewMenu()

def getFilmes(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', attrs={'class':'ipsGrid ipsPad_half'})
        filmes = conteudo[0]('div', attrs={'class':'vbItemImage'})
        totF = len(filmes)

        for filme in filmes:
                titF = filme.a['title'].encode("utf-8")
                titF = titF.replace('Assistir','').replace('Online','')
                urlF = filme.a['href'].encode("utf-8")
                image_news = filme('div', {'class':'vb_image_container'})[0]
                imgF = re.findall(r'url\(\'(.+?)\'\);',str(image_news))[0].encode("utf-8")
                addDirF(titF, urlF, 100, imgF, False, totF)

        try :
                next_page = soup('li', attrs={'class':'ipsPagination_next'})[0]
                proxima = next_page.a['href']
                addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
        except :
                pass

        setViewFilmes()

def getSeries(url):
        link = openURL(url)
        link = unicode(link, 'utf-8', 'ignore')        
        soup = BeautifulSoup(link, 'html.parser')
        conteudo = soup('div', attrs={'class':'ipsGrid ipsPad_half'})
        filmes = conteudo[0]('div', attrs={'class':'vbItemImage'})

        for filme in filmes:
                titF = filme.a["title"].encode("utf-8")
                titF = titF.replace('Assistir','').replace('Online','')
                urlF = filme.a["href"].encode('utf-8')
                image_news = filme('div', {'class':'vb_image_container'})[0]
                imgF = re.findall(r'url\(\'(.+?)\'\);',str(image_news))[0]
                addDir(titF, urlF, 26, imgF)

        try :
                next_page = soup('li', attrs={'class':'ipsPagination_next'})[0]
                proxima = next_page.a['href']
                addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
        except :
                pass

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(name,url,iconimage):
        html = openURL(url)
        soup = BeautifulSoup(html,'html.parser')
        sname = soup.title.text.replace('-','|').split('|')[0]
        sname = sname.replace('Assistir','').replace('Online','')
        data = soup('div', {'class':'ipsColumns ipsColumns_collapsePhone'})
        url = data[0]('a',{'class':'btnn iconized assistir'})[0]['href']
        html = openURL(url)
        soup = BeautifulSoup(html, 'html.parser')
        conteudo = soup('div', attrs={'class':'box'})
        filmes = conteudo[0]('li')
        totF = len(filmes)
        imgF = data[0].img['src']
        urlF = url
        i = 1
        while i <= totF:
                titF = str(i) + "ª Temporada " + sname.encode('utf-8')
                try:
                    addDirF(titF, urlF, 27, imgF, True, totF)
                except:
                    pass
                i = i + 1
                
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
        n = re.findall(r'(.+?)ª Temporada.+', name)[0]
        link = openURL(url)
        soup = BeautifulSoup(link,'html.parser')
        sname = soup.title.text.replace('-','|').split('|')[0]
        sname = sname.replace('Assistir','').replace('Online','')
        sname = sname.encode('utf-8')
        links = re.findall(r'addiframe\(\'(.+?)\'\);', link)
        imgF = iconimage
        epis = re.findall(r'<a class="video" href="javascript: InitPlayer\(\'(.+?)\', \'(.+?)\',\'(.+?)\'\);">(.+?)</a>', link)
        totF = len(links)
        for i in range(0, totF):
            if n in str(epis[i][0]) :
                if not "ximo" in str(epis[i][3]) :
                    titS = epis[i][0]
                    titE = epis[i][1]
                    titT = epis[i][2]
                    titF = epis[i][3]
                    titF = sname.encode('utf-8') + ' T' + n + ' ' +  titT.replace('dub', '(D)').replace('leg', '(L)') + " - " + titF
                    urlF = links[i]
                    addDirF(titF, urlF, 110, imgF, False, totF)

        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
        
def pesquisa():
        hosts = []
        temp = []
        keyb = xbmc.Keyboard('', 'Pesquisar Filmes/Series')
        keyb.doModal()

        if (keyb.isConfirmed()):
                texto = keyb.getText()
                pesquisa = urllib.quote(texto)

                data = urllib.urlencode({'term':pesquisa})
                url = base + 'findContent/' 

                headers = {'Referer': url, 
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                r = requests.post(url=url, data=data, headers=headers)
                html = r.content
                soup = BeautifulSoup(html, 'html.parser')
                conteudo = soup('div', {'class':'videoboxGridview'})
                itens = conteudo[0]('div', {'class':'vbItemImage'})
                for i in itens:
                        a = i.div['style']
                        imgF = re.findall(r'.+url\(\'(.+?)\'\)',a)[0].encode('utf-8')
                        urlF = i.a['href'].encode('utf-8')
                        titF = i.a['title']+' '+i.span.text
                        titF = titF.encode('utf-8')
                        titF = titF.replace('Assistir','').replace('Online','')
                        temp = [urlF, titF, imgF]
                        hosts.append(temp)

                return hosts

def doPesquisaSeries():
        a = pesquisa()
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 26, img, False, total)
            
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
        
def doPesquisaFilmes():
        a = pesquisa()
        total = len(a)
        for url2, titulo, img in a:
            addDir(titulo, url2, 100, img, False, total)

        setViewFilmes()

def player(name,url,iconimage):
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('OverFlix', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)
        titsT = []
        idsT = []
        
        urlF = url+'?&area=online'
        xbmc.log('[plugin.video.overflix] L227 - ' + str(urlF), xbmc.LOGNOTICE)
        link = openURL(urlF)
        soup = BeautifulSoup(link, 'html.parser')
        #data = soup('div', {'class':'ipsColumns ipsColumns_collapsePhone'})
        #btn = data[0]('a',{'class':'btnn iconized assistir'})[0]['href']
        data = soup.iframe
        btn = data['src']
        xbmc.log('[plugin.video.overflix] L234 - ' + str(btn), xbmc.LOGNOTICE)
        try:
            ss = btn.split('/?')[1].split('&')
            for s in ss:
                hname = s.split('=')[0]
                if 'down' not in hname:
                    hkey = s.split('=')[1]
                    titsT.append(hname)
                    idsT.append(hkey)

            if not titsT : return

            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

            if index == -1 : return

            i = int(index)
            urlVideo = titsT[i]

            if 'verystream' in urlVideo:
                fxID = str(idsT[i])
                urlVideo = 'https://verystream.com/e/%s' % fxID

            elif 'streamango' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://streamango.com/embed/%s' % fxID
                
            elif 'rapidvideo' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID
                 
            elif 'mystream' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://mstream.cloud/%s' % fxID
                r = requests.get(urlVideo)
                data = r.content
                srv = re.findall('<meta name="og:image" content="([^"]+)">', data)[0]
                url2Play = srv.replace('/img','').replace('jpg','mp4')
                OK = False
                
            elif 'thevid' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://thevid.net/e/%s' % fxID
                 
            elif 'openload' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://openload.co/embed/%s' % fxID
 
            elif 'vidoza' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://vidoza.net/embed-%s.html' % fxID
                                       
            elif 'jetload' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://jetload.net/e/%s' % fxID
                xbmc.log('[plugin.video.overflix] L289 - ' + str(urlVideo), xbmc.LOGNOTICE)
                data = openURL(urlVideo)
                srv = re.findall('id="srv" value="([^"]+)"', data)[0]
                file_name = re.findall('file_name" value="([^"]+)"', data)[0]
                file_low = re.findall('id="file_low" value="([^"]+)"', data)[0]
                file_med = re.findall('id="file_med" value="([^"]+)"', data)[0]
                file_high = re.findall('id="file_high" value="([^"]+)"', data)[0]
                try:
                    id_srv = re.findall('id="srv_id" value="([^"]+)"', data)[0]
                except:
                    id_srv = ''
                    pass
                if id_srv != '' : 
                    url = 'https://jetload.net/api/download'
                    data = urllib.urlencode({"file_name":file_name+'.mp4',"srv":id_srv})
                    headers = {'Referer': urlVideo, 
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                    xbmc.log('[plugin.video.overflix] L310 - ' + str(urlVideo), xbmc.LOGNOTICE)
                    r = requests.post(url=url, data=data, headers=headers)
                    tipo = r.text
                    ext = tipo.split('?')[0]
                    ext2 = tipo.split('?')[1]
                    head = {'Referer': urlVideo,
                            'Content-Type': 'video/mp4',
                            'Connection': 'keep-alive',
                            'Origin': 'https://jetload.net',
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                    head2 = urllib.urlencode(head)
                    url2Play = tipo #ext+'.mp4?'+ext2+'|'+head2
                    urlVideo =[]
                    '''
                    https://jetload.net/#!/d/37AQFHdsoCwT
                    https://jetload.net/api/get_direct_video/37AQFHdsoCwT
                    '''
                    if file_high == '1'  :
                        url2Play = srv+'/v2/schema/'+file_name+'/master.m3u8'
                    elif file_med == '1' :
                        url2Play = srv+'/v2/schema/'+file_name+'/med.m3u8'
                    elif file_low == '1' :
                        url2Play = srv+'/v2/schema/'+file_name+'/low.m3u8'

                OK = False
                
            elif 'principal' in urlVideo :
                fxID = str(idsT[i+1])
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID
                
            xbmc.log('[plugin.video.overflix] L341 - ' + str(urlVideo), xbmc.LOGNOTICE)
        except:
            pass
        
        try:
            value = re.findall(r'<a style=".+?" href="(.+?)" class="btn iconized download" rel="nofollow" target="_blank"><i class="icon fa fa-download"></i> Baixar</a>', link)
            urlVideo = value[0]
        except:
            pass

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        if not url2Play : return

        xbmc.log('[plugin.video.overflix] L362 - ' + str(url2Play), xbmc.LOGNOTICE)

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
        xbmc.sleep(20000)
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
        xbmc.log('[plugin.video.overflix] L398 - ' + str(url), xbmc.LOGNOTICE)
        OK = True
        mensagemprogresso = xbmcgui.DialogProgress()
        mensagemprogresso.create('OverFlix', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
        mensagemprogresso.update(0)
        titsT = []
        idsT = []

        btn = url
        xbmc.log('[plugin.video.overflix] L407 - ' + str(btn), xbmc.LOGNOTICE)
        try:
            ss = btn.split('/?')[1].split('&')
            for s in ss:
                hname = s.split('=')[0]
                if 'down' not in hname:
                    hkey = s.split('=')[1]
                    titsT.append(hname)
                    idsT.append(hkey)

            if not titsT : return

            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

            if index == -1 : return

            i = int(index)
            urlVideo = titsT[i]

            if 'verystream' in urlVideo:
                fxID = str(idsT[i])
                urlVideo = 'https://verystream.com/e/%s' % fxID

            elif 'streamango' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://streamango.com/embed/%s' % fxID
                
            elif 'rapidvideo' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID

            elif 'mystream' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://mstream.cloud/%s' % fxID
                r = requests.get(urlVideo)
                data = r.content
                srv = re.findall('<meta name="og:image" content="([^"]+)">', data)[0]
                url2Play = srv.replace('/img','').replace('jpg','mp4')
                OK = False
                
            elif 'thevid' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://thevid.net/e/%s' % fxID
                 
            elif 'openload' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://openload.co/embed/%s' % fxID
 
            elif 'vidoza' in urlVideo :
                    fxID = str(idsT[i])
                    urlVideo = 'https://vidoza.net/embed-%s.html' % fxID
                                       
            elif 'jetload' in urlVideo :
                fxID = str(idsT[i])
                urlVideo = 'https://jetload.net/e/%s' % fxID
                xbmc.log('[plugin.video.overflix] L462 - ' + str(urlVideo), xbmc.LOGNOTICE)
                data = openURL(urlVideo)
                srv = re.findall('id="srv" value="([^"]+)"', data)[0]
                file_name = re.findall('file_name" value="([^"]+)"', data)[0]
                file_low = re.findall('id="file_low" value="([^"]+)"', data)[0]
                file_med = re.findall('id="file_med" value="([^"]+)"', data)[0]
                file_high = re.findall('id="file_high" value="([^"]+)"', data)[0]
                try:
                    id_srv = re.findall('id="srv_id" value="([^"]+)"', data)[0]
                except:
                    id_srv = ''
                    pass

                if id_srv != '' : 
                    url = 'https://jetload.net/api/download'
                    data = urllib.urlencode({"file_name":file_name+'.mp4',"srv":id_srv})
                    headers = {'Referer': urlVideo, 
                           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                           'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                           'Connection': 'keep-alive',
                           'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                    xbmc.log('[plugin.video.overflix] L484 - ' + str(data), xbmc.LOGNOTICE)
                    r = requests.post(url=url, data=data, headers=headers)
                    tipo = r.text
                    ext = tipo.split('?')[0]
                    ext2 = tipo.split('?')[1]
                    head = {'Referer': urlVideo,
                            'Content-Type': 'video/mp4',
                            'Connection': 'keep-alive',
                            'Origin': 'https://jetload.net',
                            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
                }
                    head2 = urllib.urlencode(head)
                    url2Play = tipo #ext+'?'+ext2+'|'+head2
                    urlVideo =[]
                    xbmc.log('[plugin.video.overflix] L498 - ' + str(tipo), xbmc.LOGNOTICE)
                else:
                    if file_high == '1'  :
                        url2Play = srv+'/v2/schema/'+file_name+'/master.m3u8'
                    elif file_med == '1' :
                        url2Play = srv+'/v2/schema/'+file_name+'/med.m3u8'
                    elif file_low == '1' :
                        url2Play = srv+'/v2/schema/'+file_name+'/low.m3u8'
                    #url2Play = srv + "/v2/schema/%s/master.m3u8" % file_name
                OK = False
                
            elif 'principal' in urlVideo :
                fxID = str(idsT[i+1])
                urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID
                
            xbmc.log('[plugin.video.overflix] L513- ' + str(urlVideo), xbmc.LOGNOTICE)
                
        except:
            pass

        if OK :
            try:
                url2Play = urlresolver.resolve(urlVideo)
            except:
                dialog = xbmcgui.Dialog()
                dialog.ok(" Erro:", " Video removido! ")
                url2Play = []
                pass

        if not url2Play : return

        xbmc.log('[plugin.video.overflix] L529 - ' + str(url2Play), xbmc.LOGNOTICE)

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

def addDirF(name,url,mode,iconimage,pasta=True,total=1) :
        u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok = True

        liz = xbmcgui.ListItem(name, iconImage="iconimage", thumbnailImage=iconimage)

        liz.setProperty('fanart_image', fanart)
        liz.setInfo(type="Video", infoLabels={"title": name})

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
        texto = texto.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
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
elif mode == 26      : getTemporadas(name,url,iconimage)
elif mode == 27      : getEpisodios(name,url)
elif mode == 30      : doPesquisaSeries()
elif mode == 35      : doPesquisaFilmes()
elif mode == 40      : getFavoritos()
elif mode == 41      : addFavoritos(name,url,iconimage)
elif mode == 42      : remFavoritos(name,url,iconimage)
elif mode == 43      : cleanFavoritos()
elif mode == 98      : getInfo(url)
elif mode == 99      : playTrailer(name,url,iconimage)
elif mode == 100  : player(name,url,iconimage)
elif mode == 110  : player_series(name,url,iconimage)
elif mode == 999  : openConfig()
elif mode == 1000 : openConfigEI()

xbmcplugin.endOfDirectory(int(sys.argv[1]))