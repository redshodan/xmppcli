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
from .TextBuffer import TextBuffer
from .Tabs import Tabs
from .StatusBar import StatusBar
from xmppcli import log


class LineWalker(urwid.ListWalker):
    def __init__(self):
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
        self.lines.append(urwid.Text(line))
        self.set_focus(len(self.lines) - 1)

    def clear(self):
        self.lines = []


class Roster(urwid.ListBox):
    def __init__(self):
        self.walker = LineWalker()
        urwid.ListBox.__init__(self, self.walker)
        self.roster = None

    def setRoster(self, roster):
        self.roster = roster
        self.update()

    def update(self):
        if not self.roster:
            return
        self.walker.clear()
        for jid, entry in self.roster.iteritems():
            self.walker.append("%s:" % jid)
            for res, rentry in entry["resources"].iteritems():
                pri = "0"
                if "priority" in rentry and rentry["priority"]:
                    pri = rentry["priority"]
                val = "   %s(%s)" % (res, pri)
                if (("status" in rentry) and rentry["status"] and
                    (rentry["status"] != "Available")):
                    val = val + " status(%s)" % rentry["status"]
                if "show" in rentry and rentry["show"]:
                    val = val + " show(%s)" % rentry["show"]
                self.walker.append(val)
