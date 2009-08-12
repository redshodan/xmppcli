# Copyright (C) 2009 James Newton
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import sys, xmpp
#import xmppparser
#from xmppparser import Interface
from .XMPPClient import XMPPClient
from .ui import UI
import xmppcli.log as log

def run():
    log.setup()
    xmpp.debug.colors_enabled = False
    ui = UI()
    log.info("Connecting...")
    jid = xmpp.JID(sys.argv[1])
    client = XMPPClient(ui, jid, sys.argv[2])
    ui.setClient(client)
    # stream_info = {"hostname" : jid.getDomain(), "user" : jid.getNode(),
    #                "resource" : jid.getResource(), "jid" : str(jid)}
    # ui = Interface(client, stream_info, "../../xmppparser/trunk")
    def connectedCB():
        ui.setRoster(client.conn.Roster)
    client.run(conncb=connectedCB)
    ui.run()
