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
from optparse import OptionParser
#import xmppparser
#from xmppparser import Interface
from .XMPPClient import XMPPClient
from .ui import UI
import xmppcli.log as log


def parseArgs():
    usage = "usage: %prog [options] user@host[/resource] password"
    parser = OptionParser(usage=usage)

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        sys.exit(-1)
    
    return options, args


def run():
    options, args = parseArgs()
    log.setup()
    xmpp.debug.colors_enabled = True
    ui = UI()
    jid = xmpp.JID(args[0])
    client = XMPPClient(ui, jid, args[1])
    ui.setClient(client)
    # stream_info = {"hostname" : jid.getDomain(), "user" : jid.getNode(),
    #                "resource" : jid.getResource(), "jid" : str(jid)}
    # ui = Interface(client, stream_info, "../../xmppparser/trunk")
    def connectedCB():
        ui.setRoster(client.conn.Roster)
    client.run(conncb=connectedCB)
    ui.run()
