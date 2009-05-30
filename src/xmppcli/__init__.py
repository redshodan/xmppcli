# Copyright (C) 2008 James Newton
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
import xmppparser
from xmppparser import Interface
from .XMPPClient import XMPPClient


def run():
    import logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')
    print "Connecting..."
    jid = xmpp.JID(sys.argv[1])
    client = XMPPClient(jid, sys.argv[2])
    client.connect()
    print "connected"
    stream_info = {"hostname" : jid.getDomain(), "user" : jid.getNode(),
                   "resource" : jid.getResource(), "jid" : str(jid)}
    ui = Interface(client, stream_info, "../../xmppparser/trunk")
    client.setUI(ui)
    client.run()
    ui.setRoster(client.conn.Roster)
    ui.run()
