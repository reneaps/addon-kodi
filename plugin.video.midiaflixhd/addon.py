#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : MidiaFlixHD
# By AddonBrasil - 11/12/2015
# Atualizado (1.0.0) - 29/06/2018
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib				 import jsunpack
from time						 import time

version	  = '1.5.0'
addon_id  = 'plugin.video.midiaflixhd'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder	= addonfolder + '/resources/img/'
fanart		= addonfolder + '/fanart.png'
base		= base64.b64decode('aHR0cDovL3d3dy5taWRpYWZsaXhoZC5uZXQv')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'				, base + ''								,	10, artfolder + 'categorias.png')
		addDir('Lançamentos'			, base + 'categoria/lancamentos/'		,	20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'		, base + '?s=dublado'					,	20, artfolder + 'pesquisa.png')
		addDir('Seriados'				, base + 'series/'						,	25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'		, '--'									,	30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'		, '--'									,	35, artfolder + 'pesquisa.png')
		addDir('Configurações'			, base									,  999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo'	, base								, 1000, artfolder + 'config.png', 1, False)
			
		setViewMenu()		
		
def getCategorias(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)
		conteudo   = soup("ul",{"class":"sub-menu"})
		categorias = conteudo[0]("li")

		totC = len(categorias)

		for categoria in categorias:
				titC = categoria.a.text.encode('utf-8','')
				urlC = categoria.a["href"]
				imgC = artfolder + limpa(titC) + '.png'
				addDir(titC,urlC,20,imgC)
			
		setViewMenu()		
		
def getFilmes(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		
		soup = BeautifulSoup(link)
		conteudo = soup("div",{"class":"items"})
		filmes = conteudo[0]('div',{'class':'poster'})

		totF = len(filmes)

		for filme in filmes:
				titF = filme.img["alt"].encode("utf-8")
				urlF = filme.a["href"].encode('utf-8')
				imgF = filme.img["src"]
				addDirF(titF, urlF, 100, imgF, False, totF)
				
		try : 
				proxima = re.findall('<link rel="next" href="(.+?)" />', link)[0]
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except : 
				pass
				
		setViewFilmes()
				
def getSeries(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		
		
		soup = BeautifulSoup(link)
		conteudo = soup.findAll('div',{'id':'series-list'})
		filmes = conteudo[0]('a')
		#xbmc.log('[plugin.video.midiaflixhd] L87 ' + str(filmes), xbmc.LOGNOTICE)
		totF = len(filmes)

		for filme in filmes:
				titF = filme.find('div',{'class':'title'}).text.encode('utf-8')
				urlF = filme["href"].encode('utf-8')
				titF = urlF.replace('http://www.midiaflixhd.net/series/','')
				titF = titF.replace('/','').replace('-',' ')
				titF = titF.replace(' as','').replace('todas','').replace('temporadas','')
				titF = titF.title()
				imgF = filme.img["data-original"].encode('utf-8')
				addDir(titF, urlF, 26, imgF)
				
		try : 
				proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
				#proxima = re.findall('<a class="next page-numbers" href="(.*?)"', link)[0]
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except : 
				pass

		setViewFilmes()

def getTemporadas(url):
		link  = openURL(url)	
		soup = BeautifulSoup(link)	
		filmes = soup('div', {'id':'seasons'})
		seasons = filmes[0]('div',{'class':'item get_episodes'})
		urlF = url
		totD = len(seasons)
		
		imgF = ""
		img = soup.find("meta", {"property": "og:image"})
		imgF = re.findall(r'content=[\'"]?([^\'" >]+)', str(img))
		imgF = imgF[0]
				
		i = 1
		while i <= totD:
			titF = str(i) + "ª Temporada"
			try:
				addDir(titF, urlF, 27, imgF)
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
		filmes = soup.findAll('div', {'id':'seasons'})
		seasons = filmes[0]('div',{'class':'item get_episodes'})
		idseasons = seasons[n]['data-row-id']
		data = urllib.urlencode({'action':'episodes','season':idseasons})
		url = 'http://www.midiaflixhd.net/wp-admin/admin-ajax.php'
		req = urllib2.Request(url=url,data=data)
		content = urllib2.urlopen(req).read()
		d = json.loads(content)
		b = d['episodes']
		#xbmc.log('[plugin.video.midiaflixhd] L87 ' + str(b), xbmc.LOGNOTICE)
		imgF = ""
		img = soup.find("meta", {"property": "og:image"})
		imgF = re.findall(r'content=[\'"]?([^\'" >]+)', str(img))
		img = imgF[0]
							
		for i in range(0, len(b)):
				titF = b[str(i)]['name'].encode('utf-8')
				idname = b[str(i)]['id']
				urlF = pega(idname)
				if urlF == "" : titF = titF + ">>Indisponivel"
				imgF = ''
				temp = (urlF, titF)
				episodios.append(temp)

		total = len(episodios)

		for url, titulo in episodios:
				addDirF(titulo, url, 110, img, False, total)

def pega(idname):
	idtime = int(round(time() * 1000))
	idtime = str(idtime)
	data = urllib.urlencode({'action':'downloadPage','id':idname,'_':idtime})
	url = 'http://www.midiaflixhd.net/wp-admin/admin-ajax.php'
	#req.add_header('Referer', 'http://www.midiaflixhd.net/series/game-of-thrones-todas-as-temporadas/')
	r = urllib2.urlopen(url+'?'+data)
	html = r.read()
	#xbmc.log('[plugin.video.midiaflixhd] L180 ' + str(html), xbmc.LOGNOTICE)		
	urlF = re.compile(r'<a target="_BLANK" href="(.+?)" class="player">').findall(html)[0]
	html = openURL(urlF)
	soup = BeautifulSoup(html)
	#xbmc.log('[plugin.video.midiaflixhd] L184 ' + str(html), xbmc.LOGNOTICE)	
	urlF = soup.iframe["src"]
	html = openURL(urlF)
	soup = BeautifulSoup(html)
	#xbmc.log('[plugin.video.midiaflixhd] L188 ' + str(soup), xbmc.LOGNOTICE)	
	return urlF
	'''
	data = urllib.urlencode({'action':'players','id':idname})
	url = 'http://www.midiaflixhd.net/wp-admin/admin-ajax.php'
	req = urllib2.Request(url=url,data=data)
	content = urllib2.urlopen(req).read()
	#print content
	soup = BeautifulSoup(content)
	try:
		ef = soup.div['data-player-content']
	except TypeError:
		urlF = ''
		return urlF
	s = BeautifulSoup(ef)
	urlF = s.iframe['src']
	#print urlF
	return urlF
	'''

def pesquisa():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto	 = keyb.getText()
				pesquisa = urllib.quote(texto)
				url		 = base + '?s=%s' % str(pesquisa)

				hosts = []
				link  = openURL(url)
				link = unicode(link, 'utf-8', 'ignore')		
				soup	 = BeautifulSoup(link)
				conteudo = soup.findAll('div',{'class':'row movies-list'})
				filmes = conteudo[0]('a')
				totF = len(filmes)
				for filme in filmes:
						titF = filme["title"].encode('utf-8')
						urlF = filme["href"].encode('utf-8')
						imgF = filme.div.div["data-original"].encode('utf-8')	
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
		setViewFilmes()
		
def player(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('MegaFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		idsT = []
		url2 = []
		matriz = []
		
		link  = openURL(url) 
		xbmc.log('[plugin.video.midiaflixhd] L241 ' + str(url), xbmc.LOGNOTICE)		
		soup = BeautifulSoup(link)
		urlF = soup.iframe["data-lazy-src"]
		try:
		    html = openURL(urlF)
		    urlVideo = re.findall(r'var JWp = \{\'mp4file\': \'(.+?)\',', html)[0]
		    url2Play = urlVideo
		    OK = False
		    print urlVideo
		except:
		    print "Video Indisponivel"
		    return OK

		xbmc.log('[plugin.video.midiaflixhd] L325 ' + str(urlVideo), xbmc.LOGNOTICE)
		
		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
						
		if OK : url2Play = urlresolver.resolve(urlVideo)
		
		xbmc.log('[plugin.video.midiaflixhd] L343 ' + str(url2Play), xbmc.LOGNOTICE)
		
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
	
				
def player_series(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('MegaFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		idsT = []
		links = []
		hosts = []
		matriz = []
			
		t = requests.get(url)
		urlVideo = t.url

		xbmc.log('[plugin.video.midiaflixhd] L369 ' + str(urlVideo), xbmc.LOGNOTICE)
		#urlVideo = url
		#conteudo = soup('iframe')
		#urlVideo = conteudo[0]['src']
		'''
		try :
				conteudo = soup('iframe')
				srvsdub	 = conteudo[0]("src")
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
				conteudo = soup('iframe'})
				srvsleg	 = conteudo[0]("src")
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
		okID = urlVideo.split('embed/?v=')[1]
		urlVideo = okID
		'''
		xbmc.log('[plugin.video.midiaflixhd] L423 ' + str(urlVideo), xbmc.LOGNOTICE)

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
				
		if 'open.php' in urlVideo :
				nowID = urlVideo.split("id=")[1]
				urlVideo = 'https://openload.co/embed/%s' % nowID
				
		elif 'video.php' in urlVideo :
				nowID = urlVideo.split("id=")[1]
				urlVideo = 'https://openload.co/embed/%s' % nowID
				
		elif 'openload.php' in urlVideo :
				nowID = urlVideo.split("id=")[1]
				urlVideo = 'https://openload.co/embed/%s' % nowID
				
		elif 'thevid.net' in urlVideo :
				okID = urlVideo.split('e/')[1]
				urlVideo = 'http://thevid.net/e/%s' % okID	
				
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
		req = urllib2.Request(url)
		req.add_header('Referer',url)
		req.add_header('Upgrade-Insecure-Requests',1)
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
		
		if	 opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
		elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
		elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")
		
def setViewFilmes() :
		xbmcplugin.setContent(int(sys.argv[1]), 'movies')

		opcao = selfAddon.getSetting('filmesVisu')

		if	 opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
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

params	  = get_params()
url		  = None
name	  = None
mode	  = None
iconimage = None

try	   : url=urllib.unquote_plus(params["url"])
except : pass
try	   : name=urllib.unquote_plus(params["name"])
except : pass
try	   : mode=int(params["mode"])
except : pass
try	   : iconimage=urllib.unquote_plus(params["iconimage"])
except : pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)
print "Iconimage: "+str(iconimage)

###############################################################################################################

if	 mode == None : menuPrincipal()
elif mode == 10	  : getCategorias(url)
elif mode == 20	  : getFilmes(url)
elif mode == 25	  : getSeries(url)
elif mode == 26	  : getTemporadas(url)
elif mode == 27	  : getEpisodios(name,url)
elif mode == 30	  : doPesquisaSeries()
elif mode == 35	  : doPesquisaFilmes()
elif mode == 40	  : getFavoritos()
elif mode == 41	  : addFavoritos(name,url,iconimage)
elif mode == 42	  : remFavoritos(name,url,iconimage)
elif mode == 43	  : cleanFavoritos()
elif mode == 98	  : getInfo(url)
elif mode == 99	  : playTrailer(name,url,iconimage)
elif mode == 100  : player(name,url,iconimage)
elif mode == 110  : player_series(name,url,iconimage)
elif mode == 999  : openConfig()
elif mode == 1000 : openConfigEI()

xbmcplugin.endOfDirectory(int(sys.argv[1])) 