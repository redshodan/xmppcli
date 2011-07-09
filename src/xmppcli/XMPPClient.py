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

import xmpp, types
from xmppcli import log

class XMPPClient(object):
    def __init__(self, ui, jid, password):
        self.ui = ui
        if isinstance(jid, types.StringTypes):
            self.jid = xmpp.JID(jid)
        else:
            self.jid = jid
        self.password = password
        self.conn = None
        self.running = True

    def connect(self):
        self.conn = xmpp.Client(self.jid.getDomain(), log_file=log.xmpppy_proxy,
                                debug=["always", "nodebuilder", "dispatcher"])
        resp = self.conn.connect()
        if not resp:
            raise Exception("Failed to connect")
        log.info("Connected with: %s", resp)
        resp = self.conn.auth(self.jid.getNode(), self.password,
                              self.jid.getResource())
        if not resp:
            raise Exception("Failed to authenticate")
        log.info("Authed with: %s", resp)
        self.conn.RegisterHandler("iq", self.onIq)
        self.conn.RegisterHandler("presence", self.onPresence)
        self.conn.RegisterHandler("message", self.onMessage)
        self.conn.sendInitPresence()

    def run(self, conncb=None):
        import thread
        def runner(self):
            try:
                log.info("XMPPClient: Connecting...")
                self.connect()
                log.info("XMPPClient: connected")
                if conncb:
                    conncb()
                while self.running:
                    self.conn.Process(1)
            except Exception, e:
                log.exception(
                    "******************EXCEPTION**********************")
                log.exception(e)
        thread.start_new_thread(runner, (self,))

    def stop(self):
        self.running = False
        self.ui.stop()

    def send(self, stanza):
        self.conn.send(stanza)

    def onIq(self, conn, iq):
        log.xmlIN(str(iq))

    def onPresence(self, conn, pres):
        log.xmlIN(str(pres))

    def onMessage(self, conn, msg):
        log.xmlIN(str(msg))

    ##
    ## UI handlers
    ##
    def handleXML(self, xml):
        log.debug("handleXML: " + xml)
        self.send(xml)

    def handleCmd(self, name, args):
        handler = getattr(self, "cmd_" + name)
        if handler:
            return handler(args)

    def cmd_available(self, args):
        extra = ""
        if "to" in args and args["to"]:
            extra = " to='%s'" % args["to"]
        self.send("<presence%s/>" % extra)

    def cmd_away(self, args):
        extra = ""
        if "to" in args and args["to"]:
            extra = " to='%s'" % args["to"]
        self.send("<presence%s><show>away</show></presence>" % extra)

    def cmd_xa(self, args):
        extra = ""
        if "to" in args and args["to"]:
            extra = " to='%s'" % args["to"]
        self.send("<presence%s><show>xa</show></presence>" % extra)

    def cmd_dnd(self, args):
        extra = ""
        if "to" in args and args["to"]:
            extra = " to='%s'" % args["to"]
        self.send("<presence%s><show>dnd</show></presence>" % extra)

    def cmd_unavailable(self, args):
        extra = ""
        if "to" in args and args["to"]:
            extra = " to='%s'" % args["to"]
        self.send("<presence type='unavailable'%s/>" % extra)

    def cmd_subscribe(self, args):
        if (("to" not in args) or (not len(args["to"]))):
            print "Must supply a to"
            return
        print "Subscribing to", args["to"]
        self.send("<presence to='%s' type='subscribe'/>" % args["to"])


# def connect(*args, **kwargs):
#     import thread
#     client = XMPPClient(*args, **kwargs)
#     def runner(client):
#         try:
#             while self.running:
#                 self.conn.Process(1)
#         except Exception, e:
#             print "******************EXCEPTION**********************"
#             print e
#     thread.start_new_thread(runner, (self,))
