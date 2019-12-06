#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : BKSeries
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
from time import time

version	  = '1.0.0'
addon_id  = 'plugin.video.bkseries'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder	= addonfolder + '/resources/media/'
fanart		= addonfolder + '/resources/fanart.png'
#base		 = base64.b64decode('aHR0cHM6Ly9vdmVyZmxpeC5uZXQv')
base		= 'https://www.bkseries.com/'
sbase		= 'navegar/series-2/?alphabet=all&sortby=v_started&sortdirection=desc'
v_views		= 'navegar/filmes-1/?alphabet=all&sortby=v_views&sortdirection=desc'

############################################################################################################

def menuPrincipal():
		#addDir('Categorias Filmes'			 , base + ''							 ,		  10, artfolder + 'categorias.png')
		#addDir('Categorias Series'			 , base + sbase							 ,		  10, artfolder + 'categorias.png')
		#addDir('Lançamentos'				 , base + 'lancamento/'					 ,		  20, artfolder + 'lancamentos.png')
		#addDir('Filmes Dublados'			 , base + '?s=dublado'					 ,		  20, artfolder + 'pesquisa.png')
		#addDir('Filmes Mais Assistidos'	 , base + v_views						  ,		   20, artfolder + 'pesquisa.png')
		addDir('Series'						, base									,		 25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'			, '--'									,		 30, artfolder + 'pesquisa.png')
		#addDir('Pesquisa Filmes'			, '--'									,		 35, artfolder + 'pesquisa.png')
		addDir('Configurações'				, base									,		999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo' , base									,	   1000, artfolder + 'config.png', 1, False)

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
		soup = BeautifulSoup(link, 'html5lib')
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
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		   
		soup = BeautifulSoup(link, "html5lib")
		conteudo = soup('ul', attrs={'class':'lista-filmes'})
		filmes = conteudo[0]('li')
		
		for filme in filmes:
				filme = filme('div', attrs={'class':'capa'})
				titF = filme[0].a.text.encode("utf-8")
				urlF = filme[0].a['href'].encode("utf-8")
				imgF = filme[0].img['src'].encode("utf-8")
				addDirF(titF, urlF, 26, imgF)

		try :
				next_page = soup('div', attrs={'class':'navigation open-sans'})
				pg = next_page[0]('a', attrs={'class':'next page-numbers'})[0]
				proxima = pg['href']
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except :
				pass

		xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')

def getTemporadas(name,url,iconimage):
		html = openURL(url)
		soup = BeautifulSoup(html, "html5lib")
		i = soup('div',{'class':'capa-single'})
		imgF = i[0].img['src']
		t = soup('div', attrs={'class':'content content-single'})
		tt = t[0]('ul', attrs={'class':'tabs'})
		tt = tt[0]('li')
		totF = len(tt)
		urlF = url
		xbmc.log('[plugin.video.FilmesOnlinePlus] L129 - ' + str(tt), xbmc.LOGNOTICE)
		for i in tt :
			titF = i.a.text.encode("utf-8") + ' Temporada'
			try:
				addDir(titF, urlF, 27, imgF, True, totF)
			except:
				pass
				
		xbmcplugin.setContent(handle=int(sys.argv[1]), content='seasons')

def getEpisodios(name, url):
		n = name.replace('ª Temporada', '')
		n = int(n)
		n = n - 1
		link = openURL(url)
		soup = BeautifulSoup(link, "html5lib")
		i = soup('div',{'class':'capa-single'})
		imgF = i[0].img['src']
		conteudo = soup('div', attrs={'class':'tab_content'})
		partes = conteudo[n]('div',attrs={'class':'um_terco'})
		xbmc.log('[plugin.video.FilmesOnlinePlus] L149 - ' + str(url), xbmc.LOGNOTICE)

		try:
			e = partes[0]('li')
			totF = len(e)
			for i in e :
				urlF = i.a['href']
				urlF = urlF.split('v=')[-1]
				urlF = 'https://www.bkseries.com/video/blogger.php?v=' + urlF
				titF = i.a['title']
				addDirF(titF, urlF, 110, imgF, False, totF)
		except:
			pass
		try:
			f = partes[1]('li')
			totF = len(f)
			for i in f :
				urlF = i.a['href']
				urlF = urlF.split('v=')[-1]
				urlF = 'https://www.bkseries.com/video/blogger.php?v=' + urlF
				titF = i.a['title']
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
				
				link = openURL(url)
				link = unicode(link, 'utf-8', 'ignore')	
				soup = BeautifulSoup(link, "html5lib")
				conteudo = soup('ul', attrs={'class':'lista-filmes'})
				filmes = conteudo[0]('li')
				
				for filme in filmes:
						filme = filme('div', attrs={'class':'capa'})
						titF = filme[0].a.text.encode("utf-8")
						urlF = filme[0].a['href'].encode("utf-8")
						imgF = filme[0].img['src'].encode("utf-8")
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

		listitem = xbmcgui.ListItem(name,thumbnailImage=iconimage)
		listitem.setPath(url2Play)
		#listitem.setProperty('mimetype','video/m3u8')
		listitem.setProperty('IsPlayable', 'true')
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
		
		link = openURL(url)
		soup = BeautifulSoup(link, "html5lib")
		conteudo = soup('div',{'class':'geral'})
		filmes = conteudo[0]('div', {'class':'itens'})
		filmes = filmes[0]('a')
		totF = len(filmes)

		xbmc.log('[plugin.video.FilmesOnlinePlus] L344 - ' + str(totF), xbmc.LOGNOTICE)

		for s in filmes:
			hname = s.text.encode('utf-8')
			u = s['onclick']
			u = u.replace('window.location.href=','').replace('\'','')
			xbmc.log('[plugin.video.FilmesOnlinePlus] L349 - ' + str(u), xbmc.LOGNOTICE)
			hkey = u
			titsT.append(hname)
			idsT.append(hkey)

		if not titsT : return

		try:

			index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

			if index == -1 : return

			i = int(index)
			
			urlVideo = idsT[i]

			if 'jw.php' in urlVideo:
				fxID = urlVideo.split('v=')[-1]
				url2Play = 'https://www.bkseries.com/videozin/video-play.mp4/?contentId=%s' % fxID
				OK = False
				
			elif 'yt.php' in urlVideo:
				fxID = urlVideo.split('contentId=')[-1]
				url2Play = 'https://www.bkseries.com/videozin/video-play.mp4/?contentId=%s' % fxID
				OK = False
				
			elif 'xbox.php' in urlVideo:
				fxID = urlVideo.split('v=')[-1]
				url2Play = 'https://www.bkseries.com/videozin/video-play.mp4/?contentId=%s' % fxID
				OK = False

			xbmc.log('[plugin.video.FilmesOnlinePlus] L379 - ' + str(urlVideo), xbmc.LOGNOTICE)
				
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

		xbmc.log('[plugin.video.FilmesOnlinePlus] L532 - ' + str(url2Play), xbmc.LOGNOTICE)

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