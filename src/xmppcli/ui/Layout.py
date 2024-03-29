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
from .TextBuffer import TextBuffer, LogBuffer
from .Tabs import Tabs
from .StatusBar import StatusBar
from .Roster import Roster
from .Input import Input
from xmppcli import log

class Layout(object):
    def __init__(self, ui):
        self.iparser = None
        self.ui = ui
        self.roster = Roster()
        ### StatusBar
        self.status = StatusBar()
        self.attr_status = urwid.AttrWrap(self.status, "status")
        ### Tabs
        self.roster_box = urwid.LineBox(self.roster)
        self.logbuff = LogBuffer("Logs", self)
        log.addStreamHandler(self.logbuff)
        self.xmlbuff = LogBuffer("XML", self)
        log.addXMLHandler(self.xmlbuff)
        self.tabs = Tabs([self.logbuff, self.xmlbuff], self.status)
        ### Input area
        self.input = Input(self)
        self.attr_input = urwid.AttrWrap(self.input, "input")
        ### Pile
        self.pile = urwid.Pile(
            [self.tabs, ("flow", self.attr_status),
             ("flow", self.attr_input)], self.attr_input)
        self.top = self.pile
        ### Overlay
        self.roster_overlay = urwid.Overlay(self.roster_box, self.pile, "right",
                                            ("relative", 50), "top",
                                            ("relative", 100))
        self.fullsizes = [self.roster_overlay]

    def setInputParser(self, parser):
        self.iparser = parser
        self.input.setInputParser(parser)

    def keypress(self, size, key):
        if self.top in self.fullsizes:
            pass_size = size
        else:
            pass_size = size[:1]
        if urwid.is_mouse_event(key):
            event, button, col, row = key
            self.top.mouse_event(pass_size, *key, focus=True)
        elif key == "window resize":
            log.debug("window resize")
            self.ui.refreshSize()
            self.ui.clear()
        elif key == "ctrl l":
            self.ui.clear()
        else:
            key = self.top.keypress(pass_size, key)
            if key:
                self.unhandled(size, key)

    def unhandled(self, size, key):
        if key == "ctrl r":
            if self.top == self.roster_overlay:
                self.top = self.pile
            else:
                self.roster.update()
                self.top = self.roster_overlay
            self._invalidate()
        elif key == "ctrl n":
            self.tabs.next()
            self._invalidate()
        elif key == "ctrl p":
            self.tabs.prev()
            self._invalidate()
        else:
            log.debug("KEY %s" % key)

    def setRoster(self, roster):
        self.roster.setRoster(roster)

    def wake(self):
        self.ui.wake()

    def __getattr__(self, name):
        return getattr(self.top, name)
