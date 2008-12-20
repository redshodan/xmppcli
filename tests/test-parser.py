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

import sys

sys.path.append("./src")

import xmppcli
from xmppcli import Interface

xmppcli.init(".")

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
