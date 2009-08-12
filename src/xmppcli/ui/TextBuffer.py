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

class LineWalker(urwid.ListWalker):
    def __init__(self, limit = 1000):
        self.limit = limit
        self.lines = []
        self.focus = 0

    def get_focus(self):
        return self.get(self.focus)

    def set_focus(self, focus):
        self.focus = focus
        self._modified()

    def get_next(self, at):
        return self.get(at + 1)

    def get_prev(self, at):
        return self.get(at - 1)

    def get(self, at):
        if ((at < 0) or (len(self.lines) <= at)):
            return None, None
        else:
            return self.lines[at], at

    def append(self, line):
        if len(self.lines) > self.limit:
            del self.lines[:1]
        self.lines.append(urwid.Text(line))
        self.set_focus(len(self.lines) - 1)

class TextBuffer(urwid.ListBox):
    def __init__(self, name):
        self.name = name
        self.walker = LineWalker()
        urwid.ListBox.__init__(self, self.walker)

    def append(self, buff):
        self.walker.append(buff)

    def rows(self, (maxcol,), focus=False):
        focus_widget, focus_pos = self.body.get_focus()
        return focus_widget.rows((maxcol,), focus=focus)

### File object interface for logging
class LogBuffer(TextBuffer):
    def __init__(self, name, layout):
        TextBuffer.__init__(self, name)
        self.lo = layout

    def write(self, buff):
        self.append(buff.rstrip("\r\n"))
        self.lo.wake()

    def flush(self):
        pass
