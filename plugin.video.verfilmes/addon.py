﻿#####################################################################
#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : VerFilmes
# By AddonReneSilva - 17/02/2017
# Atualizado (1.0.0) - 17/02/2017
# Atualizado (1.0.1) - 27/07/2017
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib               import jsunpack

addon_id  = 'plugin.video.verfilmes'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder  = selfAddon.getAddonInfo('path')
artfolder    = addonfolder + '/resources/img/'
fanart       = addonfolder + '/fanart.png'
addon_handle = int(sys.argv[1])
base         = base64.b64decode('aHR0cDovL3d3dy52ZXJmaWxtZXMuYml6Lw==')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'                , base							,   10, artfolder + 'categorias.png')
		addDir('Lançamentos'               , base + 'categoria/lancamento-de-2016/'	,	20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'           , base + 'search.php?s=dublado' 	,	20, artfolder + 'pesquisa.png')
		addDir('Series'		               , base + 'categoria/series/'		,   25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'           , '--'                           ,   30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'           , '--'                           ,   35, artfolder + 'pesquisa.png')
		addDir('Configurações'             , base                           ,  999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo', base                           , 1000, artfolder + 'config.png', 1, False)
			
		setViewMenu()		
		
def getCategorias(url):
		link = openURL(url)
		#link = unicode(link, 'utf-8', 'ignore')	
		soup = BeautifulSoup(link)
		conteudo   = soup("div", {"id": "sidebar"})
		categorias = conteudo[0]("li")
		totC = len(categorias)
		for categoria in categorias:
				titC = categoria.text.encode('utf-8', 'ignore')
				if not 'Lançamento' in titC :
								urlC = categoria.a["href"]
								imgC = artfolder + limpa(titC) + '.png'
								addDir(titC,urlC,20,imgC)
			
		setViewMenu()
		
def getFilmes(url):
		link = openURL(url)
		#link = unicode(link, 'utf-8', 'ignore')
		soup     = BeautifulSoup(link)
		conteudo = soup("div", {"id": "postagem"})
		filmes = conteudo[0]("div",{"class":"capa"})
		urls = conteudo[0]("a")
		totF = len(filmes)
		
		for x in range(0, totF):
				titF = filmes[x].img["title"].encode('utf-8','replace')
				urlF = urls[x].get("href").encode('utf-8','replace')
				pltF = sinopse(urlF)
				imgF = filmes[x].img["src"].encode('utf-8', 'ignore')
				addDirF(titF, urlF, 100, imgF, False, totF, pltF)
		try : 
				prox = re.findall('<a href="(.*?)/page/(.*?)">.*?</a>', link)
				i = len(prox)
				i = int(i)
				i = (i-1)
				proxima = prox[i][0] + "/page/" + prox[i][1]
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except : 
				pass
				
		#setViewFilmes()
							
def getSeries(url):
		link = openURL(url)
		#link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)
		conteudo = soup("div", {"id": "postagem"})
		filmes = conteudo[0]("div",{"class":"capa"})
		urls = conteudo[0]("a")
		totF = len(filmes)

		for x in range(0, totF):
				titF = filmes[x].img["title"].encode('utf-8','replace')
				urlF = urls[x].get("href").encode('utf-8','replace')
				pltF = sinopse(urlF)
				imgF = filmes[x].img["src"].encode('utf-8', 'ignore')
				addDirF(titF, urlF, 26, imgF, True, totF, pltF)
		try : 
				prox = re.findall('<a href="(.*?)/page/(.*?)">.*?</a>', link)
				i = len(prox)
				i = int(i)
				i = (i-1)
				proxima = prox[i][0] + "/page/" + prox[i][1]
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except : 
				pass
		#setViewFilmes()
		
def getTemporadas(url):
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)		
		conteudo = soup("div", {"class": "conteudo"})
		linhas = conteudo[0]("ul", {"class": "itens"})
		temporadas = linhas[0]("li",{"id":"tempnresponsive"})
		totF = len(temporadas)
		imgF = []
		img = soup.find("div", {"class": "playingconteudo"})
		imgF = img.img['src']
		urlF = url
		i = 0

		for i in range(totF):
			i = i + 1
			titF = str(i) + "ª Temporada"
			xbmc.log('[plugin.video.verfilmes] L125 ' + str(imgF), xbmc.LOGNOTICE)
			addDir(titF, urlF, 27, imgF, False, totF)


def getEpisodios(name, url):
		xbmc.log('[plugin.video.verfilmesBiz] L130 - ' + str(url), xbmc.LOGNOTICE)
		n = name.replace('ª Temporada', '')	
		n = int(n)
		temp = []
		episodios = []
	
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')		

		soup = BeautifulSoup(link)
		conteudo = soup("div", {"class": "videos"})
		arquivo = conteudo[0]("li", {"class": "video" + str(n) + "-code"})
	
		try:
			temporadas = arquivo[0]('table')
			filmes = temporadas[0]('a')		
			audio = str(arquivo[0].span.text)

			totF = len(filmes)

			for filme in filmes:
					titF = filme.text.encode('utf-8', 'ignore')
					titF = titF.replace('Assistir ','').replace('Filme ','') + " " +audio #" Dublado"
					titF = str(n) + "T " + titF
					urlF = filme.get("href").encode('utf-8', 'ignore')
					urlF = base + urlF
					temp = (titF, urlF)
					episodios.append(temp)
		except:
			pass
			
		try:
			temporadas = arquivo[0]('table')
			filmes = temporadas[1]('a')		
			audio = str(temporadas[1].span.text)

			totF = len(filmes)

			for filme in filmes:
					titF = filme.text.encode('utf-8', 'ignore')
					titF = titF.replace('Assistir ','').replace('Filme ','') + " " +audio #" Legendado"
					titF = str(n) + "T " + titF
					urlF = filme.get("href").encode('utf-8', 'ignore')
					urlF = base + urlF
					temp = (titF, urlF)
					episodios.append(temp)
		except:
			pass
			
		audio = []
		imgF = []
		img = soup.find("div", {"class": "playingconteudo"})
		imgF = img.img['src']
		
		total = len(episodios)
		
		for titF, urlF in episodios:
				addDir(titF, urlF, 110, imgF, False, totF)

def pesquisa():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto    = keyb.getText()
				pesquisa = urllib.quote(texto)
				url      = base + 'search.php?s=%s' % str(pesquisa)
				hosts = []
				
				link = openURL(url)
				#link = unicode(link, 'utf-8', 'ignore')
				soup     = BeautifulSoup(link)
				
				conteudo = soup("div", {"id": "postagem"})
				filmes = conteudo[0]("div",{"class":"capa"})
				urls = conteudo[0]("a")
				totF = len(filmes)
				
				for x in range(0, totF):
					titF = filmes[x].img["title"].encode('utf-8','replace')
					urlF = urls[x].get("href").encode('utf-8','replace')
					pltF = sinopse(urlF)
					imgF = filmes[x].img["src"].encode('utf-8', 'ignore')
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
		xbmc.log('[plugin.video.verfilmes] L229 - ' + str(a), xbmc.LOGNOTICE)
		if a is None:
			xbmcgui.Dialog().ok('VerFilmes', 'Conteudo temporariamente indisponivel,desculpe o transtorno.')
			return 
		total = len(a)
		for url2, titulo, img in a:
			addDir(titulo, url2, 100, img, False, total)
			
def player(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('VerFilmes', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		matriz = []

		link = openURL(url)
		soup  = BeautifulSoup(link)
		conteudo = soup("div", {"class":"opcoes-r"})
		srvsdub = conteudo[0]('a')
		totD = len(srvsdub)
		titsT = []
		for i in range(totD) :
						titS = srvsdub[i].text
						titsT.append(titS)
						print titsT
		
		if not titsT : return
		
		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)
		
		if index == -1 : return
		
		i = int(index)

		links  = conteudo[0]('a')
		
		if len(links) == 0 : links = conteudo[0]("a")
		
		urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]
		
		link = openURL(urlVideo)
		soup  = BeautifulSoup(link)
		conteudo = soup.findAll("iframe")
		urlVideo = conteudo[2].get('src')
		
		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')
		
		xbmc.log('[plugin.video.verfilmes] L279 ' + str(urlVideo), xbmc.LOGNOTICE)

		if 'openload2' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'https://openload.co/embed/%s' % fxID
				
		elif 'ok' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'http://ok.ru/videoembed%s' % fxID
				
		elif 'thevid2' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'http://thevid.net/e/%s' % fxID
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

def player_series(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('VerFilmes', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		links = []
		hosts = []
		matriz = []

		link = openURL(url)
		soup  = BeautifulSoup(link)
		conteudo = soup("div", {"class":"itens"})
		srvsdub = conteudo[0]('a')
		totD = len(srvsdub)
		
		titsT = []
		
		for i in range(totD) :
				titS = srvsdub[i].text
				titS = titS.replace('Assistir no', '')
				titsT.append(titS)
				print titsT
	
		if not titsT : return

		index = xbmcgui.Dialog().select('Selecione uma das fontes suportadas :', titsT)	

		if index == -1 : return
		
		i = int(index)

		links  = conteudo[0]('a')
		
		if len(links) == 0 : links = conteudo[0]("a")
		
		urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]
		
		link = openURL(urlVideo)
		soup  = BeautifulSoup(link)
		conteudo = soup.findAll("iframe")
		urlVideo = conteudo[1].get('src')
		
		xbmc.log('[plugin.video.verfilmesBiz - player_series -L383] ' + str(urlVideo), xbmc.LOGNOTICE)

		mensagemprogresso.update(50, 'Resolvendo fonte para ' + name,'Por favor aguarde...')

		if 'openload2' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'https://openload.co/embed/%s' % fxID
				
		elif 'ok2' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'http://ok.ru/videoembed%s' % fxID

		elif 'vidto2' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'http://vidto.me/embed-%s-850x550.html' % fxID

		elif 'vidzi2' in urlVideo :
				fxID = urlVideo.split('-')[1]
				urlVideo = 'http://vidzi.tv/%s.html' % fxID
						
		elif 'thevid' in urlVideo :
				fxID = urlVideo.split('=')[1]
				urlVideo = 'http://thevid.net/e/%s' % fxID
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
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
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
		titO = re.findall('<h1 id="tt-site" class="hidden-xs">(.*?)</h1>', link)[0]
		titO = titO.replace('Assistir','').replace('Dublado','').replace('Legendado','').replace('Online','')
						
		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
		link = openURL(url)
		ytID = re.findall('<iframe width="100%" height="100%" src="https://www.youtube.com/embed/(.*?)" frameborder="0" allowfullscreen>.*?</iframe>', link)[0]

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

def sinopse(urlF):
		link = openURL(urlF)
		#link = unicode(link, 'utf-8', 'ignore')
		soup = BeautifulSoup(link)
		conteudo = soup("div", {"class": "perfil_sinopse"})
		#print conteudo
		plot = conteudo[0].span.text
		return plot
			
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