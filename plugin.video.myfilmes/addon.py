#####################################################################
# -*- coding: UTF-8 -*-
#####################################################################
# Addon : plugin.video.filmes
# By AddonReneSilva - 28/06/2018
# Atualizado (1.0.0) - 28/06/2018
#####################################################################
import sys
import xbmcgui
import xbmcplugin
import urllib

addon_handle = int(sys.argv[1])

def pesquisa():
		keyb = xbmc.Keyboard('', 'Entre com URL:')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto	 = keyb.getText()
				pesquisa = texto #urllib.quote_plus(texto)
				url		 = str(pesquisa)
		return url
				
xbmcplugin.setContent (addon_handle, 'movies')

url = pesquisa()
li = xbmcgui.ListItem('Meu primeiro video', iconImage = 'DefaultVideo.png')
#xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=li)
xbmcplugin.addDirectoryItem (handle = addon_handle, url = url, listitem = li)

xbmcplugin.endOfDirectory (addon_handle)