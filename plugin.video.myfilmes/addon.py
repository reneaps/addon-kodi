#####################################################################
#####################################################################
# -*- coding: UTF-8 -*-
#####################################################################
# Addon : plugin.video.filmes
# By AddonReneSilva - 28/06/2018
# Atualizado (1.0.0) - 28/06/2018
#####################################################################
import sys
import urllib
import xbmcgui
import xbmcplugin

addon_handle = int(sys.argv[1])

xbmcplugin.setContent(addon_handle, 'movies')

def pesquisa():
		keyb = xbmc.Keyboard('', 'Entre com URL:')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto	 = keyb.getText()
				pesquisa = texto #urllib.quote(texto)
				url		 = str(pesquisa)
		return url

url = pesquisa()
li = xbmcgui.ListItem('Meu primeiro video!', iconImage = 'DefaultVideo.png')
li.setInfo(type = "Video", infoLabels = {"title": "Arrow"})
xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

xbmcplugin.endOfDirectory (addon_handle)