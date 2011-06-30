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

import types
import urwid
from xmppcli import log

class Tabs(urwid.Widget):
    def __init__(self, widgets, status):
        urwid.Widget.__init__(self)
        self.widgets = widgets
        self.status = status
        self.selected = 0
        self.setStatusName()

    def append(self, widget):
        self.widgets.append(widget)
        self.setStatusName()

    def prepend(self, widget):
        self.widgets.append(widget)
        self.setStatusName()

    def remove(self, widget):
        for index in range(len(self.widgets)):
            if self.widgets[index] == widget:
                del self.widgets[index]
                break
        self.setStatusName()

    def cur(self):
        return self.widgets[self.selected]

    def next(self):
        self.selected = self.selected + 1
        if self.selected >= len(self.widgets):
            self.selected = 0
        self.setStatusName()
        self._invalidate()

    def prev(self):
        self.selected = self.selected - 1
        if self.selected < 0:
            self.selected = len(self.widgets) - 1
        self.setStatusName()
        self._invalidate()

    def setStatusName(self):
        names = []
        for idx in range(len(self.widgets)):
            if idx == self.selected:
                color = 'status-hilite'
            else:
                color = 'status'
            names.append((color, '[' + self.widgets[idx].name + ']'))
            names.append(" ")
        self.status.setBuffName(names)
    
    def select(self, index):
        if type(index) is types.IntType:
            self.selected = index
        else:
            for windex in range(len(self.widgets)):
                if self.widgets[windex] is index:
                    self.selected = windex
                    break
            else:
                raise Exception("Invalid selection %s" % str(index))
        self._invalidate()

    def __getattr__(self, name):
        return getattr(self.cur(), name)
