﻿#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : MidiaFlixHD
# By AddonBrasil - 11/12/2015
# Atualizado (1.0.0) - 29/06/2018
# Atualizado (1.0.1) - 22/07/2018
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib				 import jsunpack
from time						 import time

version	  = '1.0.1'
addon_id  = 'plugin.video.midiaflixhd'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder	= addonfolder + '/resources/media/'
fanart		= addonfolder + '/fanart.png'
base		= base64.b64decode('aHR0cDovL3d3dy5taWRpYWZsaXhoZC5uZXQv')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'				, base + ''								,	10, artfolder + 'categorias.png')
		addDir('Lançamentos'			, base + 'filmes/'						,	20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'		, base + '?s=dublado'					,	20, artfolder + 'pesquisa.png')
		addDir('Seriados'				, base + 'series/'						,	25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'		, '--'									,	30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'		, '--'									,	35, artfolder + 'pesquisa.png')
		addDir('Configurações'			, base									,  999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo' , base								, 1000, artfolder + 'config.png', 1, False)

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
		try:
			conteudo = soup("div",{"class":"animation-2 items"})
			filmes = conteudo[0]('div',{'class':'poster'})
		except:
			conteudo = soup("div",{"class":"items"})
			filmes = conteudo[0]('div',{'class':'poster'})
			pass
		
		totF = len(filmes)

		for filme in filmes:
				titF = filme.img["alt"].encode("utf-8")
				urlF = filme.a["href"].encode('utf-8')
				imgF = filme.img["src"].encode('utf-8')
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
		conteudo = soup("div",{"id":"archive-content"})
		filmes = conteudo[0]('div',{'class':'poster'})
		
		totF = len(filmes)

		for filme in filmes:
				titF = filme.img["alt"].encode("utf-8")
				titF = titF.replace('assistir','').replace('online','')
				titF = titF.replace('Assistir','').replace('Online','')
				titF = titF.replace('á','a')
				urlF = filme.a["href"].encode('utf-8')
				imgF = filme.img["src"].encode("utf-8")
				xbmc.log('[plugin.video.midiaflixhd] L109 - ' + str(titF), xbmc.LOGNOTICE)
				addDir(titF, urlF, 26, imgF)

		try :
				proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except :
				pass

		setViewFilmes()

def getTemporadas(name,url,iconimage):
		html = openURL(url)
		soup = BeautifulSoup(html)
		xbmc.log('[plugin.video.midiaflixhd] L109 - ' + str(url), xbmc.LOGNOTICE)
		#print soup
		'''
		try:
				urlF = re.findall(r'<iframe src=".+?" data-lazy-src="(.+?)" width=".+?" height=".+?" frameborder="0" allowfullscreen="allowfullscreen"></iframe>', html)[0]
				xbmc.log('[plugin.video.midiaflixhd] L120 - ' + str(urlF), xbmc.LOGNOTICE)
		except:
			pass
		try:
				urlF = re.findall(r'<iframe width=".+?" height=".+?" src=".+?" data-lazy-src="(.+?)" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe>', html)[0]
				xbmc.log('[plugin.video.midiaflixhd] L125 - ' + str(urlF), xbmc.LOGNOTICE)
		except:
			pass
		try:
				urlF = re.findall(r'<iframe src=".+?" data-lazy-src="(.+?)" width=".+?" height=".+?">.+?</iframe>', html)[0]
				xbmc.log('[plugin.video.midiaflixhd] L128 - ' + str(urlF), xbmc.LOGNOTICE)
		except:
				pass
		try:
				urlF = re.findall('<iframe width=".+?" height=".+?" src=".+?" data-lazy-src="(.+?)" allowfullscreen></iframe>', html)[0]
		except:
				pass
		'''
		conteudo = soup("iframe")
		for i in conteudo:
				if not 'youtube' in str(i) : 
					urlF = i["data-lazy-src"]
		html = openURL(urlF)
		soup = BeautifulSoup(html)
		episodes = soup('a',{'class':'video'})
		servers = re.findall("addiframe\('(.*?)'\);", html)
		print len(episodes)
		total = len(servers)
		imgF = ''
		x = 0
		a = []
		for item in servers:
				urlF = servers[x]
				titF = episodes[x]["href"].encode("utf-8")
				a = re.findall(r'javascript: InitPlayer\(\'(.+?)\', \'(.+?)\',\'(.+?)\'\);' ,titF)[0]
				titF = 'S'+a[0]+'E'+a[1]
				if "dub" in a[2] : titF = titF + " - Dublado"
				if "leg" in a[2] : titF = titF + " - Legendado"
				titF = name + ': ' + titF
				x += 1
				addDirF(titF, urlF, 110, imgF, False, total)

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
		xbmc.log('[plugin.video.midiaflixhd] L295 - ' + str(url), xbmc.LOGNOTICE)
		soup = BeautifulSoup(link)
		try:
			urlF = soup.iframe["data-lazy-src"]
		except:
			pass
		try:
			urlF = soup.iframe["src"]
		except:
			pass
		xbmc.log('[plugin.video.midiaflixhd] L305 - ' + str(urlF), xbmc.LOGNOTICE)
		html = openURL(urlF)
		urlVideo = urlF
		try:
			urlVideo = re.findall(r'var JWp = \{\'mp4file\': \'(.+?)\',', html)[0]
			xbmc.log('[plugin.video.midiaflixhd] L310 - ' + str(html), xbmc.LOGNOTICE)
			url2Play = urlVideo
			OK = False
			print urlVideo
		except:
			pass	
		try:
			urlVideo = re.findall("addiframe\('(.*?)'\);", html)[0]
			html = openURL(urlVideo)
			url2Play = re.findall(r'\[\{\"type\": "video/mp4", \"label\": "HD", \"file\": "(.+?)"\}\],', html)[0]
			r = urllib2.urlopen(url2Play)
			url2Play = r.geturl()
			OK = False
			xbmc.log('[plugin.video.midiaflixhd] L325 - ' + str(url2Play), xbmc.LOGNOTICE)
		except:
			pass
		try:
			urlVideo = re.findall(r'file: "(.+?)",', html)[2]
			url2Play = urlVideo
			OK = False
			OK = False
			xbmc.log('[plugin.video.midiaflixhd] L333 - ' + str(url2Play), xbmc.LOGNOTICE)
		except:
			pass			

		xbmc.log('[plugin.video.midiaflixhd] L337 - ' + str(urlVideo), xbmc.LOGNOTICE)

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
		
		if 'video.php' in urlVideo :
				html = openURL(urlVideo)
				soup = BeautifulSoup(html)
				urlF = soup.iframe["src"]
				urlVideo = urlF
				xbmc.log('[plugin.video.midiaflixhd] L346 - ' + str(urlVideo), xbmc.LOGNOTICE)
				
		elif 'embed.mystream.to' in urlVideo:
				html = openURL(urlVideo)
				soup = BeautifulSoup(html)
				urlF = soup.source["src"]
				url2Play = urlF
				xbmc.log('[plugin.video.midiaflixhd] L353 - ' + str(urlVideo), xbmc.LOGNOTICE)
				OK = False

		elif 'playercdn.net' in urlVideo:
				html = openURL(urlVideo)
				soup = BeautifulSoup(html)
				urlF = soup.source["src"]
				url2Play = urlF
				xbmc.log('[plugin.video.midiaflixhd] L353 - ' + str(urlVideo), xbmc.LOGNOTICE)
				OK = False				
				
		if OK : url2Play = urlresolver.resolve(urlVideo)

		xbmc.log('[plugin.video.midiaflixhd] L358 - ' + str(url2Play), xbmc.LOGNOTICE)

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

		#t = requests.get(url)
		#urlVideo = t.url

		xbmc.log('[plugin.video.midiaflixhd] L351 ' + str(url), xbmc.LOGNOTICE)
		urlVideo = url
		url2Play = urlVideo
		OK = False

		xbmc.log('[plugin.video.midiaflixhd] L353 ' + str(url2Play), xbmc.LOGNOTICE)

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

		if 'open.php' in urlVideo :
				nowID = urlVideo.split("id=")[1]
				urlVideo = 'https://openload.co/embed/%s' % nowID


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
elif mode == 26	  : getTemporadas(name,url,iconimage)
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