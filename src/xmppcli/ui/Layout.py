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
from .StatusBar import StatusBar
from xmppcli import log

class Layout(urwid.Pile):
    palette = \
       [("input", "light gray", "default"),
        ("status", "white", "dark blue")]

    def __init__(self, ui, screen):
        self.ui = ui
        self.screen = screen
        self.screen.register_palette(Layout.palette)
        self.logbuff = TextBuffer()
        self.buff2 = TextBuffer()
        self.buff2.append("This is buff2, biaaaatch!")
        self.tabs = Tabs([self.logbuff])
        self.tabs.append(self.buff2)
        self.status = StatusBar()
        self.attr_status = urwid.AttrWrap(self.status, "status")
        self.input = urwid.Edit()
        self.attr_input = urwid.AttrWrap(self.input, "input")
        urwid.Pile.__init__(self,
                            [self.tabs, ("flow", self.attr_status),
                             ("flow", self.attr_input)], self.attr_input)

    def keypress(self, size, key):
        if urwid.is_mouse_event(key):
            event, button, col, row = key
            self.get_focus().mouse_event(size, *key, focus=True)
        elif key == "window resize":
            self.logbuff.append("window resize")
            self.ui.refreshSize()
            self.screen._clear()
        else:
            key = self.get_focus().keypress(size[:1], key)
            if key:
                self.logbuff.append("KEY %s" % key)
                self.unhandled(size, key)

    def unhandled(self, size, key):
        self.screen.clear()
        self.tabs.next()
        self._invalidate()

    def log(self, buff):
        self.logbuff.append(buff.rstrip("\n"))
