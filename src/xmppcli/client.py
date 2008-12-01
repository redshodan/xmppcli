# Copyright (C) 2008 James Newton
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import gloox, sys, time, readline
from select import select
from xmppcli import *


class XMPPClient(gloox.MessageHandler, gloox.LogHandler):

    def __init__(self):
        gloox.MessageHandler.__init__(self)
        gloox.LogHandler.__init__(self)

        self.stream_info = {}
        self.jid = gloox.JID(sys.argv[1])
        self.password = sys.argv[2]
        self.stream_info["hostname"] = self.jid.server()
        self.client = gloox.Client(self.jid, self.password)
        self.client.registerMessageHandler(self)
        self.client.logInstance().registerLogHandler(gloox.LogLevelDebug,
                                                     gloox.LogAreaAll, self)

    def run(self):
        try:
            print "Connecting..."
            if not self.client.connect(False):
                print "Failed to connect"
                return
            ret = gloox.ConnNoError
            while ret == gloox.ConnNoError:
                ret = self.client.recv(50000)
                time.sleep(0.001)
        except Exception, e:
            logEx(e)

    def handleMessage(self, stanza, session):
        try:
            print stanza.xml()
        except Exception, e:
            logEx(e)

    def handleLog(self, level, area, message):
        try:
            if area & gloox.LogAreaXmlIncoming:
                print ansiColor("RED") + "<<<< " + message + ansiColor("RESET")
            elif area & gloox.LogAreaXmlOutgoing:
                print ansiColor("CYAN") + ">>>> " + message + ansiColor("RESET")
        except Exception, e:
            logEx(e)
