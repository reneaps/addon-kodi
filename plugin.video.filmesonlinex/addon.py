#!/usr/bin/env python
# -*- coding: UTF-8 -*-

############################################################################################################
#                                      BIBLIOTECAS A IMPORTAR E DEFINIC�ES                                   #
############################################################################################################

import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,HTMLParser,xmltosrt,os, base64
import urlresolver
import resources.lib.moonwalk as moonwalk
import requests

import jsunpack
from bs4 import BeautifulSoup
from urlparse           import urlparse
try:
    import json
except:
    import simplejson as json
h = HTMLParser.HTMLParser()

versao = '1.0.6'
addon_id = 'plugin.video.filmesonlinex'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonfolder = selfAddon.getAddonInfo('path')
artfolder = addonfolder + '/resources/img/'
fanart = addonfolder + '/fanart.jpg'
fav = addonfolder + '/fav'
upnp = addonfolder + '/upnp'
url_base = 'https://filmesonlinex.me'
url_base2 = 'https://ibb.co/'

############################################################################################################
#                                                   MENUS                                                   #
############################################################################################################

def menu():
    addDir("[B]Generos[/B]",url_base,2,url_base2+'igQGsk')          
    addDir("[B]Favoritos[/B]",'-',22,url_base2+'jNC8q5')  
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmc.executebuiltin('Container.SetViewMode(502)')
    
def todas_categorias(url):
    xbmc.log('[plugin.video.filmesonlinex] L42 - ' + str(url), xbmc.LOGNOTICE)
    html = gethtml(url)
    soup = html.find("div",{"class":"bgct"})
    categorias = html("li")
    for categoria in categorias:
        titulo = categoria.a['title']
        url = categoria.a["href"]
        #img = categoria.img["src"]
        addDir("[B]"+titulo.encode('utf-8')+"[/B]",url,3,'img')
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        xbmc.executebuiltin('Container.SetViewMode(502)')
        
def menu_filme(name,url,iconimage): 
    addDir('[B]Assistir Agora: [/B]'+name,url,4,iconimage)
    addDir('[B]Trailer[/B]',url,21,iconimage,False)
    addDir('[B]Adicionar aos Favoritos[/B]',name+','+iconimage+','+url,17,url_base2+'jNC8q5',False)
    xbmc.executebuiltin('Container.SetViewMode(502)')    
    
def listar_filmes(url):
    if "lancamentos" in url : url = url.replace('lancamentos','lancamentos')
    xbmc.log('[plugin.video.filmesonlinex] L61 - ' + str(url), xbmc.LOGNOTICE)
    addDir("[B][COLOR red]PESQUISAR FILMES[/B][/COLOR]",'-',11,url_base2+'kUn2Hk')
    html = gethtml(url)
    arquivo = html("div",{"class":"main"})
    filmes = arquivo[0]("div", {"class":"poster"})
    total = len(filmes)
    for filme in filmes:
            titulo = filme.a['title'].encode('utf-8')
            if not 'filmes' in titulo:
                    url = filme.a['href'].encode('utf-8')
                    try:
                        img = filme.img['srcset'].split(',')[0].split(' ')[0].encode('utf-8')
                    except:
                        img = ''
                    addDir(titulo,url,20,img)
                    
    xbmc.executebuiltin('Container.SetViewMode(502)') 

def listar_filmes_p(url):
    print url
    addDir("[B][COLOR red]PESQUISAR FILMES[/B][/COLOR]",'-',11,url_base2+'kUn2Hk')
    html = abrir_url(url)
    soup = BeautifulSoup(html, "html5lib")
    filmes = soup("div",{"class":"poster"})
    total = len(filmes)
    for filme in filmes:
            img = filme.img['srcset'].split(',')[0].split(' ')[0]
            url =  filme.a['href']
            titulo = filme.a['title']
            addDir(titulo,url,20,img)
                    
    xbmc.executebuiltin('Container.SetViewMode(502)')    

def adicionar_favoritos_filmes(url):
    arquivo = open(fav, 'r')
    texto = arquivo.readlines()
    texto.append('\n'+url) 
    arquivo = open(fav, 'w')
    arquivo.writelines(texto)
    arquivo.close()
    xbmcgui.Dialog().ok('FilmesOnlineX', '                              Adicionado a lista de Favoritos.')    

def favoritos_filmes():
    arquivo = open(fav, 'r').readlines()
    for line in arquivo:
        params = line.split(',')
        try:
            nome = params[0]
            img = params[1].replace(' http','http')
            rtmp = params[2]
            addDir(nome,rtmp,4,img)
        except:
            pass
    addDir('[B]Remover Favoritos[/B]','-',19,url_base2+'jn8TOQ')  
    xbmc.executebuiltin('Container.SetViewMode(500)')

def limpar_lista_favoritos_filmes():    
    arquivo = open(fav, 'w')
    arquivo.write('')
    xbmcgui.Dialog().ok('FilmesOnlineX', '                       Lista de Favoritos limpa com sucesso.')
    menu()    
    
def categoria_favorito():
    addDir("[B]Filmes Favoritos[/B]",'-',18,url_base2+'jNC8q5')      
    
def trailer(name,url,iconimage):  
    html = abrir_url(url)
    link = re.compile(r'<div class="p"><strong><a href=" https://www.youtube.com/embed/(.*?)" data-lity>ASSISTIR O TRAILER</a></strong></div').findall(html)
    print link
    xbmc.log('[plugin.video.filmesonlinex] L130 - ' + str(link), xbmc.LOGNOTICE)
    link = link[0]
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play('plugin://plugin.video.youtube/play/?video_id='+link)
    del xbmcPlayer
    
def trailer2(name,url,iconimage):
    yt = "https://www.youtube.com/results?search_query="
    codigo_fonte = abrir_url(yt+name.replace(' ','%20'))
    a=[]
    idd = re.compile('" data-context-item-id="(.+?)"').findall(codigo_fonte)[0]
    print idd    
    xbmcPlayer = xbmc.Player()
    xbmcPlayer.play('plugin://plugin.video.youtube/play/?video_id='+idd)
    del xbmcPlayer

def pesquisar_filmes():
    keyb = xbmc.Keyboard('', 'Pesquisar...')
    keyb.doModal()
    if (keyb.isConfirmed()):
        search = keyb.getText()

        parametro_pesquisa=urllib.quote(search)

        url = 'http://www.filmesonlinex.ch/search.php?key=%s' % str(parametro_pesquisa)

        print url
        listar_filmes_p(url)

def player(name,url,iconimage):
    imgF = False
    OK = True
    html = abrir_url(url)
    soup = BeautifulSoup(html, "html5lib")
    xbmc.log('[plugin.video.filmesonlinex] L162 - ' + str(url), xbmc.LOGNOTICE)
    imgF = re.compile(r'<img class="poster" src="(.*?)" alt=".+?" title=".+.?">')
    try:
        link_houst = re.compile(r'<div class=\'web\'><a class=\'video\' id=\'video\' rel=\'nofollow\' href=\'(.*?)\'>.+?</a></div>').findall(html)
        pass
    except:
        pass
    try:
        link_houst = re.compile(r'<div class=\'web\'><a class=\'video2\' target=\'\_blank\' id=\"video\" rel=\'nofollow\' href=\'(.+?)\'>.+?</a></div>').findall(html)[0]
        pass
    except:
        pass
    
    if len(link_houst) <=0:
        titsT = []
        idsT = []
        #xbmc.log('[plugin.video.filmesonlinex] L175 - ' + str(html), xbmc.LOGNOTICE)
        links = soup('div', attrs={'class':'links'})
        srvsdub = links[0]('a')
        xbmc.log('[plugin.video.filmesonlinex] L181 - ' + str(srvsdub), xbmc.LOGNOTICE)

        for i in srvsdub :
                xbmc.log('[plugin.video.filmesonlinex] L186 - ' + str(i['href']), xbmc.LOGNOTICE)
                urlF = i["href"]
                urlF = urlF.replace(' ','')
                titS = i.text + ' - ' + urlparse(urlF).netloc.split('.')[0]
                titsT.append(titS)
                idsT.append(urlF)

        if not titsT : return

        index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

        if index == -1 : return
            
        i = int(index)
        link_houst = idsT[i]
        urlVideo = link_houst.encode('utf-8')
       
    xbmc.log('[plugin.video.filmesonlinex] L201 - ' + str(link_houst), xbmc.LOGNOTICE)
    if 'campanha.php' in link_houst:
            urlVideo = link_houst.split('id=')[1]
            st = urlVideo.split('&')[0]
            urlF = ''.join( reversed(st) )
            urlF = base64.b64decode(urlF)
            idVD = urlF.split('v/')[1]
            link_houst = 'https://adtly.in/api/source/%s' % idVD

    xbmc.log('[plugin.video.filmesonlinex] L192 - ' + str(link_houst), xbmc.LOGNOTICE)
    
    #if not "openload" in link_houst: html = abrir_url(link_houst)
    imgF = ""
    if "INDISPON�VEL" in html: return
    try:
        imgF = re.compile(r'image: \'(.+?)\'').findall(html)[0]
    except:
        pass
    addDir('[B]Adicionar aos Favoritos[/B]',name+','+iconimage+','+url,17,url_base2+'jNC8q5',False)
            
    if 'secvideo1' in urlVideo :
            fxID = urlVideo.split('embed/')[1]
            urlVideo = 'https://secvideo1.online/embed/%s' % fxID
            html = abrir_url(urlVideo)
            links = re.findall(r'file\:"(.*?)",', html)[-1]
            if ',' in links :
                links = links.split(',')
                srvs = re.sub(r'.\[.+?\]','\'',str(links))
                srvs = re.sub(r'.\[.+?\]','\'',str(links))
                srvs = srvs.split(',')
                urlVideo = links[1][6:]
            else :
                urlVideo = links
                xbmc.log('[plugin.video.filmesonlinex] L239 - ' + str(urlVideo), xbmc.LOGNOTICE)
            OK = False

    elif 'mrdhan.com' in urlVideo or 'vfilmesonline' in urlVideo :
            headers = {'referer': urlVideo,
                       'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'}
            response = requests.get(url=urlVideo,allow_redirects=False,headers=headers)
            if response.status_code >= 300 and response.status_code <= 399:
                # Sucesso
                urlVideo = response.headers['Location']
            pu = urlparse(urlVideo)
            p = r'(?://|\.)((mrdhan|dutrag|vfilmesonline)\.(com|net))/(?:f|e|v)/(.+)'
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
            xbmc.log('[plugin.video.filmesonlinex] L257 - ' + str(r), xbmc.LOGNOTICE)
            js = json.loads(r.text)
            links = js['data']
            qual = []
            for link in links:
                qual.append(link['label'])
            index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', qual)
            if index == -1 : return
            i = int(index)
            urlVideo = links[i]['file']
            OK = False
   
    if OK :
        link_video = urlresolver.resolve(urlVideo)
    else:
        link_video = urlVideo

    urlF = link_video
    sfile = ['-']
    xbmc.log('[plugin.video.filmesonlinex] L239 - ' + str(link_video), xbmc.LOGNOTICE)
    addLink(name.replace('Assistir Agora: ',''),urlF,imgF,sfile)
    '''
    sfile = ['720p']
    link_housts = link_houst
    for link_houst in link_housts:

            urlVideo = link_houst
            
            if 'playflixhd.ml' in link_houst:
                idVD = urlVideo.split('/')[4]
                link_video = 'https://playflixhd.ml/api/source/%s/' % idVD
                html = post_url(link_video)
                xbmc.log('[plugin.video.filmesonlinex] L223 - ' + str(link_video), xbmc.LOGNOTICE)
            elif 'playflixhd.co' in link_houst:
                idVD = urlVideo.split('/')[4]
                link_video = 'https://playflixhd.co/api/source/%s/' % idVD
                html = post_url(link_video)
            elif 'adtly.in' in link_houst:
                idVD = link_houst.split('v/')[1]
                link_video = 'https://adtly.in/api/source/%s' % idVD
                html = post_url(link_video)
                xbmc.log('[plugin.video.filmesonlinex] L231 - ' + str(link_video), xbmc.LOGNOTICE)
            else:
                urlVideo = link_houst 
            try:
                link_video = re.compile(r'\{\"file\":"(.*?)",\"label\":"(.*?)",\"type\":".+?"',    re.DOTALL).findall(html)
                sfile = re.compile(r'\{\"file\":".*?",\"label\":"(.*?)",\"type\":".+?"',re.DOTALL).findall(html)
                #xbmc.log('[plugin.video.filmesonlinex] L237 - ' + str(html), xbmc.LOGNOTICE)
                for urlF, qual in link_video:
                    urlF = urlF.replace("\\", "")
                    addLink(name.replace('Assistir Agora: ','') +' Full HD '+ str(qual),urlF,imgF,sfile)
            except:
                pass
            xbmc.log('[plugin.video.filmesonlinex] L233 - ' + str(link_houst), xbmc.LOGNOTICE)
            xbmc.log('[plugin.video.filmesonlinex] L234 - ' + str(link_video), xbmc.LOGNOTICE)
            if not link_video:
                try:
                    urlVideo = link_houst
                    OK = True
            
                    if 'secvideo1' in urlVideo :
                            fxID = urlVideo.split('embed/')[1]
                            urlVideo = 'https://secvideo1.online/embed/%s' % fxID
                            html = abrir_url(urlVideo)
                            links = re.findall(r'file\:"(.*?)",', html)[-1]
                            links = links.split(',')
                            srvs = re.sub(r'.\[.+?\]','\'',str(links))
                            srvs = re.sub(r'.\[.+?\]','\'',str(links))
                            srvs = srvs.split(',')
                            urlVideo = links[1][6:] 
                            OK = False

                    elif 'thevid' in urlVideo :
                            fxID = urlVideo.split('/e/')[1]
                            urlVideo = 'https://thevid.net/e/%s' % fxID

                    elif 'vcdn.io' in urlVideo :
                            fxID = urlVideo.split('/v/')[1]
                            urlVideo = 'https://www.fembed.com/v/%s' % fxID
                            
                    elif 'mixdrop' in urlVideo :
                            fxID = urlVideo.split('/e/')[1]
                            urlVideo = 'https://mixdrop.co/e/%s' % fxID
                            
                    elif 'jawcloud' in urlVideo :
                            link = abrir_url(urlVideo)
                            link = unicode(link, 'utf-8', 'ignore')
                            urlVideo = re.findall(r'source src=\s*\"(.+?)\"',link)[-1]
                            OK = False
                
                    if OK :
                        link_video = urlresolver.resolve(urlVideo)
                    else:
                        link_video = urlVideo
                        
                    urlF = link_video
                    sfile = ['-']
                    xbmc.log('[plugin.video.filmesonlinex] L239 - ' + str(link_video), xbmc.LOGNOTICE)
                    addLink(name.replace('Assistir Agora: ',''),urlF,imgF,sfile)
                except:
                    pass
    '''
    xbmc.log('[plugin.video.filmesonlinex] L244 - ' + str(link_video), xbmc.LOGNOTICE)
            
def player2(name,url,iconimage):
    print url
    xbmc.log('[plugin.video.filmesonlinex] L258 - ' + str(url), xbmc.LOGNOTICE)
    status = xbmcgui.DialogProgress()
    status.create('FILMESONLINEX', 'Resolvendo link...','Por favor aguarde...') 
    playlist = xbmc.PlayList(1)
    playlist.clear()    
    try:
        listitem = xbmcgui.ListItem(name,thumbnailImage=iconimage)
        listitem.setInfo("Video", {"Title":name.replace('Assistir o Filme: ','')})
        listitem.setProperty('mimetype', 'video/mp4')
        playlist.add(url,listitem)
        xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
        status.update(100)        
        xbmcPlayer.play(playlist).showSubtitles(True)
        status.close()        
    except: 
        xbmcgui.Dialog().ok('FILMESONLINEX', 'Conteudo temporariamente indisponivel,desculpe o transtorno.')
    del xbmcPlayer
    del status
        
############################################################################################################
#                                                   FUNC�ES                                                   #
############################################################################################################
    
def abrir_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.get_method = lambda: 'GET'
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    del response
    return link

def post_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    del response
    return link
    
def gethtml(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    del response
    soup = BeautifulSoup(link, "html5lib")
    return soup
    
def addDir(name,url,mode,iconimage,pasta=True,total=1,plot=''):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="iconimage", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', iconimage)
    liz.setInfo( type="video", infoLabels={ "title": name, "plot": plot } )
    contextMenuItems = []
    contextMenuItems.append(('Movie Information', 'XBMC.Action(Info)'))
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)
    return ok    

def addLink(name,url,iconimage,subtitle):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name })
    liz.setSubtitles(subtitle)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok    

def cast_upnp(url):
    arquivo = open(upnp, 'r')
    texto = arquivo.readlines()
    texto.append('\n'+url) 
    arquivo = open(upnp, 'w')
    arquivo.writelines(texto)
    arquivo.close()
    xbmcgui.Dialog().ok('FilmesOnlineX', '                              Adicionado a lista de Favoritos.')    
    
    
############################################################################################################
#                                              MAIS PAR�METROS                                               #
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

      
params=get_params()
url=None
name=None
mode=None
iconimage=None


try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass

try:        
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass


print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)

###############################################################################################################
#                                                    MODOS                                                      #
###############################################################################################################

if mode==None or url==None or len(url)<1:
    print ""
    menu()
elif mode==2:
    print ""
    todas_categorias(url)
elif mode==3:
    print  ""
    listar_filmes(url)
elif mode==4:
    print ""
    player(name,url,iconimage)
elif mode==5:
    print ""
    player2(name,url,iconimage) 
elif mode==11:
    print ""
    pesquisar_filmes()
elif mode==17:
    print ""
    adicionar_favoritos_filmes(url)
elif mode==18:
    print ""
    favoritos_filmes()    
elif mode==19:
    print ""
    limpar_lista_favoritos_filmes()
elif mode==20:
    print ""
    menu_filme(name,url,iconimage)
elif mode==21:
    print ""
    trailer(name,url,iconimage)
elif mode==22:
    print ""
    categoria_favorito()
elif mode==31:
    print ""
    trailer2(name,url,iconimage)
elif mode==32:
    print ""
    cast_upnp(url)    
    
xbmcplugin.endOfDirectory(int(sys.argv[1]))