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

addon_handle = int (sys.argv [1])

def pesquisa():
		keyb = xbmc.Keyboard('', 'Entre com URL:')
		keyb.doModal()

		if (keyb.isConfirmed()):
				texto	 = keyb.getText()
				pesquisa = urllib.quote(texto)
				url		 = str(pesquisa)
		return url
				
xbmcplugin.setContent (addon_handle, 'movies')

url = pesquisa()
li = xbmcgui.ListItem('Meu primeiro video', iconImage = 'DefaultVideo.png')
xbmcplugin.addDirectoryItem (manipular = addon_handle, url = url, listitem = li)

xbmcplugin.endOfDirectory (addon_handle)