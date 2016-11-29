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

addon_id  = 'plugin.video.filmesonlinehd11'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/img/'
fanart      = addonfolder + '/fanart.png'
base        = base64.b64decode('aHR0cDovL3d3dy5maWxtZXNvbmxpbmVoZDExLmNj')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'                , base							,   10, artfolder + 'categorias.png')
		addDir('Lançamentos'               , base + '/lancamentos/'			,   20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'           , base + '/?s=dublado&submit='	,   20, artfolder + 'pesquisa.png')
		addDir('Seriados'	               , base + '/series/'				,   25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'           , '--'							,   30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'           , '--'							,   35, artfolder + 'pesquisa.png')
		addDir('Configurações'             , base							,  999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo', base							, 1000, artfolder + 'config.png', 1, False)
			
		setViewMenu()		
		
def getCategorias(url):
		link = openURL(url)
		soup = BeautifulSoup(link)
		link = unicode(link, 'utf-8', 'ignore')
		
		conteudo   = soup("div", {"class": "cabecalho"})	
		categorias = conteudo[0]('li', {'class':'unidade submenu'})
		categorias = categorias[0]('li')
				
		totC = len(categorias)
		
		for categoria in categorias:
				titC = categoria.text.encode('utf-8','replace')
				urlC = categoria.a["href"]
				imgC = artfolder + limpa(titC) + '.png'
				addDir(titC,urlC,20,imgC)
			
		setViewMenu()		
		
def getFilmes(url):
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup     = BeautifulSoup(link)
		conteudo = soup("div", {"class": "peliculas"})
		filmes   = conteudo[0]("div", {"class": "item"})
		totF = len(filmes)
		for filme in filmes:
				titF = filme.img["alt"].encode('utf-8').replace('Assistir ', '')
				urlF = filme.a["href"].encode('utf-8')
				imgF = filme.img["src"].encode('utf-8')
				addDirF(titF, urlF, 100, imgF, False, totF)

		try :
				proxima = re.findall('<a class="nextpostslink" rel="next" href="(.*?)">.*?</a>', link)[0]				
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except : 
				pass
				
		setViewFilmes()
				
def getSeries(url):
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		
		
		soup     = BeautifulSoup(link)
		conteudo = soup("div", {"class": "peliculas"})
		filmes   = conteudo[0]("div", {"class": "item"})
		totF = len(filmes)
		for filme in filmes:
				titF = filme.img["alt"].encode('utf-8').replace('Assistir ', '')
				urlF = filme.a["href"].encode('utf-8')
				imgF = filme.img["src"].encode('utf-8')
				addDir(titF, urlF, 26, imgF)
				
		try : 
				proxima = re.findall('<a class="nextpostslink" rel="next" href="(.*?)">.*?</a>', link)[0]				
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except : 
				pass
				
		setViewFilmes()

def getTemporadas(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')	
		soup     = BeautifulSoup(link)
		conteudo = soup("div", {"class": "cuerpo"})
		if not conteudo:
			conteudo = soup.findAll("film", {"class":"players"})
			srvsdub  = conteudo[0]("iframe")
		else:
			srvsdub  = conteudo[0]("iframe")
		urlF = srvsdub[0]['src']
		
		img = soup.find("div", {"class": "caratula"})
		if not img:
			img = soup.find("div", {"class": "peli"})
		imgF = re.findall(r'<img src="(.*?) alt=.*?" />', str(img))
		imgF = imgF[0]
		
		link = openURL(urlF)
		link = unicode(link, 'utf-8', 'ignore')	
		soup = BeautifulSoup(link)
		conteudo = soup("div", {"class": "embed"})
		if not conteudo:
			conteudo = soup("div", {"class": "content"})
			srvsdub  = conteudo[0]("video")
		else:
			srvsdub  = conteudo[0]("button")

		servers = re.findall("addiframe\('(.*?)'\);", link)
		totF = len(srvsdub)
		for i in range(totF) :
				titF = srvsdub[i].text.encode('utf-8').replace('Assistir por ','')
				titF = titF.replace('Assistir ', '')
				urlF = servers[i]
				if "Epis" in titF:
					addDir(titF, urlF, 28, imgF, False, totF)
				else:
					addDir(titF, urlF, 27, imgF)

def getServidores(name, url, iconimage):
		temp = []
		episodios = []
		imgF = iconimage
		
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')	
		soup     = BeautifulSoup(link)		
		conteudo = soup("div", {"class": "embed"})
		if not conteudo:
			conteudo = soup("div", {"class": "content"})
			srvsdub  = conteudo[0]("video")
		else:
			srvsdub  = conteudo[0]("button")
		servers = re.findall("addiframe\('(.*?)'\);", link)
		print servers
		totD = len(srvsdub)
		print totD
		print "Lista Servidores"
		for i in range(totD) :
				titF = srvsdub[i].text.encode('utf-8').replace('Assistir por ','')
				titF = titF.replace('Assistir ', '')
				urlF = servers[i]
				if "Epis" in titF:
					addDir(titF, urlF, 28, imgF, False, totD)
				else:
					addDir(titF, urlF, 27, imgF)
					
def getEpisodios(name, url, iconimage):
		temp = []
		episodios = []
		imgF = iconimage

		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')	
		soup     = BeautifulSoup(link)		
		conteudo = soup("div", {"class": "embed"})
		if not conteudo:
			conteudo = soup("div", {"class": "content"})
			srvsdub  = conteudo[0]("video")
		else:
			srvsdub  = conteudo[0]("button")
		
		servers = re.findall("addiframe\('(.*?)'\);", link)
		
		addon = xbmcaddon.Addon()
		addonname = addon.getAddonInfo('name')
		line1 = str(len(servers))
		xbmcgui.Dialog().ok(addonname, line1)	
		
		print servers
		totD = len(srvsdub)
		print totD
		print "Lista Episodios"
		for i in range(totD) :
				titF = srvsdub[i].text.encode('utf-8').replace('Assistir por ','')
				titF = titF.replace('Assistir ', '')
				urlF = servers[i]
				addDir(titF, urlF, 110, imgF, False, totD)

def pesquisa():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()
		a = []
		hosts = []
		
		if (keyb.isConfirmed()):
				texto    = keyb.getText()
				pesquisa = urllib.quote(texto)
				url      = base + '/?s=%s&submit=' % str(pesquisa)

				link  = openURL(url)
				link = unicode(link, 'utf-8', 'ignore')		
				soup     = BeautifulSoup(link)
				conteudo = soup.findAll("div", {"class": "peliculas"})
				if not conteudo:
						conteudo = soup.findAll("div", {"class": "filmes"})
						filmes   = conteudo[1]("film", {"class": "item"})
				else:
						filmes   = conteudo[0]("div", {"class": "item"})
				totF = len(filmes)
				#print totF
				for filme in filmes:
						titF = filme.img["alt"].encode('utf-8').replace('Assistir ', '')
						urlF = filme.a["href"].encode('utf-8')
						imgF = filme.img["src"].encode('utf-8')	
						temp = [urlF, titF, imgF]
						hosts.append(temp)
					
				a = []
				for url, titulo, img in hosts:
					temp = [url, titulo, img]
					a.append(temp);
					
				return a
		return

def doPesquisaSeries():
		a = pesquisa()
		if not a: return
		total = len(a)
		for url2, titulo, img in a:
			addDir(titulo, url2, 26, img, False, total)
			
def doPesquisaFilmes():
		a = pesquisa()
		if not a: return
		total = len(a)
		for url2, titulo, img in a:
			addDir(titulo, url2, 100, img, False, total)
			
def player(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('FilmesOnlineHD11', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		idsT = []
		
		matriz = []

		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')	
		soup     = BeautifulSoup(link)
		conteudo = soup("film", {"class": "players"})
		if not conteudo:
				conteudo = soup.findAll("div", {"class": "cuerpo"})
				srvsdub  = conteudo[0]("iframe")
		else:
				srvsdub  = conteudo[0]("iframe")
		url = srvsdub[0]['src']

		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')	
		soup = BeautifulSoup(link)

		conteudo = soup("div", {"class": "embed"})
		srvsdub  = conteudo[0]("button")

		totD = len(srvsdub)
		print totD
		for i in range(totD) :
				srv = srvsdub[i].text.replace('Assistir por ','')
				srv = srv.replace('Assistir Por ', '')
				titsT.append(srv)
				
		if not titsT : return
		
		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)
		
		if index == -1 : return
		
		i = index
		
		servers = re.findall("addiframe\('(.*?)'\);", link)
		print servers

		urlVideo = servers[i]
		print urlVideo
		
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
				
		elif 'ok.ru' in urlVideo :
				okID = urlVideo.split('embed/')[1]
				urlVideo = 'https://ok.ru/videoembed/%s' % okID
				
		elif 'openload' in urlVideo :
				okID = urlVideo.split('embed/')[1]
				urlVideo = 'https://openload.co/embed/%s' % okID			
				
		elif 'thevid.net' in urlVideo :
				linkTV  = openURL(urlVideo)		
				sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
				aMatches = re.compile(sPattern).findall(linkTV)
				sUnpacked = jsunpack.unpack(aMatches[1])
				url2Play = re.findall('var vurl3="(.*?)"', sUnpacked)
				url2Play = str(url2Play[0])				
	
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
		
		addon = xbmcaddon.Addon()
		addonname = addon.getAddonInfo('name')
		line1 = str(url2Play)
		#xbmcgui.Dialog().ok(addonname, line1)	
		
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
		return ok
		
def player_series(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('FilmesOnlineHD11', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		urlVideo = url
		
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
				linkTV  = openURL(urlVideo)		
				sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
				aMatches = re.compile(sPattern).findall(linkTV)
				sUnpacked = jsunpack.unpack(aMatches[1])
				url2Play = re.findall('var vurl3="(.*?)"', sUnpacked)
				url2Play = str(url2Play[0])				

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
		
		return ok
	
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
		titO = re.findall('<h2 class="titulo-filme"><b>(.*?)</b></h2>', link)[0]

		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
		link = openURL(url)
		ytID = re.findall('<iframe src="http://www.youtube.com/embed/(.*?)" frameborder="0" width="100%" height="100%" scrolling="no" allowfullscreen="true"></iframe>', link)[0]

		if not ytID : 
			addon = xbmcaddon.Addon()
			addonname = addon.getAddonInfo('name')
			line1 = str("Trailer não disponível!")
			xbmcgui.Dialog().ok(addonname, line1)	
			return
			
		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=youtubevideo, id=%s")' % ytID)
	
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
elif mode == 27   : getServidores(name, url, iconimage)
elif mode == 28   : getEpisodios(name, url, iconimage)
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