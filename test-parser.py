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
