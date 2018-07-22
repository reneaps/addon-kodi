#####################################################################
#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : BestFilmes
# By AddonReneSilva - 01/02/2017
# Atualizado (1.0.0) - 03/07/2018
# Atualizado (1.0.1) - 09/07/2018
# Atualizado (1.0.2) - 22/07/2018
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver
import requests

from bs4 			import BeautifulSoup
from urlparse 		import urlparse
#from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib	import jsunpack

addon_id  = 'plugin.video.bestfilmes'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder  = selfAddon.getAddonInfo('path')
artfolder    = addonfolder + '/resources/img/'
fanart       = addonfolder + '/fanart.png'
addon_handle = int(sys.argv[1])
base         = base64.b64decode('aHR0cDovL2Jlc3RmaWxtZXNoZC5jb20v')
base2        = base64.b64decode('aHR0cHM6Ly9tZWdhc2VyaWVoZC5jb20v')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'                , base								,   10, artfolder + 'categorias.png')
		addDir('Lançamentos'               , base  + 'category/lancamentos/' 	,	20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'           , base  + '?s=dublado&'		 		,	20, artfolder + 'pesquisa.png')
		addDir('Series'		               , base2 + 'series/' 					,   25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'           , '--'                           	,   30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'           , '--'                           	,   35, artfolder + 'pesquisa.png')
		addDir('Configurações'             , base                           	,  999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo', base                           	, 1000, artfolder + 'config.png', 1, False)

		setViewMenu()

def getCategorias(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link, "html.parser")
		conteudo = soup("ul", {"class": "sub-menu"})
		categorias = conteudo[0]("li")
		
		totC = len(categorias)
		
		for categoria in categorias:
				titC = categoria.a.text.encode('utf-8')
				titC = limpa(titC)
				titC = titC.title()
				if not "Lançamentos" in str(categoria):
						urlC = categoria.a["href"]
						imgC = artfolder + 'categorias.png'
						addDir(titC,urlC,20,imgC)

def getFilmes(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup     = BeautifulSoup(link, "html.parser")
		conteudo = soup("div", {"class": "item_1 items"})
		filmes   = conteudo[0]("div", {"class": "item"})

		totF = len(filmes)

		for filme in filmes:
				titF = filme.img["alt"].encode('utf-8','replace')
				urlF = filme.a["href"].encode('utf-8', 'ignore')
				if not 'teste' in titF: imgF = filme.img["src"].encode('utf-8', 'ignore')
				pltF = ''
				addDirF(titF, urlF, 100, imgF, False, totF, pltF)
		try :
				proxima = re.findall(r'<link rel="next" href="(.+?)" />', link)[0]
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except :
				pass

		setViewFilmes()

def getSeries(url):
		xbmc.log('[plugin.video.bestfilmes] L85 - ' + str(url), xbmc.LOGNOTICE)
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup     = BeautifulSoup(link, "html.parser")
		conteudo = soup("div", {"class": "animation-2 items"})
		filmes   = conteudo[0]("article", {"class": "item tvshows"})

		totF = len(filmes)

		for filme in filmes:
				titF = filme.img["alt"].encode('utf-8','replace')
				urlF = filme.a["href"].encode('utf-8', 'ignore')
				if not 'teste' in titF: imgF = filme.img["src"].encode('utf-8', 'ignore')
				xbmc.log('[plugin.video.bestfilmes] L97 - ' + str(imgF), xbmc.LOGNOTICE)
				pltF = ''
				addDir(titF, urlF, 26, imgF)
		try :
				proxima = re.findall(r'<link rel=\'next\' href=\'(.+?)\' />', link)[0]
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except :
				pass
				
		setViewFilmes()

def getTemporadas(url):
		xbmc.log('[plugin.video.bestfilmes] L108 - ' + str(url), xbmc.LOGNOTICE)
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link, "html.parser")
		links = soup("iframe")
		for i in links:
			if "playtop" in str(i) : urlF = i["src"]
		img = soup('div', {'id':'dt_galery'})
		#xbmc.log('[plugin.video.bestfilmes] L116 - ' + str(soup), xbmc.LOGNOTICE)
		imgF = img[0].img['src']
		link  = openURL(urlF)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link, "html.parser")
		conteudo = conteudo = soup("div", {"class": "box"})	
		linhas = conteudo[0]("ul", {"class": "menu-temps"})
		temporadas = linhas[0]("li")
		totF = len(temporadas)
		i = 1
		while i <= totF:
			titF = str(i) + "ª Temporada"
			addDir(titF, urlF, 27, imgF)
			i = i + 1

def getEpisodios(name, url, iconimage):
		xbmc.log('[plugin.video.bestfilmes] L131 - ' + str(name), xbmc.LOGNOTICE)
		n = name.replace('ª Temporada', '')
		temp = []
		episodios = []

		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link, "html.parser")
		links = soup.findAll('a',{'class':'video'})
		links2 = re.findall(r'addiframe\(\'(.+?)\'\);', link)
		epis = re.findall(r'<a class="video" href="javascript: InitPlayer\(\'(.+?)\', \'(.+?)\',\'(.+?)\'\);">(.+?)<\/a>', str(links))
		totF = len(links2)
		temp = []
		episodios = []
		imgF = iconimage
		
		for i in range(0, totF):
			if n in str(epis[i][0]) :
				if not "ximo" in str(epis[i][3]) :
					titS = epis[i][0]
					titE = epis[i][1]
					titT = epis[i][2]
					titF = epis[i][3].decode('unicode-escape').encode('utf-8')
					titF = titT.replace('dub', '(D)').replace('leg', '(L)') + " - " + titF
					urlF = links2[i]
					print epis[i][0],epis[i][1], epis[i][2], epis[i][3], links2[i]
					addDirF(titF, urlF, 110, imgF, False, totF)

def doPesquisaSeries(url):
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto    = keyb.getText()
				pesquisa = urllib.quote(texto)
				url      = base2 + '?s=%s&' % str(pesquisa)
				#getSeries(url)
				
				link = openURL(url)
				link = unicode(link, 'utf-8', 'ignore')
				xbmc.log('[plugin.video.bestfilmes] L171 - ' + str(url), xbmc.LOGNOTICE)
				soup     = BeautifulSoup(link, "html.parser")
				conteudo = soup("div", {"class": "search-page"})
				filmes   = conteudo[0]("div", {"class": "thumbnail animation-2"})

				totF = len(filmes)

				for filme in filmes:
						titF = filme.img["alt"].encode('utf-8','replace')
						urlF = filme.a["href"].encode('utf-8', 'ignore')
						if not 'teste' in titF: imgF = filme.img["src"].encode('utf-8', 'ignore')
						pltF = ''
						addDir(titF, urlF, 26, imgF)
				try :
						proxima = re.findall(r'<link rel=\'next\' href=\'(.+?)\' />', link)[0]
						addDir('Próxima Página >>', proxima, 30, artfolder + 'proxima.png')
				except :
						pass
		setViewFilmes()
		
def doPesquisaFilmes():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto    = keyb.getText()
				pesquisa = urllib.quote(texto)
				url      = base + '/?s=%s&' % str(pesquisa)
				getFilmes(url)

def player(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('BestFilmes', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)

		titsT = []
		matriz = []

		xbmc.log('[plugin.video.bestfilmes] L187 - ' + str(url), xbmc.LOGNOTICE)
		link = openURL(url)
		soup = BeautifulSoup(link, "html.parser")
		conteudo = soup('div', {'class':'movieplay'})
		urlF = conteudo[0].iframe["src"].encode('utf-8')
		link = openURL(urlF)
		links = re.findall(r'addiframe\(\'(.+?)\'\);', link)
		for i in links:
			u = i.replace('www.','')
			domain = urlparse(u).netloc.split('.')[0]
			titS = domain.title()
			if len(titS) > 0 : titsT.append(titS)
		'''
		soup  = BeautifulSoup(link, "html.parser")
		conteudo = soup('div', {'class':'embed'})
		try:
			srvsdub = conteudo[0]('button')
		except:
			ul = soup('ul', class_='menuPlayer')
			srvsdub = ul[0]('li')
			pass
		totD = len(srvsdub)
		titsT = []
		for i in srvsdub :
						try:
							titS = i['data-player'].encode('utf-8')
						except:
							titS = i.text
						if len(titS) > 0 : titsT.append(titS)
						print titsT
		'''
		
		if not titsT : return

		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)

		if index == -1 : return

		i = int(index)

		links = re.findall(r'addiframe\(\'(.+?)\'\);', link)

		urlVideo = links[i]
		xbmc.log('[plugin.video.bestfilmes] L257 - ' + str(urlVideo), xbmc.LOGNOTICE)

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

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
		xbmc.sleep(20000)
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
		xbmc.log('[plugin.video.bestfilmes] L314 - ' + str(url), xbmc.LOGNOTICE)
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('BestFilmes', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)

		titsT = []
		urlsF = []
		links = []
		hosts = []
		matriz = []

		urlVideo = url
		url2Play = urlVideo
		OK = False
		
		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

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
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		return link

def addDir(name, url, mode, iconimage, total=1, pasta=True):
		u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
		ok = True
		liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
		liz.setProperty('fanart_image', iconimage)
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
		titO = re.findall('<h1 title="(.+?)">\n.+?</h1>', link)[0]
		titO = titO.replace('Assistir','').replace('Dublado','').replace('Legendado','').replace('Online','')

		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
		link = openURL(url)
		ytID = re.findall('<div id="single">\n<meta itemprop="embedUrl" content="https://www.youtube.com/embed/(.+?)">.+?</div>', link)[0]

		if not ytID :
			addon = xbmcaddon.Addon()
			addonname = addon.getAddonInfo('name')
			line1 = str("Trailer não disponível!")
			xbmcgui.Dialog().ok(addonname, line1)
			return

		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=youtubevideo, id=%s)' % ytID)

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
		elif opcao == '8': xbmc.executebuiltin("Container.SetViewMode(550)")
		elif opcao == '9': xbmc.executebuiltin("Container.SetViewMode(560)")

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
elif mode == 27   : getEpisodios(name,url,iconimage)
elif mode == 30   : doPesquisaSeries(url)
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