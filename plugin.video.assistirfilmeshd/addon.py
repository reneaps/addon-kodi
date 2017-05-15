#####################################################################
# -*- coding: utf-8 -*-
#####################################################################
# Addon : AssistirFilmesHD
# By AddonReneSilva - 02/11/2016
# Atualizado (1.0.0) - 02/11/2016
# Atualizado (1.0.1) - 06/12/2016
# Atualizado (1.0.2) - 21/12/2016
# Atualizado (1.0.3) - 06/02/2017
#####################################################################

import urllib, urllib2, re, xbmcplugin, xbmcgui, xbmc, xbmcaddon, os, time, base64
import urlresolver

from resources.lib.BeautifulSoup import BeautifulSoup
from resources.lib               import jsunpack

addon_id  = 'plugin.video.assistirfilmeshd'
selfAddon = xbmcaddon.Addon(id=addon_id)

addonfolder = selfAddon.getAddonInfo('path')
artfolder   = addonfolder + '/resources/img/'
fanart      = addonfolder + '/fanart.png'
base        = base64.b64decode('aHR0cDovL3d3dy5hc3Npc3RpcmZpbG1lc2hkLm9yZw==')

############################################################################################################

def menuPrincipal():
		addDir('Categorias'                , base + '/categoria/'			,   10, artfolder + 'categorias.png')
		addDir('Lançamentos'               , base + '/categoria/lancamento-de-2016/' 	,	20, artfolder + 'lancamentos.png')
		addDir('Filmes Dublados'           , base + '/search.php?s=dublado&btn-busca=' 	,	20, artfolder + 'pesquisa.png')
		addDir('Series'		               , base + '/categoria/series/'	,   25, artfolder + 'legendados.png')
		addDir('Pesquisa Series'           , '--'                           ,   30, artfolder + 'pesquisa.png')
		addDir('Pesquisa Filmes'           , '--'                           ,   35, artfolder + 'pesquisa.png')
		addDir('Configurações'             , base                           ,  999, artfolder + 'config.png', 1, False)
		addDir('Configurações ExtendedInfo', base                           , 1000, artfolder + 'config.png', 1, False)
			
		setViewMenu()		
		
def getCategorias(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')	
		soup = BeautifulSoup(link)
		conteudo   = soup("div", {"id": "wrap"})
		categorias = conteudo[0]("li", {"class": "item_normal"})
		totC = len(categorias)
		for categoria in categorias:
				titC = categoria.h5.text.encode('utf-8')
				titC = titC.replace('&ccedil;','c').replace('&atilde;','a').replace('&eacute;','e')
				titC = titC.replace('&ecirc;','i').replace('&aacute;','a').replace('&eacute;','e')
				if not 'Lançamento' in titC :
								urlC = categoria.a["href"]
								imgC = artfolder + limpa(titC) + '.png'
								addDir(titC,urlC,20,imgC)
			
		setViewMenu()
		
def getFilmes(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup     = BeautifulSoup(link)
		conteudo = soup("div", {"id": "wrap"})
		filmes   = conteudo[0]("div", {"class": "box-filme"})
		totF = len(filmes)
		for filme in filmes:
				titF = filme.img["alt"].encode('utf-8','replace')
				titF = titF.replace('Assistir ','').replace('Filme ','')
				urlF = filme.a["href"].encode('utf-8', 'ignore')
				imgF = filme.img["src"].encode('utf-8', 'ignore')
				imgF = imgF.split('?src=')[1]
				imgF = imgF.split('&')[0]
				addDirF(titF, urlF, 100, imgF, False, totF)
		try : 
				proxima = re.findall('<a href="(.*?)">Pr.*?xima</a>', link)[0]
				addDir('Próxima Página >>', proxima, 20, artfolder + 'proxima.png')
		except : 
				pass
				
		setViewFilmes()
					
def getSeries(url):
		link = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')
		soup     = BeautifulSoup(link)
		conteudo = soup("div", {"id": "wrap"})
		filmes   = conteudo[0]("div", {"class": "box-filme"})
		totF = len(filmes)
		for filme in filmes:
				titF = filme.img["alt"].encode('utf-8','replace')
				titF = titF.replace('Assistir ','').replace('Filme ','')
				titF = titF.replace('- Todas as Temporadas - Dublado / Legendado', '')
				titF = titF.replace('- Minisérie', '')
				titF = titF.replace('- Minissérie', '')
				urlF = filme.a["href"].encode('utf-8', 'ignore')
				imgF = filme.img["src"].encode('utf-8', 'ignore')
				imgF = imgF.split('?src=')[1]
				imgF = imgF.split('&')[0]
				addDirF(titF, urlF, 26, imgF)
		try : 
				proxima = re.findall('<a href="(.*?)">Pr.*?xima</a>', link)[0]
				addDir('Próxima Página >>', proxima, 25, artfolder + 'proxima.png')
		except : 
				pass
		setViewFilmes()
		
def getTemporadas(url):	
		link  = openURL(url)
		link = unicode(link, 'utf-8', 'ignore')						
		soup = BeautifulSoup(link)
		conteudo = soup.find("ul", {"class": "itens"}) 
		temporadas = conteudo("li")
		totF = len(temporadas)
		img = soup.find("div", {"id": "postimg"})
		imgF = img.img['src']
		imgF = imgF.split('?src=')[1]
		imgF = imgF.split('&')[0]
		urlF = url
		i = 1
		while i <= totF:
			titF = str(i) + "ª Temporada"
			try:
				addDirF(titF, urlF, 27, imgF)
			except:
				pass
			i = i + 1
		
def getEpisodios(name, url):
		n = name.replace('ª Temporada', '')	
		n = int(n)
		#n = (n-1)
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
							titF = titF.replace('Assistir ','').replace('Filme ','') + " - " +audio #" Dublado"
							titF = str(n) + "T " + titF
							urlF = filme.get("href").encode('utf-8', 'ignore')
							urlF = base + "/" + urlF
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
							titF = titF.replace('Assistir ','').replace('Filme ','') + " - " +audio #" Legendado"
							titF = str(n) + "T " + titF
							urlF = filme.get("href").encode('utf-8', 'ignore')
							urlF = base + "/" + urlF
							temp = (titF, urlF)
							episodios.append(temp)
		except:
			pass
		
		audio = []
		imgF = []
		img = soup.find("div", {"id": "postimg"})
		imgF = img.img['src']
		imgF = imgF.split('?src=')[1]
		imgF = imgF.split('&')[0]
		
		total = len(episodios)

		for titF, urlF in episodios:
				addDirF(titF, urlF, 110, imgF, False, totF)
				
def pesquisa():
		keyb = xbmc.Keyboard('', 'Pesquisar Filmes')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto    = keyb.getText()
				pesquisa = urllib.quote(texto)
				url      = base + '/search.php?s=%s&btn-busca=' % str(pesquisa)

				link  = openURL(url)
				link = unicode(link, 'utf-8', 'ignore')		
		
				soup     = BeautifulSoup(link)
				conteudo = soup("div", {"id": "wrap"})
				filmes   = conteudo[0]("div", {"class": "box-filme"})
				totF = len(filmes)
				hosts = []
				for filme in filmes:
					titF = filme.img["alt"].encode('utf-8','replace')
					titF = titF.replace('Assistir ','').replace('Filme ','')
					urlF = filme.a["href"].encode('utf-8', 'ignore')
					imgF = filme.img["src"].encode('utf-8', 'ignore')
					imgF = imgF.split('?src=')[1]
					imgF = imgF.split('&')[0]
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
			addDirF(titulo, url2, 100, img, False, total)
			
def player(name,url,iconimage):
		OK = True
		mensagemprogresso = xbmcgui.DialogProgress()
		mensagemprogresso.create('AssistirFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		idsT = []
		matriz = []

		link = openURL(url)
		soup  = BeautifulSoup(link)
			
		conteudo = soup("div", {"id": "assistindo"})
		opcoes  = conteudo[0]("div", {"class": "opcoes"})
		srvsdub = opcoes[0]('a')
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

		links  = opcoes[0]('a')
		
		if len(links) == 0 : links = conteudo[0]("a")
		
		urlVideo = re.findall(r'href=[\'"]?([^\'" >]+)', str(links))[i]

		link = openURL(urlVideo)
		soup  = BeautifulSoup(link)
		conteudo = soup("iframe")
		urlVideo = str(conteudo[1]['src'])
		
		xbmc.log('[plugin.video.assistirfilmeshd] L277 - ' + str(urlVideo), xbmc.LOGNOTICE)
		
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
				okID = urlVideo.split('/')[4]
				urlVideo = 'https://openload.co/embed/%s' % okID
				
		elif 'thevid.net' in urlVideo :
				okID = urlVideo.split('e/')[1]
				urlVideo = 'http://thevid.net/v/%s' % okID
				xbmc.log('[plugin.video.assistirfilmeshd] L304 - ' + str(urlVideo), xbmc.LOGNOTICE)
				'''
				linkTV  = openURL(urlVideo)		
				sPattern = "(\s*eval\s*\(\s*function(?:.|\s)+?)<\/script>"
				aMatches = re.compile(sPattern).findall(linkTV)
				sUnpacked = jsunpack.unpack(aMatches[1])
				url2Play = re.findall('var vurl_\d+="(.*?)"', sUnpacked)
				url2Play = str(url2Play[0])				
	
				OK = False
				'''
						
		if OK : url2Play = urlresolver.resolve(urlVideo)
		
		xbmc.log('[plugin.video.assistirfilmeshd] L318 - ' + str(url2Play), xbmc.LOGNOTICE)

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
		mensagemprogresso.create('AssistirFilmesHD', 'Obtendo Fontes para ' + name, 'Por favor aguarde...')
		mensagemprogresso.update(0)
		
		titsT = []
		idsT = []
		links = []
		hosts = []
		matriz = []

		link = openURL(url)
		soup  = BeautifulSoup(link)

		conteudo = soup("div", {"class": "itens"})
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
		conteudo = soup("iframe")
		urlVideo = str(conteudo[1]['src'])

		xbmc.log('[plugin.video.assistirfilmeshd - player_series -L397] ' + str(urlVideo), xbmc.LOGNOTICE)
		
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
		req.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C)')
		#req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64; Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
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
		titO = re.findall('<h1 class="titulopostagem">(.*?)</h1>', link)[0]
		titO = titO.replace('Dublado','').replace('Legendado','')
						
		xbmc.executebuiltin('XBMC.RunScript(script.extendedinfo,info=extendedinfo, name=%s)' % titO)

def playTrailer(name, url,iconimage):
		link = openURL(url)
		ytID = re.findall('<a href="http://www.youtube.com/embed/(.*?)autoplay=1" class="trailer">TRAILER</a>', link)[0]
		ytID = ytID.replace('?','')

		if not ytID : 
			addon = xbmcaddon.Addon()
			addonname = addon.getAddonInfo('name')
			line1 = str("Trailer não disponível!")
			xbmcgui.Dialog().ok(addonname, line1)	
			return
			
		xbmcPlayer = xbmc.Player()
		xbmcPlayer.play('plugin://plugin.video.youtube/play/?video_id='+ytID)
		
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