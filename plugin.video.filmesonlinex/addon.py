#!/usr/bin/env python
# -*- coding: UTF-8 -*-

############################################################################################################
#                                     BIBLIOTECAS A IMPORTAR E DEFINICÕES                                  #
############################################################################################################

import urllib,urllib2,re,xbmcplugin,xbmcgui,xbmc,xbmcaddon,HTMLParser,xmltosrt,os

import jsunpack
from bs4 import BeautifulSoup
try:
    import json
except:
    import simplejson as json
h = HTMLParser.HTMLParser()

versao = '0.0.1'
addon_id = 'plugin.video.filmesonlinex'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonfolder = selfAddon.getAddonInfo('path')
artfolder = addonfolder + '/resources/img/'
fanart = addonfolder + '/fanart.jpg'
fav = addonfolder + '/fav'
upnp = addonfolder + '/upnp'
url_base = 'http://www.filmesonlinex.net/'
url_base2 = 'https://copy.com/'

############################################################################################################
#                                                  MENUS                                                   #
############################################################################################################

def menu():
    addDir("[B]Generos[/B]",url_base,2,url_base2+'ZLG0E8EeWlWfxpNA')        
    addDir("[B]Favoritos[/B]",'-',22,url_base2+'E1ebCG3qH1eEfP2v')  
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmc.executebuiltin('Container.SetViewMode(502)')
    
def todas_categorias(url):  
    html = gethtml(url)
    soup = html.find("ul",{"class":"clearfix"})
    categorias = soup.findAll("li")
    for categoria in categorias:
        titulo = categoria.a.text
        url = categoria.a["href"]
        #img = categoria.img["src"]
        addDir("[B]"+titulo.encode('utf-8')+"[/B]",url,3,'img')
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        xbmc.executebuiltin('Container.SetViewMode(502)')
        
def menu_filme(name,url,iconimage): 
    addDir('[B]Assistir Agora: [/B]'+name,url,4,iconimage)
    addDir('[B]Trailer[/B]',url,21,iconimage,False)
    addDir('[B]Adicionar aos Favoritos[/B]',name+','+iconimage+','+url,17,url_base2+'E1ebCG3qH1eEfP2v',False)
    xbmc.executebuiltin('Container.SetViewMode(502)')   
    
def listar_filmes(url):
    print url
    addDir("[B][COLOR red]PESQUISAR FILMES[/B][/COLOR]",'-',11,url_base2+'PyJEKKphI7CuvJPe')
    html = abrir_url(url)
    soup = BeautifulSoup(html)
    arquivo = soup("ul",{"id":"category-thumbs"})[0]
    filmes = arquivo("li")
    total = len(filmes)
    for filme in filmes:
            titulo = filme.b.text.encode('utf-8')
            if not 'filmes' in titulo:
                    url = filme.a["href"].encode('utf-8')
                    try:
                        img = filme.img["data-src"]
                    except KeyError:
                        img = filme.img["src"]
                    addDir(titulo,url,20,img)
                    
    xbmc.executebuiltin('Container.SetViewMode(502)') 

def listar_filmes_p(url):
    print url
    addDir("[B][COLOR red]PESQUISAR FILMES[/B][/COLOR]",'-',11,url_base2+'PyJEKKphI7CuvJPe')
    html = abrir_url(url)
    soup = BeautifulSoup(html)
    filmes = soup("div",{"class":"filme"})
    total = len(filmes)
    for filme in filmes:
            links = filme('a',{'class':'link'})
            img = filme.img['src']
            url =  filme.a['href']
            titulo = links[0].text.decode('unicode-escape').encode('utf-8')
            addDir(titulo,url,20,img)
                    
    xbmc.executebuiltin('Container.SetViewMode(502)')   

def adicionar_favoritos_filmes(url):
    arquivo = open(fav, 'r')
    texto = arquivo.readlines()
    texto.append('\n'+url) 
    arquivo = open(fav, 'w')
    arquivo.writelines(texto)
    arquivo.close()
    xbmcgui.Dialog().ok('Armagedom Pirata', '                             Adicionado a lista de Favoritos.')    

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
    addDir('[B]Remover Favoritos[/B]','-',19,url_base2+'nglhskXKjB2xShIB')  
    xbmc.executebuiltin('Container.SetViewMode(500)')

def limpar_lista_favoritos_filmes():    
    arquivo = open(fav, 'w')
    arquivo.write('')
    xbmcgui.Dialog().ok('Armagedom Pirata', '                      Lista de Favoritos limpa com sucesso.')
    menu()  
    
def categoria_favorito():
    addDir("[B]Filmes Favoritos[/B]",'-',18,url_base2+'oHdcc77U8Zb3SqfM')   
    
def trailer(name,url,iconimage):  
        html = abrir_url(url)
        link = re.compile(r'<a id="trailer" class="video" href="https://www.youtube.com/embed/(.+?)" rel="nofollow">trailer</a>').findall(html)[0]
        print link
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play('plugin://plugin.video.youtube/play/?video_id='+link)
		del xbmcPlayer
        
def trailer2(name,url,iconimage):
    yt = "https://www.youtube.com/results?search_query="
    codigo_fonte = abrir_url(yt+name.replace(' ','%20'))
    #print html
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

        url = 'https://www.filmesonlinex.net/search.php?key=%s' % str(parametro_pesquisa)

        print url
        listar_filmes_p(url)

def player(name,url,iconimage):
    xbmc.log('[plugin.video.filmesonlinex] L144 - ' + str(url), xbmc.LOGNOTICE)
    html = abrir_url(url)
    link_houst = re.compile(r"<a class=\'video\' rel=\'nofollow\' href=\'(.+?)'\>.+?</a>").findall(html)[0]
    if not link_houst:
        link_houst = re.compile(r"<a class=\'video cboxElement\' rel=\'nofollow\' href=\'(.+?)'\>.+?</a>").findall(html)[0]
    if not link_houst:
        link_video = re.compile(r'<div class="gdr"><a class="video" rel="nofollow" href="(.*?)">(.*?)</a></div>').findall(html)
    print link_houst
    html = abrir_url(link_houst)
    imgF =  re.compile(r'image:.*."(.*?)",').findall(html)[0]
    #xbmc.log('[plugin.video.filmesonlinex] L152 - ' + str(imgF), xbmc.LOGNOTICE)
    addDir('[B]Adicionar aos Favoritos[/B]',name+','+iconimage+','+url,17,url_base2+'E1ebCG3qH1eEfP2v',False)
    try:
        link_video = re.compile(r'"file":"(.*?)","type":".*?","label":"(.*?)".').findall(html)
        for urlF, qual in link_video:
            urlF = urlF.replace("\\", "")
            addLink(name.replace('Assistir Agora: ','')+' Full HD '+str(qual),urlF,imgF)
    except:
        pass
    if not link_video:
        try:
            link_video = re.compile(r'playerInstance.load\(\{sources: \[\{file:*\'(.*?).\'').findall(html)
            for urlF in link_video:
                addLink(name.replace('Assistir Agora: ','')+' Full HD 1080p',urlF,imgF)
        except:
            pass

def player2(name,url,iconimage):
    print url
    xbmc.log('[plugin.video.filmesonlinex] L172 - ' + str(url), xbmc.LOGNOTICE)
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
        xbmcPlayer.play(playlist)
        status.close()      
    except: 
        xbmcgui.Dialog().ok('FILMESONLINEX', 'Conteudo temporariamente indisponivel,desculpe o transtorno.')
	del xbmcPlayer
	del status
        
############################################################################################################
#                                                  FUNCÕES                                                 #
############################################################################################################
    
def abrir_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
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
    soup = BeautifulSoup(link)
    return soup

#def addDir(name,url,mode,iconimage,pasta=True,total=1,plot=''):
    #u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
    #ok=True
    #liz=xbmcgui.ListItem(name, iconImage="iconimage", thumbnailImage=iconimage)
    #liz.setProperty('fanart_image', iconimage)
    #liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
    #contextMenuItems = []
    #contextMenuItems.append(("[COLOR orange]Remove from Favourite Movies[/COLOR]",'XBMC.RunPlugin(s?name=%s&url=%s&mode=19&iconimage=%s)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))
    #liz.addContextMenuItems(contextMenuItems, replaceItems=True)
    #ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)
    #return ok

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

def addLink(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', fanart)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok   

def cast_upnp(url):
    arquivo = open(upnp, 'r')
    texto = arquivo.readlines()
    texto.append('\n'+url) 
    arquivo = open(upnp, 'w')
    arquivo.writelines(texto)
    arquivo.close()
    xbmcgui.Dialog().ok('Armagedom Pirata', '                             Adicionado a lista de Favoritos.')    
    
    
############################################################################################################
#                                             MAIS PARÂMETROS                                              #
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
#                                                   MODOS                                                     #
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