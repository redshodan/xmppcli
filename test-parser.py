import sys

sys.path.append("./src")

from xmppcli import Interface

class Handler:
    def handleUIPresence(self, argmap):
        print "handlePresence:", argmap

    def handleUIMessage(self, argmap):
        print "handleMessage:", argmap

    def handleUIIQ(self, argmap):
        print "handleIQ:", argmap

    def handleUIXML(self, xml):
        print "handleXML:", xml

if len(sys.argv) > 1:
    debug = True
else:
    debug = False
ui = Interface(Handler(), {"hostname" : "foo.com"}, debug)
ui.run()
