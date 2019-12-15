#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : FilmesOnlinePlus
# By AddonBrasil - 22/11/2019
# Atualizado (1.0.0) - 22/11/2019
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests
import resources.lib.moonwalk as moonwalk

from bs4 import BeautifulSoup
from resources.lib import jsunpack
from time import time

version   = '1.0.0'
addon_id  = 'plugin.video.filmesonlineplus'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/media/'
fanart      = addonfolder + '/resources/fanart.png'
#base        = base64.b64decode('aHR0cHM6Ly9vdmVyZmxpeC5uZXQv')
base 		= 'https://filmesonline.plus/'
sbase       = 'http://www.serieshd.biz/'
v_views     = 'navegar/filmes-1/?alphabet=all&sortby=v_views&sortdirection=desc'

############################################################################################################

def menuPrincipal():
		addDir('Categorias Filmes'          , base + ''                             ,        10, artfolder + 'categorias.png')
		#addDir('Categorias Series'          , base + sbase                          ,        10, artfolder + 'categorias.png')
		addDir('Lançamentos'                , base + 'lancamento/'                  ,        20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'            , base + '?s=dublado'                   ,        20, artfolder + 'pesquisa.png')
		#addDir('Filmes Mais Assistidos'     , base + v_views                         ,        20, artfolder + 'pesquisa.png')
		addDir('Series'                     , sbase 	                           ,        25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'            , '--'                                 ,        30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'            , '--'                                  ,        35, artfolder + 'pesquisa.png')
		addDir('Configurações'              , base                                  ,       999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo' , base                                  ,      1000, artfolder + 'config.png', 1, False)

		setViewMenu()

def getCategorias(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link, 'html.parser')
		if 'filmes' in url :
			conteudo   = soup("ul",{"id":"menu-principal"})
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
		xbmc.log('[plugin.video.FilmesOnlinePlus] L75 - ' + str(url), xbmc.LOGNOTICE)
		link = openURL(url)
		link = unicode(link, 'utf-8', 'replace')
		soup = BeautifulSoup(link, 'html.parser')
		conteudo = soup('div', attrs={'class':'galeria'})
		filmes = conteudo[0]('div', attrs={'class':'box-filme'})
		totF = len(filmes)

		for filme in filmes:
				titF = filme.a['title'].encode("utf-8")
				titF = titF.replace('Assistir','X').replace('Online','')
				urlF = filme.a['href'].encode("utf-8")
				imgF = filme.img['src'].encode("utf-8")
				#xbmc.log('[plugin.video.FilmesOnlinePlus] L85 - ' + str(filme), xbmc.LOGNOTICE)
				addDirF(titF, urlF, 100, imgF, False, totF)

		try :
				next_page = soup('div', attrs={'class':'wp-pagenavi'})[0]
				proxima = next_page('a', attrs={'class':'next page-numbers'})[0]
				proxima = proxima['href']
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except :
				pass

		setViewFilmes()

def getSeries(url):
		xbmc.log('[plugin.video.FilmesOnlinePlus] L96 - ' + str(url), xbmc.LOGNOTICE)
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')        
		soup = BeautifulSoup(link, 'html.parser')
		conteudo = soup('section', attrs={'class':'conteudo'})
		dados = conteudo[0]('ul', attrs={'id':'posts'})
		filmes = dados[0]('li')

		for filme in filmes:
				titF = filme.a["title"].encode("utf-8")
				titF = titF.replace('Assistir','').replace('Online','')
				urlF = filme.a["href"].encode('utf-8')
				image_news = filme.img['src'] #('div', {'class':'vb_image_container'})[0]
				imgF = image_news #re.findall(r'url\(\'(.+?)\'\);',str(image_news))[0]
				addDir(titF, urlF, 26, imgF)

		try :
				next_page = soup('li', attrs={'class':'ipsPagination_next'})[0]
				proxima = next_page.a['href']
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except :
				pass

		xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(name,url,iconimage):
		xbmc.log('[plugin.video.FilmesOnlinePlus] L122 - ' + str(url), xbmc.LOGNOTICE)
		html = openURL(url)
		soup = BeautifulSoup(html,'html.parser')
		sname = soup.title.text.replace('-','|').split('|')[0]
		sname = sname.replace('Assistir','').replace('Online','')
		sname = sname.replace('Assistir','').replace('online','')
		data = soup('div', {'class':'capa'})
		imgF = data[0].img['src']
		conteudo = soup('div', {'class':'server'})
		dados = conteudo[0]('ul', {'class':'tempnum'})
		filmes = dados[0]('li')
		totF = len(filmes)
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
		xbmc.log('[plugin.video.FilmesOnlinePlus] L150 - ' + str(url), xbmc.LOGNOTICE)
		n = re.findall(r'(.+?)ª Temporada.+', name)[0]
		html = openURL(url)
		soup = BeautifulSoup(html,'html.parser')
		sname = soup.title.text.replace('-','|').split('|')[0]
		sname = sname.replace('Assistir','').replace('Online','')
		sname = sname.replace('Assistir','').replace('online','')
		data = soup('div', {'class':'capa'})
		imgF = data[0].img['src']
		conteudo = soup('div', attrs={'class':'servidor'})
		dados = conteudo[0]('div', {'class':'temp'+n+'-view'})

		try:
			dub = dados[0]('ul', {'class':'dub'})
			epis_dub = dub[0]('li')
			totF = len(epis_dub)
			for i in epis_dub:
				urlF = i.a['href']
				titF = i.span.text.encode('utf-8') + i.a.text.encode('utf-8') + '(Dub)'
				addDirF(titF, urlF, 110, imgF, False, totF)
		except:
			pass

		try:
			leg = dados[0]('ul', {'class':'leg'})
			epis_leg = leg[0]('li')
			totF = len(epis_leg)
			for i in epis_leg:
				urlF = i.a['href']
				titF = i.span.text.encode('utf-8') + i.a.text.encode('utf-8') + '(Leg)'
				addDirF(titF, urlF, 110, imgF, False, totF)
		except:
			pass

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
				soup = BeautifulSoup(link, 'html.parser')
				conteudo = soup('div', attrs={'class':'galeria'})
				filmes = conteudo[0]('div', attrs={'class':'box-filme'})
				totF = len(filmes)

				for filme in filmes:
						titF = filme.a['title'].encode("utf-8")
						titF = titF.replace('Assistir','X').replace('Online','')
						urlF = filme.a['href'].encode("utf-8")
						imgF = filme.img['src'].encode("utf-8")
						temp = [urlF, titF, imgF]
						hosts.append(temp)

				return hosts

def doPesquisaSeries():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes/Series')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto = keyb.getText()
				pesquisa = urllib.quote(texto)
				data = '' #urllib.urlencode({'term':pesquisa})
				url = sbase + '?s=' + pesquisa

		xbmc.log('[plugin.video.FilmesOnlinePlus] L231 - ' + str(url), xbmc.LOGNOTICE)
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')        
		soup = BeautifulSoup(link, 'html.parser')
		conteudo = soup('section', attrs={'class':'conteudo'})
		dados = conteudo[0]('ul', attrs={'id':'posts'})
		filmes = dados[0]('li')
		totF = len(filmes)

		for filme in filmes:
				titF = filme.a["title"].encode("utf-8")
				titF = titF.replace('Assistir','').replace('Online','')
				urlF = filme.a["href"].encode('utf-8')
				image_news = filme.img['src'] #('div', {'class':'vb_image_container'})[0]
				imgF = image_news #re.findall(r'url\(\'(.+?)\'\);',str(image_news))[0]
				addDir(titF, urlF, 26, imgF, False, totF)
			
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
		mensagemprogresso.create('FilmesOnlinePlus', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		titsT = []
		idsT = []
		
		urlF = url
		xbmc.log('[plugin.video.FilmesOnlinePlus] L240 - ' + str(urlF), xbmc.LOGNOTICE)
		link = openURL(urlF)
		soup = BeautifulSoup(link, 'html.parser')
		data = soup('div', {'id':'opcoes-player'})
		btn = data[0]('a',{'class':'nome-server'})
		#xbmc.log('[plugin.video.FilmesOnlinePlus] L246 - ' + str(btn), xbmc.LOGNOTICE)

		for s in btn:
			hname = s.text
			titsT.append(hname)
			#idsT.append(hkey)

		if not titsT : return

		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

		if index == -1 : return

		i = int(index) + 1

		conteudo = soup('div', {'id':'player-video'})
		players = conteudo[0]('iframe')
		#xbmc.log('[plugin.video.FilmesOnlinePlus] L262 - ' + str(players), xbmc.LOGNOTICE)
		urlF = players[i]['data-src']

		if 'index.html' in urlF :
			fxID = urlF.split('id=')[1]
			url2Play = 'https://002.yandexcloud.ga/drive/hls/%s/%s.m3u8' % (fxID, fxID)
		else :
			res = urlF.split('/')[4]
			url2Play = base64.b64decode(res + "===")

		xbmc.log('[plugin.video.FilmesOnlinePlus] L272 - ' + str(url2Play), xbmc.LOGNOTICE)

		OK = False

		urlVideo = ''
				
		#xbmc.log('[plugin.video.FilmesOnlinePlus] L278 - ' + str(urlVideo), xbmc.LOGNOTICE)

		if OK :
			try:
				xbmc.log('[plugin.video.FilmesOnlinePlus] L282 - ' + str(urlVideo), xbmc.LOGNOTICE)
				url2Play = urlresolver.resolve(urlVideo)
			except:
				dialog = xbmcgui.Dialog()
				dialog.ok(" Erro:", " Video removido! ")
				url2Play = []
				pass

		if not url2Play : return

		xbmc.log('[plugin.video.FilmesOnlinePlus] L298 - ' + str(url2Play), xbmc.LOGNOTICE)

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
		#xbmc.log('[plugin.video.FilmesOnlinePlus] L398 - ' + str(url), xbmc.LOGNOTICE)
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('FilmesOnlinePlus', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		titsT = []
		idsT = []

		xbmc.log('[plugin.video.FilmesOnlinePlus] L346 - ' + str(url), xbmc.LOGNOTICE)


		if 'campanha.php' in url :
			urlF = url.split('id=')[1]
			st = urlF.split('&')[0]
			urlF = ''.join( reversed(st) )
			urlF = base64.b64decode(urlF)
			xbmc.log('[plugin.video.FilmesOnlinePlus] L354 - ' + str(urlF), xbmc.LOGNOTICE)	
			#ss = btn.split('/?&')[1].split('&')
		
		try:
			ss = urlF.split('/?&')[1].split('&')
		except:
			ss = urlF.split('/?')[1].split('&')
			pass

		for s in ss:
			hname = s.split('=')[0]
			if 'very' not in hname:
    				if 'open' not in hname:
							hkey = s.split('=')[1]
							titsT.append(hname)
							idsT.append(hkey)

		if not titsT : return

		try:

			index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

			if index == -1 : return

			i = int(index)
			urlVideo = titsT[i]

			if 'verystream' in urlVideo:
				fxID = str(idsT[i])
				urlVideo = 'https://verystream.com/e/%s' % fxID
					
			elif 'mix' in urlVideo :
					fxID = str(idsT[i])
					urlVideo = 'https://mixdrop.co/e/%s' % fxID
					data = openURL(urlVideo)
					#url2Play = re.findall('MDCore.vsrc = "(.*?)";', data)[0]
					#url2Play = 'http:%s' % url2Play if url2Play.startswith("//") else url2Play
					sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
					aMatches = re.compile(sPattern).findall(data)
					sUnpacked = jsunpack.unpack(aMatches[0])
					xbmc.log('[plugin.video.FilmesOnlinePlus] L379 - ' + str(sUnpacked), xbmc.LOGNOTICE)
					url2Play = re.findall('MDCore.vsrc="(.*?)"', sUnpacked)
					url = str(url2Play[0])
					url2Play = 'http:%s' % url if url.startswith("//") else url
					OK = False

			elif 'only' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'https://onlystream.tv/e/%s' % fxID
				'''
				headers = {
					'Referer': urlvideo,
					'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
					'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
					'Connection':'keep-alive',
					'upgrade-insecure-requests': '1'}
				xbmc.log('[plugin.video.FilmesOnlinePlus] L301 - ' + str(urlvideo), xbmc.LOGNOTICE)
				r = requests.get(url=urlVideo, headers=headers)
				data = r.content
				url2Play = re.findall('sources\:\s*\[{file\:"([^"]+)",', data)[0]
				xbmc.log('[plugin.video.FilmesOnlinePlus] L474 - ' + str(url2Play), xbmc.LOGNOTICE)
				OK = False
				'''
				
			elif 'streamango' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'https://streamango.com/embed/%s' % fxID

			elif 'vt=' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'http://vidto.me/embed-%s.html' % fxID

			elif 'ok=' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'https://ok.ru/videoembed/%s' % fxID

			elif 'vidlox' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'https://vidlox.me/embed-%s' % fxID
			 		 			 		 
			elif 'raptu' in urlVideo :
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
				 
			elif 'netu' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'https://waaw.tv/watch_video.php?v=%s' % fxID
 
			elif 'vidoza' in urlVideo :
					fxID = str(idsT[i])
					urlVideo = 'https://vidoza.net/embed-%s.html' % fxID

			elif 'stream' in urlVideo :
					fxID = str(idsT[i])
					urlVideo = 'https://streamz.cc/%s' % fxID
																		   
			elif 'jetload' in urlVideo :
				fxID = str(idsT[i])
				urlVideo = 'https://jetload.net/e/%s' % fxID

			elif 'principal' in urlVideo :
				fxID = str(idsT[i+1])
				urlVideo = 'https://www.rapidvideo.com/e/%s' % fxID
				
			xbmc.log('[plugin.video.FilmesOnlinePlus] L440 - ' + str(urlVideo), xbmc.LOGNOTICE)
				
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

		xbmc.log('[plugin.video.FilmesOnlinePlus] L487 - ' + str(url2Play), xbmc.LOGNOTICE)

		legendas = '-'

		mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')

		playlist = xbmc.PlayList(1)
		playlist.clear()


		if "m3u8" in url2Play:
				#ip = addon.getSetting("inputstream")
				url2Play = url2Play.split('|')[0]
				xbmc.log('[plugin.video.FilmesOnlinePlus] L500 - ' + str(url2Play), xbmc.LOGNOTICE)
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

def getInfo(url)    :
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

if   mode == None : menuPrincipal()
elif mode == 10   : getCategorias(url)
elif mode == 20   : getFilmes(url)
elif mode == 25   : getSeries(url)
elif mode == 26   : getTemporadas(name,url,iconimage)
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