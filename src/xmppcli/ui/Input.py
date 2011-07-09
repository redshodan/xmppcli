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

import urwid
from xmppcli import log

class Input(urwid.Edit):
    def __init__(self, layout):
        urwid.Edit.__init__(self)
        self.iparser = None
        self.lo = layout

    def setInputParser(self, parser):
        self.iparser = parser

    def rlShowComps(self, comps):
        log.debug("rlShowComps: " + str(comps))

    def rlRedisplay(self):
        log.debug("rlRedisplay")

    def keypress(self, size, key):
        log.debug("key: " + key)
        if not self.edit_text or not len(self.edit_text):
            self.iparser.startInput()
        ret = urwid.Edit.keypress(self, size, key)

        if key == "tab":
            key = "\t"
        
        if key == "enter":
            self.iparser.endInput()
        else:
            self.iparser.handleInput(key)
        return ret
