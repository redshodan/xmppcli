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

import os, sys, select, errno, fcntl
import urwid.curses_display
import urwid
from xmppcli import log
from .Layout import Layout

class UI(object):
    palette = \
    [
        ("input", "light gray", "default"),
        ("status", "white", "dark blue"),
        ("status-hilite", "dark blue", "light gray"),

        # XMPPPY color mappings
        ("none", "default", "default"),
        ("black", "black", "default"),
        ("red", "dark red", "default"),
        ("green", "dark green", "default"),
        ("brown", "brown", "default"),
        ("blue", "dark blue", "default"),
        ("magenta", "dark magenta", "default"),
        ("cyan", "dark cyan", "default"),
        ("light_gray", "light gray", "default"),
        ("dark_gray", "dark gray", "default"),
        ("bright_red", "light red", "default"),
        ("bright_green", "light green", "default"),
        ("yellow", "yellow", "default"),
        ("bright_blue", "light blue", "default"),
        ("purple", "light magenta", "default"),
        ("bright_cyan", "light cyan", "default"),
        ("white", "white", "default"),
    ]

    xmpppy_needle = chr(27) + "["
    xmpppy_colors = \
    {
        "0" : "none",
        "30" : "black",
        "31" : "red",
        "32" : "green",
        "33" : "brown",
        "34" : "blue",
        "35" : "magenta",
        "36" : "cyan",
        "37" : "light_gray",
        "30;1" : "dark_gray",
        "31;1" : "bright_red",
        "32;1" : "bright_green",
        "33;1" : "yellow",
        "34;1" : "bright_blue",
        "35;1" : "purple",
        "36;1" : "bright_cyan",
        "37;1" : "white",
    }

    def __init__(self):
        self.client = None
        self.running = True
        self.pipe = os.pipe()
        fcntl.fcntl(self.pipe[0], fcntl.F_SETFL, os.O_NONBLOCK)
        self.fds = [[sys.stdin.fileno(), self.pipe[0]], [], []]
        self.screen = urwid.curses_display.Screen()
        self.screen.register_palette(UI.palette)
        self.layout = Layout(self)
        self.size = None

    def setClient(self, client):
        self.client = client

    def setRoster(self, roster):
        self.layout.setRoster(roster)

    def run(self):
        self.screen.run_wrapper(self._run)

    def _run(self):
        self.screen.set_mouse_tracking()
        self.refreshSize()
        while self.running:
            canvas = self.layout.render(self.size, focus=True)
            self.screen.draw_screen(self.size, canvas)
            keys = self.getInput()
            if not keys:
                continue
            for key in keys:
                self.layout.keypress(self.size, key)

    def getInput(self):
        keys = None
        while not keys:
            ret = None
            try:
                ret = select.select(*self.fds)
            except select.error, e:
                if e.args[0] != errno.EINTR:
                    raise
            if ret and self.pipe[0] in ret[0]:
                try:
                    os.read(self.pipe[0], 1)
                except OSError, e:
                    if ((e.args[0] != errno.EINTR) and
                        (e.args[0] != errno.EAGAIN)):
                        raise
                break
            keys = self.screen.get_input()
        return keys

    def stop(self):
        self.running = False

    def wake(self):
        os.write(self.pipe[1], "\0")

    def refreshSize(self):
        osize = self.size
        self.size = self.screen.get_cols_rows()
        log.debug("refreshSize: old=%s new=%s" % (osize, self.size))

    def clear(self):
        self.screen.clear()

    @staticmethod
    def convertXMPPYColor(buff):
        idx = 0
        oidx = 0
        length = len(buff)
        out = []
        cur = None
        while idx > -1 and idx < length:
            oidx = idx
            idx = buff.find(UI.xmpppy_needle, idx)
            found = False
            if idx > -1:
                try:
                    if cur:
                        cur.append(buff[oidx:idx])
                        out.append(tuple(cur))
                        cur = None
                    else:
                        out.append(buff[oidx:idx])
                    midx = idx + 2
                    cidx = buff.find("m", midx)
                    color = buff[midx:cidx]
                    pcolor = UI.xmpppy_colors[color]
                    cur = [pcolor]
                    idx = cidx + 1
                    found = True
                except:
                    pass
            if not found:
                if cur:
                    cur.append(buff[oidx:idx])
                    out.append(tuple(cur))
                    cur = None
                else:
                    out.append(buff[oidx:idx])
        return out
