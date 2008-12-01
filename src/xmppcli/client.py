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

import gloox, sys, time, thread
from select import select
from xmppcli import glooxutils
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
        self.out_buffer = []
        self.lock = thread.allocate_lock()

    def setUI(self, ui):
        self.ui = ui

    def run(self):
        try:
            print "Connecting..."
            if not self.client.connect(False):
                print "Failed to connect"
                return
            ret = gloox.ConnNoError
            while ret == gloox.ConnNoError:
                ret = self.client.recv(50000)
                self.sendElems()
                time.sleep(0.001)
        except Exception, e:
            logEx(e)

    def sendElems(self):
        self.lock.acquire()
        for xml in self.out_buffer:
            elems = glooxutils.parse(xml)
            if len(elems):
                for elem in elems:
                    self.client.send(elem.clone())
            else:
                print "Invalid XML"
        del self.out_buffer[:]
        self.lock.release()

    def queueXML(self, xml):
        self.lock.acquire()
        self.out_buffer.append(xml)
        self.lock.release()

    ### gloox handlers
    def handleMessage(self, stanza, session):
        try:
            print stanza.xml()
        except Exception, e:
            logEx(e)

    def handleLog(self, level, area, message):
        try:
            if area & gloox.LogAreaXmlIncoming:
                self.ui.handleIncomingXML(message)
            elif area & gloox.LogAreaXmlOutgoing:
                self.ui.handleOutgoingXML(message)
        except Exception,e :
            logEx(e)

    ### Interface handlers
    def handleUIPresence(self, argmap):
        print "handlePresence:", argmap

    def handleUIMessage(self, argmap):
        print "handleMessage:", argmap

    def handleUIIQ(self, argmap):
        print "handleIQ:", argmap

    def handleUIXML(self, xml):
        print "handleXML:", xml
        #self.client.send(gloox.Tag("presence").clone())
        self.queueXML(xml)
