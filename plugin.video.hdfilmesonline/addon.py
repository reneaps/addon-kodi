﻿#####################################################################
#####################################################################
# -*- coding: UTF-8 -*-
#####################################################################
# Addon : HDFilmesOnlineOnline
# By AddonReneSilva - 12/06/2017
# Atualizado (1.0.0) - 12/06/2017
# Atualizado (1.0.1) - 14/06/2017
# Atualizado (1.0.2) - 15/06/2017
# Atualizado (1.0.3) - 17/07/2017
# Atualizado (1.0.4) - 10/08/2017
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver
from urlparse import urlparse

from resources.lib.BeautifulSoup		import BeautifulSoup
from resources.lib						import jsunpack

version   = '1.0.3'
addon_id  = 'plugin.video.hdfilmesonline'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder	= selfAddon.getAddonInfo('path')
artfolder	= addonfolder + '/resources/img/'
fanart		= addonfolder + '/fanart.png'
addon_handle = int(sys.argv[1])
base		= base64.b64decode('aHR0cDovL2hkZmlsbWVzb25saW5lZ3JhdGlzLm5ldC8=')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'					, base							,	10, artfolder + 'categorias.png')
		addDir('Coleções'					, base + 'colecoes/'				,	15, artfolder + 'filmes.png')
		addDir('Lançamentos'				, base + 'genero/lancamentos/'	,	20, artfolder + 'new.png')
		addDir('Filmes Dublados'			, base + '?s=dublado'			,	20, artfolder + 'filmes.png')
		addDir('Filmes 720p'				, base + 'qualidade/720p/'		,	20, artfolder + 'filmes.png')
		addDir('Filmes 2016'				, base + 'ano/2016/'				,	20, artfolder + 'filmes.png')
		addDir('Series'						, base + '?post_type=tvshows'		,	25, artfolder + 'series.png')
		addDir('Pesquisa Series'			, '--'							,	30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'			, '--'							,	35, artfolder + 'pesquisa.png')
		addDir('Configurações'				, base							,	 999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo'	,base							,  1000, artfolder + 'config.png', 1, False)
			
		setViewMenu()		
		
def getCategorias(url):
		link = openURL(url)
		#link = unicode(link, 'utf-8', 'ignore')	
		soup = BeautifulSoup(link)
		conteudo   = soup("div", {"class": "categorias"})
		categorias = conteudo[0]("li")
		totC = len(categorias)
		for categoria in categorias:
				titC = categoria.text.encode('utf-8', 'ignore')
				if not 'Lançamento' in titC :
								urlC = categoria.a["href"]
								imgC = artfolder + limpa(titC) + '.png'
								addDir(titC,urlC,20,imgC)
			
		setViewMenu()
		
def getColecoes(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)
		filmes = soup.findAll("div", {"class":"item"})
		totF = len(filmes)
		for i in range(totF):
				imgF = filmes[i].img['src']
				titF = filmes[i].img['alt'].encode('utf-8','replace')
				urlF = filmes[i].a['href']
				addDir(titF,urlF,20,imgF)
				#addDirF(titF, urlF, 100, imgF, False, totF, pltF)
		try :
				proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
				addDir('Próxima Página >>', proxima, 15, artfolder + 'proxima.png')
		except : 
				pass
				
		setViewFilmes()
		
def getFilmes(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		#xbmc.log('[plugin.video.hdfilmes] L125 ' + str(link), xbmc.LOGNOTICE)
		soup = BeautifulSoup(link)
		filmes = soup.findAll("div", {"class":"item"})
		totF = len(filmes)
		for databox in filmes:
				imgF = databox.img['src']
				titF = databox.img['alt'].encode('utf-8','replace')
				urlF = databox.a['href']
				soup = BeautifulSoup(str(databox))
				sinopse = soup.findAll("div", {"class":"boxinfo"})
				if sinopse :
					sinop = sinopse[0]("span", {"class":"ttx"})
					pltF = sinopse[0].text.encode('utf-8','replace')
					xbmc.log('[plugin.video.hdfilmes] L97 ' + str(sinop), xbmc.LOGNOTICE)
				else:
					pltF = ""
				addDirF(titF, urlF, 100, imgF, False, totF, pltF)
		try :
				proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except : 
				pass
				
		setViewFilmes()
							
def getSeries(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)
		conteudo = soup("div", {"class":"peliculas"})
		filmes = conteudo[0]("div",{"class":"item"})
		totF = len(filmes)
		for databox in filmes:
				imgF = databox.img['src']
				titF = databox.img['alt'].encode('utf-8','replace')
				urlF = databox.a['href']
				soup = BeautifulSoup(str(databox))
				sinopse = soup.find("div", {"class":"boxinfo"})
				if sinopse is None :
						pltF = ''
				else:
					sinopse = sinopse("span", {"class":"ttx"})
					pltF = sinopse[0].text.encode('utf-8','replace')
				addDirF(titF, urlF, 26, imgF, True, totF, pltF)
		try :
				proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except : 
				pass
		
def getTemporadas(url):
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)		
		seasons = soup.findAll('div', {'id':'seasons'})
		links  = seasons[0]('div', {'class':'se-c'})
		#print soup
		totF = len(links)
		imgF = []
		img = soup.find("div", {"class": "imagen"})
		imgF = img.img['src']
		urlF = url
		i = 0

		for i in range(totF):
			a = links[i]('span',{'class':'title'})
			titF = a[0].text.encode('utf-8','replace')
			titF = titF.replace('&#8217;', '\'')
			xbmc.log('[plugin.video.hdfilmes] L125 ' + str(titF), xbmc.LOGNOTICE)
			addDir(titF, urlF, 27, imgF, totF)


def getEpisodios(name, url):
		n = name.split(' - ')[1]
		n = n.replace('ª Temporada', '')	
		n = int(n)
		n = n-1
		temp = []
		episodios = []
	
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		
		soup = BeautifulSoup(link)
		episodios = soup.findAll('ul', {'class':'episodios'})
		links = episodios[n]('li')
		totF = len(links)

		imgF = []
		img = soup.find("div", {"class": "imagen"})
		imgF = img.img['src']
		
		for i in  range (0,len(links)):
				link = links[i].find('div', {'class':"numerando"})
				titF = links[i].find('div', {'class':"numerando"}).text.encode('utf-8','replace')
				urlF = links[i].a['href']
				titN = links[i]('div', {'class':"episodiotitle"})
				titN = titN[0].a.text.encode('utf-8','replace')
				titF = titF + " - " + titN
				addDirF(titF, urlF, 110, imgF, False, totF)
				
		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

def pesquisa():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto	 = keyb.getText()
				pesquisa = urllib.quote(texto)
				url		 = base + '?s=%s' % str(pesquisa)
				hosts = []
				
				link = openURL(url)
				link = unicode(link, 'utf-8', 'ignore')
				soup = BeautifulSoup(link)
				filmes = soup.findAll("div", {"class":"item"})
				totF = len(filmes)
				for databox in filmes:
					imgF = databox.img['src']
					titF = databox.img['alt'].encode('utf-8','replace')
					urlF = databox.a['href']
					soup = BeautifulSoup(str(databox))
					sinopse = soup.findAll("div", {"class":"boxinfo"})
					if sinopse :
						sinop = sinopse[0]("span", {"class":"ttx"})
						pltF = sinopse[0].text.encode('utf-8','replace')
						xbmc.log('[plugin.video.hdfilmes] L97 ' + str(sinop), xbmc.LOGNOTICE)
					else:
						pltF = ""
					temp = [urlF, titF, imgF, pltF]
					hosts.append(temp)
					
				a = []
				for url, titulo, img, pltf in hosts:
					temp = [url, titulo, img, pltf]
					a.append(temp);
				return a

def doPesquisaSeries():
		a = pesquisa()
		total = len(a)
		for url2, titulo, img, pltf in a:
			addDir(titulo, url2, 26, img, False, total)
			
def doPesquisaFilmes():
		a = pesquisa()
		total = len(a)
		for url2, titulo, img, pltF in a:
			#addDir(titulo, url2, 100, img, False, total)
			addDirF(titulo, url2, 100, img, False, total, pltF)
		setViewFilmes()
		
def player(name,url,iconimage):
		if "#" in url: 
			addon = xbmcaddon.Addon()
			addonname = addon.getAddonInfo('name')
			line1 = str(" - Episodio ainda não liberado!")
			xbmcgui.Dialog().ok(addonname, name+line1,'Por favor aguarde...')
			return
			
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('HDFilmesOnline', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		matriz = []
		urlF = []
		
		xbmc.log('[plugin.video.hdfilmes] L253 - ' + str(url), xbmc.LOGNOTICE)
		link  = openURL(url)
		link  = unicode(link, 'utf-8', 'ignore')
		soup  = BeautifulSoup(link)
		links = soup.findAll('div', {'class':'movieplay'})

		for i in  range (0,len(links)):
			link = links[i].iframe['src']
			xbmc.log('[plugin.video.hdfilmes] L261 - ' + str(link), xbmc.LOGNOTICE)
			#if not "hdfilmesonlinegratis" in link :
			urllink = ""
			if not "filmeshd.php" in link:
				if not "/hd/embed/" in link:
					if not "id=5090" in link:
						urllink = link.split('url=')[1]
						domain = urlparse(urllink)
						domain = domain.netloc.split('.')[0]
						urlF.append(urllink)
						titsT.append(domain)
			
		xbmc.log('[plugin.video.hdfilmes] L268 ' + str(urlF), xbmc.LOGNOTICE)
		
		if not titsT : return
		
		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)
		
		if index == -1 : return
		
		i = int(index)
		
		urlVideo = urlF[i]

		#links	= conteudo[0]('a')
		
		#if len(links) == 0 : links = conteudo[0]("a")
		
		#urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]
		
		#link = openURL(urlVideo)
		#soup  = BeautifulSoup(link)
		#conteudo = soup.findAll("iframe")
		#urlVideo = conteudo[2].get('src')
		
		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
		
		xbmc.log('[plugin.video.hdfilmes] L284 ' + str(urlVideo), xbmc.LOGNOTICE)

		if 'openload2' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'https://openload.co/embed/%s' % fxID
				
		elif 'ok' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'http://ok.ru/videoembed%s' % fxID
				
		elif 'thevid2' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'http://thevid.net/e/%s' % fxID
				linkTV	= openURL(urlVideo)		
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

def player_series(name,url,iconimage): 
		if "#" in url: 
			addon = xbmcaddon.Addon()
			addonname = addon.getAddonInfo('name')
			line1 = str(" - Episodio ainda não liberado!")
			xbmcgui.Dialog().ok(addonname, name+line1,'Por favor aguarde...')
			return
			
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('HDFilmesOnline', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)

		titsT = []
		urlF = []
		links = []
		hosts = []
		matriz = []
		
		xbmc.log('[plugin.video.hdfilmes] L245 - ' + str(url), xbmc.LOGNOTICE)
		link  = openURL(url)
		link  = unicode(link, 'utf-8', 'ignore')
		soup  = BeautifulSoup(link)
		links = soup("iframe")
		link = links[0].get("src")
		html = openURL(link)
		soup = BeautifulSoup(html)
		conteudo = soup("div",{"class":"geral"})
		links = conteudo[0]("a")
		
		for i in links:
			link =	i["onclick"]
			link2 = link.split("=")[1]
			link2 = link2.replace("\'","")
			link = link.split("=")[2]
			link = link.replace("\'","")
			srv	 = i.text.encode('utf-8','replace')
			#xbmc.log('[plugin.video.hdfilmes] L341 - ' + str(link), xbmc.LOGNOTICE)
			if not "hdfilmesonlinegratis" in link : 
				urlF.append(link)
				hosts.append(link2)
				titsT.append(srv)
			
		xbmc.log('[plugin.video.hdfilmes] L348 ' + str(urlF), xbmc.LOGNOTICE)
		
		if not titsT : return
		
		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)
		
		if index == -1 : return
		
		i = int(index)
		
		urlVideo = base + "v/t/" + hosts[i]

		#links	= conteudo[0]('a')
		
		#if len(links) == 0 : links = conteudo[0]("a")
		
		#urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]
		
		#link = openURL(urlVideo)
		#soup  = BeautifulSoup(link)
		#conteudo = soup.findAll("iframe")
		#urlVideo = conteudo[2].get('src')
		
		xbmc.log('[plugin.video.hdfilmes] L381 - ' + str(titsT[i]), xbmc.LOGNOTICE)

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

		if 'open' in titsT[i].lower() :
				fxID = urlF[i]
				urlVideo = 'https://openload.co/embed/%s' % fxID
				
		elif 'ok2' in urlVideo :
				fxID = urlF[i]
				urlVideo = 'http://ok.ru/videoembed%s' % fxID

		elif 'vidto' in titsT[i].lower() :
				fxID = urlF[i]
				urlVideo = 'http://vidto.me/embed-%s-850x550.html' % fxID

		elif 'vidzi' in titsT[i].lower() :
				fxID = urlF[i]
				urlVideo = 'http://vidzi.tv/%s.html' % fxID
						
		elif 'thevid' in titsT[i].lower() :
				fxID = urlF[i]
				urlVideo = 'http://thevid.net/e/%s' % fxID
				
		xbmc.log('[plugin.video.hdfilmes] 407 - ' + str(urlVideo), xbmc.LOGNOTICE)	
		
		if OK : 
			try:
				url2Play = urlresolver.resolve(urlVideo)
			except:
				dialog = xbmcgui.Dialog()
				dialog.ok(" Erro:", " Video removido! ")
				url2Play = []
				return
				pass
				
		if not url2Play : return

		legendas = '-'
		
		mensagemprogresso.update(75, 'Abrindo Sinal para ' + name,'Por favor aguarde...')
		
		playlist = xbmc.PlayList(1)
		playlist.clear()

		listItem = xbmcgui.ListItem(name,thumbnailImage=iconimage) 
		listItem.setPath(url2Play)
		listItem.setProperty('mimetype','video/mp4')
		listItem.setProperty('IsPlayable', 'true')
		playlist.add(url2Play,listItem)

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

		#return ok
				
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
		
def addDirF(name,url,mode,iconimage,pasta=True,total=1,plot='') :
		u  = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
		ok = True
		
		liz = xbmcgui.ListItem(name, iconImage="iconimage", thumbnailImage=iconimage)
		
		liz.setProperty('fanart_image', iconimage)
		liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": plot})
		
		cmItems = []
		
		cmItems.append(('[COLOR gold]Informações do Filme[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=98)'%(sys.argv[0], url)))
		cmItems.append(('[COLOR lime]Assistir Trailer[/COLOR]', 'XBMC.RunPlugin(%s?url=%s&mode=99)'%(sys.argv[0], urllib.quote_plus(url))))
		
		liz.addContextMenuItems(cmItems, replaceItems=False)
				
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta,totalItems=total)
		
		return ok	

def getInfo(url)	:
		link = openURL(url)
		#titO = re.findall('<h1 itemprop="name"><a href=".*?" title="(.*?)">.*?</a></h1>', link)[0]
		titO = re.findall('<span class="titulo_o"><i itemprop="name">(.*?)</i>.*?</span>', link)[0]
		titO = titO.replace('Assistir','').replace('Dublado','').replace('Legendado','').replace('Online','')
						
		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
		link = openURL(url)
		link  = unicode(link, 'utf-8', 'ignore')
		ytID = re.findall('<iframe width=".*?" height=".*?" src="//www.youtube.com/embed/(.*?)" frameborder="0" allowfullscreen></iframe>', link)[0]

		if not ytID : 
			addon = xbmcaddon.Addon()
			addonname = addon.getAddonInfo('name')
			line1 = str("Trailer não disponível!")
			xbmcgui.Dialog().ok(addonname, line1)	
			return

		xbmc.executebuiltin('XBMC.RunPlugin("plugin://plugin.video.youtube/play/?video_id=%s")' % ytID)
		#xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=youtubevideo, id=%s)' % ytID)
	
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
		elif opcao == '8': xbmc.executebuiltin("Container.SetViewMode(550)")
		elif opcao == '9': xbmc.executebuiltin("Container.SetViewMode(560)")
		
def limpa(texto):
		texto = texto.replace('ç','c').replace('ã','a').replace('õ','o')
		texto = texto.replace('â','a').replace('ê','e').replace('ô','o')
		texto = texto.replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
		texto = texto.replace(' ','-')
		texto = texto.lower()
		
		return texto
'''
def sinopse(urlF):
		link = openURL(urlF)
		#link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)
		conteudo = soup("div", {"class": "perfil_sinopse"})
		#print conteudo
		plot = conteudo[0].span.text
		return plot
'''
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
elif mode == 15	  : getColecoes(url)
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