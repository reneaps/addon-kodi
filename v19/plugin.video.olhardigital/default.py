# -*- coding: utf-8 -*-
#------------------------------------------------------------
# http://www.youtube.com/user/moshipery
#------------------------------------------------------------
# Licença: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# Baseado no código do addon youtube
#------------------------------------------------------------

import os
import sys
import plugintools
import xbmc,xbmcaddon
from addon.common.addon import Addon

addonID = 'plugin.video.olhardigital'
addon = Addon(addonID, sys.argv)
local = xbmcaddon.Addon(id=addonID)
icon = local.getAddonInfo('icon')

YOUTUBE_CHANNEL_ID = "UCGV72aVJuWP0QPNGH4YgIww"

# Ponto de Entrada
def run():
    plugintools.log("olhardigital.run")
    
    # Pega Parâmetros
    params = plugintools.get_params()
    
    if params.get("action") is None:
        main_list(params)
    else:
        action = params.get("action")
        exec action+"(params)"
    
    plugintools.close_item_list()

# Menu Principal
def main_list(params):
	plugintools.log("olhardigital.main_list "+repr(params))

	plugintools.add_item(
		title = "Canal Olhar Digital",
		url = "plugin://plugin.video.youtube/channel/"+YOUTUBE_CHANNEL_ID+"/",
		thumbnail = icon,
		folder = True )

run()