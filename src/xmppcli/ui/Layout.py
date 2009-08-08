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

import urwid
from .TextBuffer import TextBuffer
from .Tabs import Tabs
from xmppcli import log

class Layout(urwid.Widget):
    def __init__(self, screen):
        self.screen = screen
        self.logbuff = TextBuffer()
        self.buff2 = TextBuffer()
        self.buff2.append("This is buff2, biaaaatch!")
        self.tabs = Tabs([self.logbuff])
        self.tabs.append(self.buff2)
        self.widget = self.tabs

    def keypress(self, size, key):
        if urwid.is_mouse_event(key):
            event, button, col, row = key
            self.widget.mouse_event(size, *key, focus=True)
        elif key == "window resize":
            size = self.screen.get_cols_rows()
            self.log("resize: %s" % str(size))
        else:
            key = self.widget.keypress(size, key)
            if key:
                self.unhandled(size, key)

    def unhandled(self, size, key):
        self.tabs.next()

    def log(self, buff):
        self.logbuff.append(buff.rstrip("\n"))

    def __getattr__(self, name):
        return getattr(self.widget, name)
