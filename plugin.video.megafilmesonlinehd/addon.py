#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : Hora Da Pipoca
# By AddonBrasil - 11/12/2015
# Atualizado (1.0.1) - 15/12/2015
# Atualizado (1.1.0) - 12/03/2016
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib               import jsunpack

addon_id  = 'plugin.video.megafilmesonlinehd'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/img/'
fanart      = addonfolder + '/fanart.png'
base        = base64.b64decode('aHR0cDovL3d3dy5tZWdhZmlsbWVzb25saW5laGQuY29t')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'                , base                          ,   10, artfolder + 'categorias.png')
		addDir('Lançamentos'               , base + '/filmes-lancamentos'  ,   20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'           , base + '/?s=dublado&btn-busca=',  20, artfolder + 'pesquisa.png')
		addDir('Seriados'	               , base + '/seriados/'		   ,   25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'           , '--'                          ,   30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'           , '--'                          ,   35, artfolder + 'pesquisa.png')
		addDir('Configurações'             , base                          ,  999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo', base                          , 1000, artfolder + 'config.png', 1, False)
			
		setViewMenu()		
		
def getCategorias(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')	
		
		soup = BeautifulSoup(link)
		conteudo   = soup("ul", {"class": "menu"})
		categorias = conteudo[0]("li")
				
		totC = len(categorias)
		
		for categoria in categorias:
				titC = categoria.a.text.encode('utf-8','replace')
				
				if not 'Lançamento' in titC :
						urlC = categoria.a["href"]
						imgC = artfolder + limpa(titC) + '.png'
				
						addDir(titC,urlC,20,imgC)
			
		setViewMenu()		
		
def getFilmes(url):
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')

		soup     = BeautifulSoup(link)
		conteudo = soup("div", {"class": "galeria"})
		#content   = conteudo[0]("div", {"class": "content"})
		filmes   = conteudo[0]("div", {"class": "center"})
		totF = len(filmes)

		for filme in filmes:
				titF = filme.a["title"].encode('utf-8')
				urlF = filme.a["href"].encode('utf-8')
				imgF = filme.img["src"].encode('utf-8')
				addDirF(titF, urlF, 100, imgF, False, totF)
				
		try : 
				proxima = re.findall('<a class="next page-numbers" href="(.*?)"', link)[0]
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except : 
				pass
				
		setViewFilmes()
				
def getSeries(url):
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		
		
		soup     = BeautifulSoup(link)
		conteudo = soup("div", {"class": "galeria"})
		filmes   = conteudo[0]("div", {"class": "center"})
		totF = len(filmes)

		for filme in filmes:
				titF = filme.a["title"].encode('utf-8')
				urlF = filme.a["href"].encode('utf-8')
				imgF = filme.img["src"].encode('utf-8')
				addDir(titF, urlF, 26, imgF)
				
		try : 
				proxima = re.findall('<a class="next page-numbers" href="(.*?)"', link)[0]
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except : 
				pass
				
		setViewFilmes()
		
def getTemporadas(url):
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		
		soup     = BeautifulSoup(link)
		conteudo = soup.find("div", {"class": "top-menu-abas full-hidden"})
		temporadas = conteudo('a')
		totF = len(temporadas)
		img = '' #soup.find("div", {"class": "top-menu-abas full-hidden"})
		urlF = url
		i = 1
		while i <= totF:
			titF = str(i) + "ª Temporada"
			try:
				addDir(titF, urlF, 27, iconimage)
			except:
				pass
			i = i + 1

def getEpisodios(name, url):
		n = name.replace('ª Temporada', '')	
		n = int(n)
		n = (n-1)
		temp = []
		episodios = []
	
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		
		
		soup = BeautifulSoup(link)
		conteudo = soup('div',{'class':'content-menu-abas'})

		imgF = ""
		img = soup.find("div", {"class": "content relative"})
		imgF = re.findall(r'<img src="(.*?) alt=.*?" />', str(img))
		img = imgF[0]
		
		try:
			arquivo = conteudo[n]('table')
			dublados = arquivo[0]('tr')
			au = arquivo[0].text.encode('utf-8')
			result= re.split(r'Epi', au)
			audio = result[0]
			for link in dublados:
					url = link.a["href"].encode('utf-8', 'ignore')
					titulo = link.a.text.encode('utf-8', 'ignore')
					titulo = str(audio)+" "+titulo
					tempor = (url, titulo)
					episodios.append(tempor)
		except:
			pass
		try:
			arquivo = conteudo[n]('table')
			legendados = arquivo[1]('tr')
			au = arquivo[1].text.encode('utf-8')
			result= re.split(r'Epi', au)
			audio = result[0]
			for link in legendados:
					url = link.a["href"].encode('utf-8', 'ignore')
					titulo = link.a.text.encode('utf-8', 'ignore')
					titulo = str(audio)+" "+titulo
					tempor = (url, titulo)
					episodios.append(tempor)
		except:
			pass		

		total = len(episodios)

		for url, titulo in episodios:
				addDir(titulo, url, 110, img, False, total)

def pesquisa():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto    = keyb.getText()
				pesquisa = urllib.quote(texto)
				url      = base + '/?s=%s&btn-busca=' % str(pesquisa)

				link  = openURL(url)
				link = unicode(link, 'utf-8', 'ignore')		
		
				soup     = BeautifulSoup(link)
				conteudo = soup("div", {"class": "galeria"})
				content   = conteudo[0]("div", {"class": "content"})
				filmes   = conteudo[0]("div", {"class": "center"})
				totF = len(filmes)
				hosts = []

				for filme in filmes:
						titF = filme.a["title"].encode('utf-8')
						urlF = filme.a["href"].encode('utf-8')
						imgF = filme.img["src"].encode('utf-8')
						temp = [urlF, titF, imgF]
						hosts.append(temp)
					
				a = []
				for url, titulo, img in hosts:
					temp = [url, titulo, img]
					a.append(temp);
					#addDir(titulo, url, 26, img)
					
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
			
def player(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('MegaFilmesOnline', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		idsT = []
		
		matriz = []
		
		link  = openURL(url)	
		soup     = BeautifulSoup(link)	
		conteudo = soup("div", {"class": "container"})
		article = conteudo[1]("div",{'class':"content-top full-hidden"})
		srvsdub  = article[0]("div",{"class":"full-hidden"})
		serv = srvsdub[0]("div",{"class":"top-menu-abas full-hidden"})
		srvsdub = serv[0]("a")
		print srvsdub
		totD = len(srvsdub)
		print totD
		for i in range(totD) :
				srv = srvsdub[i].text
				titsT.append(srv)
				
		if not titsT : return
		
		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)
		
		if index == -1 : return
		
		i = (index + 1)

		conteudo = soup("div", {"class": "content-player"})
		links = conteudo[i]("iframe")
								
		addon = xbmcaddon.Addon()
		addonname = addon.getAddonInfo('name')
		line1 = str(links)
		#xbmcgui.Dialog().ok(addonname, line1)	
		
		if len(links) == 0 : links = conteudo[0]("a")

		urlVideo = re.findall(r'data-src=[\'"]?([^\'" >]+)', str(links))[0]
	
		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
		
		if 'nowvideo.php' in urlVideo :
				nowID = urlVideo.split("id=")[1]
				urlVideo = 'http://embed.nowvideo.sx/embed.php?v=%s' % nowID
				
		elif 'video.tt' in urlVideo :
				vttID = urlVideo.split('e/')[1]
				urlVideo = 'http://www.video.tt/watch_video.php?v=%s' % vttID
				
		elif 'flashx.php' in urlVideo :
				fxID = urlVideo.split('id=')[1]
				urlVideo = 'http://www.flashx.tv/embed-%s.html' % fxID
				
		elif 'ok.php' in urlVideo :
				okID = urlVideo.split('id=')[1]
				urlVideo = 'https://ok.ru/videoembed/%s' % okID
				
		elif 'open.php' in urlVideo :
				okID = urlVideo.split('id=')[1]
				urlVideo = 'https://openload.co/embed/%s' % okID
				
		elif 'drive.php' in urlVideo :
				okID = urlVideo.split('id=')[1]
				urlVideo = 'https://docs.google.com/file/d/%s/preview' % okID

		elif 'netu.php' in urlVideo :
				okID = urlVideo.split('id=')[1]
				urlVideo = 'http://hqq.tv/player/embed_player.php?vid=%s' % okID	

		elif 'thevid.php' in urlVideo :
				fxID = urlVideo.split('id=')[1]
				urlVideo = 'http://thevid.net/e/%s' % fxID
				linkTV  = openURL(urlVideo)		
				sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
				aMatches = re.compile(sPattern).findall(linkTV)
				sUnpacked = jsunpack.unpack(aMatches[1])
				url2Play = re.findall('var vurl3="(.*?)"', sUnpacked)
				url2Play = str(url2Play[0])				
	
				OK = False
					
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

		xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
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
		matriz = []

		link = openURL(url)
		soup  = BeautifulSoup(link)
	
		try :
				conteudo = soup("div", {"class": "geral"})
				srvsdub  = conteudo[0]("a")
				totD = len(srvsdub)
				tipo = "Server"

				for i in range(totD) :
						titS = srvsdub[i].text + " (%s)" % tipo
						idS = srvsdub[i]["id"]
						titsT.append(titS)
						idsT.append(idS)
		except :
				pass
				
		try :
				conteudo = soup("div", {"class": "geral'"})
				srvsleg  = conteudo[0]("a")
				totL = len(srvsleg)
				tipo = "Servidor"

				for i in range(totL) :
						titS = srvsdub[i].text + " (%s)" % tipo
						idS = srvsleg[i]["id"]
						titsT.append(titS)
						idsT.append(idS)
		except :
				pass
		
		if not titsT : return
		
		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)
			
		if index == -1 : return
		
		ind = idsT[index]

		conteudo = soup("div", {"class": "geral"})
		links = conteudo[0]("a")
		
		if len(links) == 0 : links = conteudo[0]("a")
		ind = int(ind)
		urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(link))[ind-1]
				
		link = openURL(urlVideo)
		soup  = BeautifulSoup(link)
		conteudo = soup("iframe")
		urlVideo = str(conteudo[0]['src'])

		print "URLVIDEO " + urlVideo

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
				
		if 'nowvideo.php' in urlVideo :
				nowID = urlVideo.split("id=")[1]
				urlVideo = 'http://embed.nowvideo.sx/embed.php?v=%s' % nowID
				
		elif 'video.tt' in urlVideo :
				vttID = urlVideo.split('e/')[1]
				urlVideo = 'http://www.video.tt/watch_video.php?v=%s' % vttID

		elif 'flashx.php' in urlVideo :
				fxID = urlVideo.split('id=')[1]
				urlVideo = 'http://www.flashx.tv/playvid-%s.html' % fxID
				
		elif 'ok.ru' in urlVideo :
				fxID = urlVideo.split('embed')[1]
				urlVideo = 'https://ok.ru/videoembed%s' % fxID
				
		elif 'thevid.net' in urlVideo :
				linkTV = openURL(urlVideo)
				js_data = jsunpack.unpack(linkTV)
				
				url2Play = re.findall('var vurl2="(.*?)"', js_data)[0]

				OK = False
		
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

		xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
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
		
		return true
	
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
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
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

def getInfo(url)	:
		link = openURL(url)
		titO = re.findall('<li>Titulo original: <span>(.*?)</span>thevid', link)[0]
				
		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
		link = openURL(url)
		ytID = re.findall('<iframe width=".*?" height=".*?" src="http://www.youtube.com/embed/(.*?)" frameborder="0" allowfullscreen></iframe>', link)[0]
		
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