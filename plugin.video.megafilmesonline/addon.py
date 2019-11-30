#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : Hora Da Pipoca
# By AddonBrasil - 11/12/2015
# Atualizado (1.0.1) - 15/12/2015
# Atualizado (1.1.0) - 12/03/2016
# Atualizado (2.0.0) - 03/08/2018
# Atualizado (2.0.9) - 15/05/2019
# Atualizado (2.1.0) - 19/06/2019
# Atualizado (2.1.1) - 20/07/2019
# Atualizado (2.1.2) - 21/11/2019
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import json
import urlresolver
import requests

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib				 import jsunpack
from time						 import time

version	  = '2.1.2'
addon_id  = 'plugin.video.megafilmesonline'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder	 = selfAddon.getAddonInfo('path')
artfolder	 = addonfolder + '/resources/img/'
fanart		 = addonfolder + '/fanart.png'
base		 = base64.b64decode('aHR0cHM6Ly93d3cuZmlsbWVzb25saW5laGR4Lm9yZy8=')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'					   , base + 'filme/'							,	 10, artfolder + 'categorias.png')
		addDir('Lançamentos'				, base + 'filmes-online/lancamentos/'	 ,	  20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'			, base + '?s=dublado'						 ,	  20, artfolder + 'pesquisa.png')
		addDir('Seriados'					 , base + 'assistir-serie/'							   ,	25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'			, '--'										  ,	   30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'			, '--'										  ,	   35, artfolder + 'pesquisa.png')
		addDir('Configurações'				  , base										,  999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo'	   , base										 , 1000, artfolder + 'config.png', 1, False)

		setViewMenu()

def getCategorias(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)
		conteudo   = soup("div", {"id": "homepage-items"})
		categorias = conteudo[0].findAll("a")
		totC = len(categorias)
		for categoria in categorias:
				#xbmc.log('[plugin.video.megahfilmeshd] L50 ' + str(categoria['href']), xbmc.LOGNOTICE)
				titC = categoria.text.encode('utf-8','replace')
				urlC = categoria["href"]
				imgC = artfolder + limpa(titC) + '.png'
				addDir(titC,urlC,20,imgC)

		setViewMenu()

def getFilmes(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)
		filmes = soup.findAll('div',{'class':re.compile('201')})
		totF = len(filmes)
		for filme in filmes:
				titF = filme.h2.text.encode('utf-8')
				urlF = filme.a["href"].encode('utf-8')
				imgF = filme.div["data-original"].encode('utf-8')
				addDirF(titF, urlF, 100, imgF, False, totF)

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
		conteudo = soup.findAll('div', {'class':'row movies-list theRow'})
		filmes = conteudo[0]('a')
		totF = len(filmes)

		for filme in filmes:
				urlF = filme["href"].encode('utf-8')
				imgF = filme.div["data-original"].encode('utf-8')
				titF = filme.find('div',{'class':'sort'}).text.encode('utf-8')
				titF = urlF.split('/')[4]
				titF = titF.replace('/','').replace('-',' ').replace('assistir','')
				titF = titF.replace(' as','').replace('todas','').replace('temporadas','')
				titF = titF.strip()
				titF = titF.title()
				addDir(titF, urlF, 26, imgF)

		try :
				proxima = re.findall('<link rel="next" href="(.*?)"', link)[0]
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except :
				pass

		xbmcplugin.setContent(int(sys.argv[1]), 'episodes')

def getTemporadas(url):
		link  = openURL(url)
		soup = BeautifulSoup(link)
		filmes = soup('div', {'class':'season'})
		seasons = filmes[0]('div',{'class':'item get_episodes changePlayer'})
		#info = soup('div', {'class':'infos'})
		#sname = info[0].h2.text.encode('utf-8')
		#xbmc.log('[plugin.video.megahfilmeshd] L117 ' + str(filmes), xbmc.LOGNOTICE)
		urlF = url
		totD = len(seasons)

		imgF = ""
		img = soup.find("div", {"class": "downloadImage"})
		imgF = re.findall(r'href=[\'"]?([^\'" >]+)', str(img))
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
		s = n
		temp = []
		episodios = []

		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')

		soup = BeautifulSoup(link)
		
		imgF = ""
		img = soup("div", {"class": "downloadImage"})
		imgF = re.findall(r'href=[\'"]?([^\'" >]+)', str(img))
		imgF = imgF[0]
		#xbmc.log('[plugin.video.megahfilmeshd] L152 ' + str(imgF), xbmc.LOGNOTICE)

		filmes = soup.findAll('div', {'class':'season'})
		info = soup('div', {'class':'infos'})
		sname = info[0].h2.text.encode('utf-8')
		seasons = filmes[0]('div',{'class':'item get_episodes changePlayer'})
		idseasons = seasons[n]['data-row-id']
		post_url = re.findall(r'''<link rel=\'shortlink\' href=\'(.+?)\' />''',link)[0]
		post_id = post_url.split('=')[1]
		data = urllib.urlencode({'post_id':post_id,'episodeos':idseasons})
		urlF = 'https://www.filmesonlinehdx.org/wp-content/themes/vizeratt/inc/parts/single/listas/se_post.php'
		req = urllib2.Request(url=urlF,data=data)
		req.add_header('Referer',url)
		req.add_header('content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36')
		response = urllib2.urlopen(req)
		content = response.read()
		response.close()
		soup = BeautifulSoup(content)
		conteudo = soup('div', {"class": "item get_player changePlayer"})
		b = conteudo

		for i in range(0, len(b)):
				titF = b[i].text.encode('utf-8')
				idname = b[i]['data-row-id']
				#xbmc.log('[plugin.video.megahfilmeshd] L177 ' + str(titF), xbmc.LOGNOTICE)
				urlF = pega(post_id, idname)
				if urlF == "" : titF = titF + ">>Indisponivel"
				temp = (urlF, titF)
				episodios.append(temp)

		total = len(episodios)

		for url, titulo in episodios:
				xbmc.log('[plugin.video.megahfilmeshd] L186 ' + str(url), xbmc.LOGNOTICE)
				addDirF(titulo, url, 110, imgF, False, total)

def pega(post_id,idname):
	data = urllib.urlencode({'id':post_id,'players':idname})
	urlF = 'https://www.filmesonlinehdx.org/wp-content/themes/vizeratt/inc/parts/single/player_post.php'
	req = urllib2.Request(url=urlF,data=data)
	req.add_header('Referer',url)
	req.add_header('content-type', 'application/x-www-form-urlencoded; charset=UTF-8')
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36')
	response = urllib2.urlopen(req)
	content = response.read()
	response.close()
	soup = BeautifulSoup(content)
	#xbmc.log('[plugin.video.megahfilmeshd] L200 ' + str(soup), xbmc.LOGNOTICE)
	okID = soup.a['href']
	okID = okID.split('token=')[1]
	urlF = base64.b64decode(okID)
	#xbmc.log('[plugin.video.megahfilmeshd] L205 ' + str(urlF), xbmc.LOGNOTICE)
	if 'video.php?v=' in urlF :
			okID = urlF.split('video.php?v=')[1]
			okID = okID.split('&')[0]
			#xbmc.log('[plugin.video.megahfilmeshd] L208 ' + str(okID), xbmc.LOGNOTICE)
			urlF = base64.b64decode(okID)
	return urlF


def pesquisa():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto	  = keyb.getText()
				pesquisa = urllib.quote(texto)
				url			= base + '?s=%s' % str(pesquisa)

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
		xbmc.log('[plugin.video.megahfilmeshd] L256 ' + str(url), xbmc.LOGNOTICE)
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('MegaFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)

		titsT = []
		idsT = []
		url2 = []
		matriz = []

		link  = openURL(url)
		soup	 = BeautifulSoup(link)
		conteudo = soup("div", {"class": "fullplayer"})
		article = conteudo[0]("div",{'class':"playerList playerListSmall"})
		srvsdub		= article[0]("a",{"class":"item get_player_content"})
		print srvsdub
		totD = len(srvsdub)
		print totD
		for i in range(totD) :
				#urlF = srvsdub[i]['data-player-content']
				#iframe = BeautifulSoup(urlF)
				#urlD = iframe.iframe['src']
				urlD = srvsdub[i]['href']
				xbmc.log('[plugin.video.megahfilmeshd] L280 ' + str(srvsdub), xbmc.LOGNOTICE)
				'''
				if totD == 1 :
					urlVideo = urlD
				else:
					link  = openURL(urlD)
					#link  = unicode(link, 'utf-8', 'ignore')
					soup	 = BeautifulSoup(link)
					#urlVideo = soup.iframe['src']
					links = soup.findAll('iframe')
					if len(links) == 1 :
						#urlVideo = links[0]['src']
						urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(link))[0]
					else:
						xbmc.log('[plugin.video.megahfilmeshd] L294 ' + str(link), xbmc.LOGNOTICE)
						#urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(link))[0]
						token = re.findall(r'<a href="http://acessoaoface.info/redir.php\?token=(.+?)" target="_blank" class="big-icon-link">', str(link))[0]
						urlVideo = base64.b64decode(token)
						xbmc.log('[plugin.video.megahfilmeshd] L298 ' + str(urlVideo), xbmc.LOGNOTICE)
						#urlVideo = links[1]['src']
						#opID =	   urlVideo.split('?')[1]
						#opID = opID.split('=')[1]
						#urlVideo = "http://openload.co/embed/" + opID
				'''
				srv = srvsdub[i].text
				titsT.append(srv)
				url2.append(urlD)

		if not titsT : return

		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

		if index == -1 : return

		i = index
		urlVideo = url2[i]

		if 'javascript' in urlVideo :
				html = openURL(urlVideo)
				soup = BeautifulSoup(html)
				xbmc.log('[plugin.video.megahfilmeshd] L320 ' + str(urlVideo), xbmc.LOGNOTICE)
				urlVideo = soup.iframe["src"]
		elif 'action' in urlVideo :
				html = openURL(urlVideo)
				soup = BeautifulSoup(html)
				urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(html))[0]
				xbmc.log('[plugin.video.megahfilmeshd] L326 ' + str(urlVideo), xbmc.LOGNOTICE)
		elif 'token=' in urlVideo :
				okID = urlVideo.split('token=')[1]
				urlVideo = base64.b64decode(okID)
				if 'video.php?v=' in urlVideo :
						okID = urlVideo.split('video.php?v=')[1]
						try:
							okID = okID.split('&')[0]
						except:
							pass
						url2Play = base64.b64decode(okID)
						OK = False
				xbmc.log('[plugin.video.megahfilmeshd] L334 ' + str(url2Play), xbmc.LOGNOTICE)
		'''
		t = requests.get(urlVideo)
		urlVideo = t.url
		'''
		
		#conteudo = soup("div", {"class": "player-video"})
		#links = conteudo[i]("iframe")

		#if len(links) == 0 : links = conteudo[0]("a")

		#urlVideo = re.findall(r'data-src=[\'"]?([^\'" >]+)', str(links))[0]
		#okID = urlVideo.split('embed/?v=')[1]
		#urlVideo = okID


		xbmc.log('[plugin.video.megahfilmeshd] L350 ' + str(urlVideo), xbmc.LOGNOTICE)

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
		
		if 'nowvideo.php' in urlVideo :
				nowID = urlVideo.split("id=")[1]
				urlVideo = 'http://embed.nowvideo.sx/embed.php?v=%s' % nowID

		elif 'megahdfilmes.com' in urlVideo :
				okID = urlVideo.split('url=')[1]
				okID = base64.b64decode(okID)
				if 'type=o' in okID:
					okID = okID.replace('id=','').replace('&type=o','')
					urlVideo = 'https://openload.co/embed/%s' % okID
				elif 'type=v' in okID:
					okID = okID.replace('id=','').replace('&type=v','')
					urlVideo = 'https://verystream.com/e/%s' % okID
				elif 'type=t' in okID:
					okID = okID.replace('id=','').replace('&type=t','')
					urlVideo = 'https://thevid.net/e/%s' % okID
				xbmc.log('[plugin.video.megahfilmeshd] L370 ' + str(urlVideo), xbmc.LOGNOTICE)

		elif 'thevid.net' in urlVideo :
				okID = urlVideo.split('e/')[1]
				urlVideo = 'http://thevid.net/e/%s' % okID

		if OK : url2Play = urlresolver.resolve(urlVideo)

		xbmc.log('[plugin.video.megahfilmeshd] L378 ' + str(url2Play), xbmc.LOGNOTICE)

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
		url2 = []
		matriz = []
		'''
		data = url
		url = 'https://megahdfilmes.com/wp-admin/admin-ajax.php'
		req = urllib2.Request(url=url,data=data)
		req.add_header('Referer',url)
		req.add_header('Upgrade-Insecure-Requests',1)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.36 Safari/537.36')
		content = urllib2.urlopen(req).read()
		soup = BeautifulSoup(content)
		srvsdub	= soup("div",{"class":"item get_player_content"})
		print srvsdub
		totD = len(srvsdub)
		print totD
		for i in range(totD) :
				urlF = srvsdub[i]['data-player-content']
				iframe = BeautifulSoup(urlF)
				urlD = iframe.iframe['src']
				if totD == 1 :
					urlVideo = urlD
				else:
					link  = openURL(urlD)
					link  = unicode(link, 'utf-8', 'ignore')
					soup	 = BeautifulSoup(link)
					#urlVideo = soup.iframe['src']
					links = soup.findAll('iframe')
					if len(links) == 1 :
						#urlVideo = links[0]['src']
						urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(link))[0]
					else:
						urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(link))[0]
						xbmc.log('[plugin.video.megahfilmeshd] L455 ' + str(urlVideo), xbmc.LOGNOTICE)
						#urlVideo = links[1]['src']
						#opID =	   urlVideo.split('?')[1]
						#opID = opID.split('=')[1]
						#urlVideo = "http://openload.co/embed/" + opID
				srv = srvsdub[i].text
				titsT.append(srv)
				url2.append(urlVideo)

		if not titsT : return

		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

		if index == -1 : return

		i = index
		urlVideo = url2[i]

		xbmc.log('[plugin.video.megahfilmeshd] L473 ' + str(urlVideo), xbmc.LOGNOTICE)
		if 'javascript' in urlVideo :
				html = openURL(urlVideo)
				soup = BeautifulSoup(html)
				xbmc.log('[plugin.video.megahfilmeshd] L477 ' + str(urlVideo), xbmc.LOGNOTICE)
				urlVideo = soup.iframe["src"]
		if 'action' in urlVideo :
				html = openURL(urlVideo)
				soup = BeautifulSoup(html)
				urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(html))[0]
				xbmc.log('[plugin.video.megahfilmeshd] L483 ' + str(urlVideo), xbmc.LOGNOTICE)
				
		t = requests.get(urlVideo)
		urlVideo = t.url
		'''
		urlVideo = url
		
		xbmc.log('[plugin.video.megahfilmeshd] L490 ' + str(urlVideo), xbmc.LOGNOTICE)

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

		if 'openload' in urlVideo :
				nowID = urlVideo.split("ed/")[1]
				urlVideo = 'https://openload.co/embed/%s' % nowID

		elif 'thevid.net' in urlVideo :
				okID = urlVideo.split('e/')[1]
				urlVideo = 'http://thevid.net/e/%s' % okID
		
		elif 'cdn' in urlVideo :
				url2Play = urlVideo
				xbmc.log('[plugin.video.megahfilmeshd] L504 ' + str(url2Play), xbmc.LOGNOTICE)
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
		headers = {
		"Referer": url,
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36"
	}
		req = urllib2.Request(url, "",headers)
		req.get_method = lambda: 'GET'
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

		if	   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
		elif opcao == '1': xbmc.executebuiltin("Container.SetViewMode(51)")
		elif opcao == '2': xbmc.executebuiltin("Container.SetViewMode(500)")

def setViewFilmes() :
		xbmcplugin.setContent(int(sys.argv[1]), 'movies')

		opcao = selfAddon.getSetting('filmesVisu')

		if	   opcao == '0': xbmc.executebuiltin("Container.SetViewMode(50)")
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

params		= get_params()
url			 = None
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

if	   mode == None : menuPrincipal()
elif mode == 10		 : getCategorias(url)
elif mode == 20		 : getFilmes(url)
elif mode == 25		 : getSeries(url)
elif mode == 26		 : getTemporadas(url)
elif mode == 27		 : getEpisodios(name,url)
elif mode == 30		 : doPesquisaSeries()
elif mode == 35		 : doPesquisaFilmes()
elif mode == 40		 : getFavoritos()
elif mode == 41		 : addFavoritos(name,url,iconimage)
elif mode == 42		 : remFavoritos(name,url,iconimage)
elif mode == 43		 : cleanFavoritos()
elif mode == 98		 : getInfo(url)
elif mode == 99		 : playTrailer(name,url,iconimage)
elif mode == 100  : player(name,url,iconimage)
elif mode == 110  : player_series(name,url,iconimage)
elif mode == 999  : openConfig()
elif mode == 1000 : openConfigEI()

xbmcplugin.endOfDirectory(int(sys.argv[1]))