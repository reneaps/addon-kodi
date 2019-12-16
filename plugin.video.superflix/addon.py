#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : SuperFlix
# By AddonBrasil - 06/12/2019
# Atualizado (1.0.0) - 06/12/2019
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests
import resources.lib.moonwalk as moonwalk

from bs4 import BeautifulSoup
from resources.lib import jsunpack
import time

version	  = '1.0.0'
addon_id  = 'plugin.video.superflix'
selfAddon = xbmcaddon.Addon(id=addon_id)
addon = xbmcaddon.Addon()
_handle = int(sys.argv[1])

addonfolder = selfAddon.getAddonInfo('path')
artfolder	= addonfolder + '/resources/media/'
fanart		= addonfolder + '/resources/fanart.png'
#base		 = base64.b64decode('aHR0cHM6Ly9vdmVyZmxpeC5uZXQv')
base		= 'https://www.superflix.net/'
sbase		= 'navegar/series-2/?alphabet=all&sortby=v_started&sortdirection=desc'
v_views		= 'filmes-e-series-online-top-mais-vistos/'

############################################################################################################

def menuPrincipal():
		addDir('Categorias Filmes'			, base + 'assistir-filmes-online/'		 	,	 10, artfolder + 'categorias.png')
		addDir('Categorias Series'			, base + 'assistir-series-online/'		 	,	 10, artfolder + 'categorias.png')
		addDir('Lançamentos'				, base + 'categoria/assistir-filmes-lancamentos-2019-online/' ,		20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'			, base + 'categoria/assistir-filmes-dublados-online/' ,	 20, artfolder + 'pesquisa.png')
		addDir('Filmes Mais Assistidos'	 	, base + v_views							,	 20, artfolder + 'pesquisa.png')
		addDir('Series'						, base + 'assistir-series-online/'			,	 25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'			, '--'										,	 30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'			, '--'										,	 35, artfolder + 'pesquisa.png')
		addDir('Configurações'				, base										,	999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo' , base										,  1000, artfolder + 'config.png', 1, False)

		setViewMenu()

def getCategorias(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link, 'html5lib')
		conteudo = soup("div",{"class":"Rght BgA"})
		menu   = conteudo[0]("nav",{"class":"Menu"})
		if 'filmes' in url :
				filmes = menu[0]("li",{'id':'menu-item-485'})
				categorias = filmes[0]('li')
		elif 'series' in url:
				series = menu[0]("li",{'id':'menu-item-876'})
				categorias = series[0]('li')

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
		xbmc.log('[plugin.video.SuperFlix] L75 - ' + str(url), xbmc.LOGNOTICE)
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		   
		soup = BeautifulSoup(link, "html5lib")
		conteudo = soup('main')
		dados = conteudo[0]('ul')
		lista = dados[0]('li')
		totF = len(lista)
		
		for f in lista:
				filme = f('article', attrs={'class':'TPost C'})
				titF = filme[0].a.text.encode('utf-8')
				urlF = filme[0].a['href']
				imgF = filme[0].img['src']
				imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
				#xbmc.log('[plugin.video.SuperFlix] L85 - ' + str(filme), xbmc.LOGNOTICE)
				if 'TV' not in filme[0].a.span.text : addDirF(titF, urlF, 100, imgF, False, totF)

		try :
				next_page = soup('div', attrs={'class':'wp-pagenavi'})
				pg = next_page[0]('a', attrs={'class':'next page-numbers'})[0]
				proxima = pg['href']
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except :
				pass

		setViewFilmes()

def getSeries(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		   
		soup = BeautifulSoup(link, "html5lib")
		conteudo = soup('main')
		dados = conteudo[0]('ul')
		lista = dados[0]('li')
		
		for f in lista:
				filme = f('article', attrs={'class':'TPost C'})
				titF = filme[0].a.text.encode('utf-8')
				urlF = filme[0].a['href'].encode('utf-8')
				imgF = filme[0].img['src'].encode('utf-8')
				imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
				addDir(titF, urlF, 26, imgF)

		try :
				next_page = soup('div', attrs={'class':'wp-pagenavi'})
				pg = next_page[0]('a', attrs={'class':'next page-numbers'})[0]
				proxima = pg['href']
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except :
				pass

		xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(name,url,iconimage):
		link = openURL(url)
		soup = BeautifulSoup(link, "html5lib")
		conteudo = soup('main')
		dados = conteudo[0]('article', attrs={'class':'TPost Single'})
		figure = dados[0]('div', {'class':'Image'})
		imgF = figure[0].img['src']
		imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
		seasons = conteudo[0]('div',{'class':'Wdgt AABox'})
		totF = len(seasons)
		i = 0

		for i in range(totF):
				i = i + 1
				titF = str(i) + "ª Temporada"
				urlF = url
				addDirF(titF, urlF, 27, imgF, True, totF)
				
		xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
		xbmc.log('[plugin.video.SuperFlix] L148 - ' + str(url), xbmc.LOGNOTICE)
		n = name.replace('ª Temporada', '')
		n = int(n)
		n = n - 1
		link = openURL(url)
		soup = BeautifulSoup(link, "html5lib")
		conteudo = soup('main')
		dados = conteudo[0]('article', attrs={'class':'TPost Single'})
		figure = dados[0]('div', {'class':'Image'})
		imgF = figure[0].img['src']
		seasons = conteudo[0]('div',{'class':'Wdgt AABox'})
		dados = seasons[n]('div',{'class':'TPTblCn AA-cont'})
		episodes = dados[0]('td',{'class':'MvTbImg B'})
		totF = len(episodes)
		#print(episodes)
		for i in episodes:
			urlF = i.a['href'].encode('utf-8')
			titF = urlF.split('/')[4].encode('utf-8')
			try:
				imgF = i.img['src']
			except:
				pass
			imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
			xbmc.log('[plugin.video.SuperFlix] L167 - ' + str(imgF), xbmc.LOGNOTICE)
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

				data = '' #urllib.urlencode({'term':pesquisa})
				url = base + '?s=' + pesquisa

				headers = {'Referer': url, 
						   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
						   'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
						   'Connection': 'keep-alive',
						   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
				}
				r = requests.post(url=url, data=data, headers=headers)
				link = r.content
				link = unicode(link, 'utf-8', 'replace')
				soup = BeautifulSoup(link, "html5lib")
				conteudo = soup('main')
				dados = conteudo[0]('ul')
				lista = dados[0]('li')
				totF = len(lista)
				
				for f in lista:
						filme = f('article', attrs={'class':'TPost C'})
						titF = filme[0].h3.text.encode('utf-8')
						urlF = filme[0].a['href']
						imgF = filme[0].img['src']
						imgF = 'http:%s' % imgF if imgF.startswith("//") else imgF
						temp = [urlF, titF, imgF]
						hosts.append(temp)

				return hosts

def doPesquisaSeries():
		a = pesquisa()
		if a is None : return
		total = len(a)
		for url2, titulo, img in a:
			addDir(titulo, url2, 26, img, False, total)
			
		xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
		
def doPesquisaFilmes():
		a = pesquisa()
		if a is None : return
		total = len(a)
		for url2, titulo, img in a:
			addDirF(titulo, url2, 100, img, False, total)

		setViewFilmes()

def player(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('SuperFlix', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		titsT = []
		idsT = []
		
		r = requests.get(url)
		html = r.content
		soup = BeautifulSoup(html, "html5lib")
		conteudo = soup('main')
		srvs = conteudo[0]('ul',{'class':'TPlayerNv'})
		srvs = srvs[0]('li')
		
		for s in srvs:
			titsT.append(s.text)

		if not titsT : return

		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

		if index == -1 : return

		i = int(index)
		
		tplayer = conteudo[0]('div',{'class':'TPlayer'})
		servers = tplayer[0]('div',{'class':'TPlayerTb'})
		totF = len(servers)
		for s in servers:
			try:
				urlS = s.iframe['src']
				idsT.append(urlS)
				print(urlS)
			except:
				l = s.get_text('src')
				urlS = re.findall(r'src="(.*?)"', l)[0].replace('#038;','')
				idsT.append(urlS)
				print(urlS)
				pass
				
		filme = idsT[i]
		
		r = requests.get(filme)
		html = r.content
		soup = BeautifulSoup(html, "html5lib")
		urlF = soup('iframe')[0]['src']
		xbmc.log('[plugin.video.SuperFlix] L270 - ' + str(urlF), xbmc.LOGNOTICE)
		if 'play' in urlF :
			headers = {'Referer': urlF, 
			   'Upgrade-Insecure-Requests': '1',
			   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
			   }
			r = requests.get(urlF)
			link = r.text
			link = openURL(urlF)
			urlF = r.url
			#urlVideo = re.findall(r'\"file\":\"(.*?)\"', link)[0]
		
		xbmc.log('[plugin.video.SuperFlix] L281 - ' + str(urlF), xbmc.LOGNOTICE)

		if 'index.html' in urlF :
			fxID = urlF.split('id=')[1]
			t = int(round(time.time() * 1000))
			#urlF = 'https://lbplus.sfplayer.net/hls/%s/%s.playlist.m3u8?t=%s' % (fxID, fxID, t)
			#urlF = 'https://slave1plus.sfplayer.net/hls/%s/%s.m3u8' % (fxID, fxID)
			#urlF = 'https://slave1plus.sfplayer.net/vl/%s?t=%s' % (fxID, t)
			#'https://002.yandexcloud.ga/drive/hls/%s/%s.m3u8' % (fxID, fxID)
			url2Play = urlF 
		else :
			res = urlF.split('/')[4]
			url2Play = base64.b64decode(res + "===")

		xbmc.log('[plugin.video.SuperFlix] L290 - ' + str(url2Play), xbmc.LOGNOTICE)

		OK = False
		
		if OK :
			try:
				xbmc.log('[plugin.video.SuperFlix] L282 - ' + str(urlVideo), xbmc.LOGNOTICE)
				url2Play = urlresolver.resolve(urlVideo)
			except:
				dialog = xbmcgui.Dialog()
				dialog.ok(" Erro:", " Video removido! ")
				url2Play = []
				pass

		if not url2Play : return

		xbmc.log('[plugin.video.SuperFlix] L298 - ' + str(url2Play), xbmc.LOGNOTICE)

		legendas = '-'

		mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

		playlist = xbmc.PlayList(1)
		playlist.clear()

		if "m3u8" in url2Play:
				#ip = addon.getSetting("inputstream")
				listitem = xbmcgui.ListItem(name, path=url2Play)
				listitem.setArt({"thumb": iconimage, "icon": iconimage})
				listitem.setProperty('IsPlayable', 'true')
				listitem.setMimeType('application/vnd.apple.mpegurl')
				listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
				listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
				playlist.add(url2Play,listitem)
		else:
				listitem = xbmcgui.ListItem(name, path=url2Play)
				listitem.setArt({"thumb": iconimage, "icon": iconimage})
				listitem.setProperty('IsPlayable', 'true')
				listitem.setMimeType('video/mp4')
				playlist.add(url2Play,listitem)
				
		xbmcPlayer = xbmc.Player()
		
		while xbmcPlayer.play(playlist) :
			xbmc.sleep(20000)
			if not xbmcPlayer.isPlaying():
				xbmc.stop()

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
		xbmc.log('[plugin.video.SuperFlix] L318 - ' + str(url), xbmc.LOGNOTICE)
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('SuperFlix', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		titsT = []
		idsT = []

		r = requests.get(url)
		html = r.content
		soup = BeautifulSoup(html, "html5lib")
		conteudo = soup('main')
		srvs = conteudo[0]('ul',{'class':'TPlayerNv'})
		srvs = srvs[0]('li')
		
		for s in srvs:
			titsT.append(s.text)

		if not titsT : return

		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

		if index == -1 : return

		i = int(index)
		
		tplayer = conteudo[0]('div',{'class':'TPlayer'})
		servers = tplayer[0]('div',{'class':'TPlayerTb'})
		totF = len(servers)
		for s in servers:
			try:
				urlS = s.iframe['src']
				idsT.append(urlS)
				print(urlS)
			except:
				l = s.get_text('src')
				urlS = re.findall(r'src="(.*?)"', l)[0].replace('#038;','')
				idsT.append(urlS)
				print(urlS)
				pass
				
		filme = idsT[i]
		
		r = requests.get(filme)
		html = r.content
		soup = BeautifulSoup(html, "html5lib")
		urlF = soup('iframe')[0]['src']
		xbmc.log('[plugin.video.SuperFlix] L410 - ' + str(urlF), xbmc.LOGNOTICE)
		headers = {'Referer': urlF, 
		   'Upgrade-Insecure-Requests': '1',
		   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0'
		   }
		r = requests.get(urlF) #,headers)
		link = r.text
		#link = openURL(urlF)
		urlVideo = r.url #re.findall(r'\"file\":\"(.*?)\"', link)[0]
		
		if 'index.html' in urlVideo :
			fxID = urlVideo.split('id=')[1]
			t = int(round(time.time() * 1000))
			#urlVideo = 'https://lbplus.sfplayer.net/hls/%s/%s.playlist.m3u8?t=%s' % (fxID, fxID, t)
			#urlVideo = 'https://slave1plus.sfplayer.net/hls/%s/%s.m3u8' % (fxID, fxID)
			#urlVideo = 'https://slave1plus.sfplayer.net/vl/%s?t=%s' % (fxID, t)
			#'https://002.yandexcloud.ga/drive/hls/%s/%s.m3u8' % (fxID, fxID)
			url2Play = urlVideo
			OK =False
		elif 'play' in urlVideo :
			res = urlVideo.split('/')[4]
			url2Play = base64.b64decode(res + "===")
			OK = False
			
		try:

			if 'mix' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'https://mixdrop.co/e/%s' % fxID
				data = openURL(urlVideo)
				#url2Play = re.findall('MDCore.vsrc = "(.*?)";', data)[0]
				#url2Play = 'http:%s' % url2Play if url2Play.startswith("//") else url2Play
				sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
				aMatches = re.compile(sPattern).findall(data)
				sUnpacked = jsunpack.unpack(aMatches[0])
				xbmc.log('[plugin.video.SuperFlix] L379 - ' + str(sUnpacked), xbmc.LOGNOTICE)
				url2Play = re.findall('MDCore.vsrc="(.*?)"', sUnpacked)
				url = str(url2Play[0])
				url2Play = 'http:%s' % url if url.startswith("//") else url
				OK = False

			elif 'drive.google.com' in urlVideo :
				OK = True

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

			elif 'vidoza' in urlVideo :
					fxID = str(idsT[i])
					urlVideo = 'https://vidoza.net/embed-%s.html' % fxID
									   
			elif 'jetload' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'https://jetload.net/e/%s' % fxID

			elif 'stream/' in urlVideo :
				url2Play = urlVideo
				OK = False
				
			xbmc.log('[plugin.video.SuperFlix] L488 - ' + str(urlVideo), xbmc.LOGNOTICE)
				
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

		xbmc.log('[plugin.video.SuperFlix] L504 - ' + str(url2Play), xbmc.LOGNOTICE)

		legendas = '-'

		mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

		playlist = xbmc.PlayList(1)
		playlist.clear()

		if "playlist.m3u8" in url2Play:
				ip = addon.getSetting("inputstream")
				listitem = xbmcgui.ListItem(name, path=url2Play)
				listitem.setArt({"thumb": iconimage, "icon": iconimage})
				listitem.setProperty('IsPlayable', 'true')
				listitem.setMimeType("application/vnd.apple.mpegurl")
				listitem.setProperty("inputstreamaddon", "inputstream.adaptive")
				listitem.setProperty("inputstream.adaptive.manifest_type", "hls")
				playlist.add(url2Play,listitem)
		else:
				listitem = xbmcgui.ListItem(name, path=url2Play)
				listitem.setArt({"thumb": iconimage, "icon": iconimage})
				listitem.setProperty('IsPlayable', 'true')
				listitem.setMimeType("video/mp4")
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

		liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)

		liz.setProperty('fanart_image', fanart)
		liz.setInfo(type = "Video", infoLabels = {"title": name})

		cmItems = []

		cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
		cmItems.append(('[COLOR red]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?name=%s&url=%s&iconimage=%s&mode=99)'%(sys.argv[0], urllib.quote(name), url, urllib.quote(iconimage))))

		liz.addContextMenuItems(cmItems, replaceItems=False)

		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)

		return ok

def getInfo(url)	:
		link = openURL(url)
		soup = BeautifulSoup(link, 'html.parser')
		conteudo = soup('div', {'class':'col-thumb'})
		title = conteudo[0]('div', {'class':'thumb'})
		titO = title[0].img['alt'].encode('utf-8')
		titO = titO.replace('Legendado','').replace('Dublado','').replace('Nacional','')
		titO = titO.replace('HD','').replace('Full','').replace('2019','').replace('Filme','')

		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
		link = openURL(url)
		ytID = re.findall('<iframe width="560" height="315" src="https://www.youtube.com/embed/(.*?)" .+?></iframe>', link)[0]
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

try		  : url=urllib.unquote_plus(params["url"])
except : pass
try		  : name=urllib.unquote_plus(params["name"])
except : pass
try		  : mode=int(params["mode"])
except : pass
try		  : iconimage=urllib.unquote_plus(params["iconimage"])
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