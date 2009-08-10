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

import os, sys, select, errno, fcntl
import urwid.curses_display
import urwid
from xmppcli import log
from .Layout import Layout

class UI(object):
    def __init__(self):
        self.client = None
        self.running = True
        self.pipe = os.pipe()
        fcntl.fcntl(self.pipe[0], fcntl.F_SETFL, os.O_NONBLOCK)
        self.fds = [[sys.stdin.fileno(), self.pipe[0]], [], []]
        self.screen = urwid.curses_display.Screen()
        self.layout = Layout(self, self.screen)
        self.size = None

    def setClient(self, client):
        self.client = client

    def setRoster(self, roster):
        self.roster = roster

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
        self.log("refreshSize: old=%s new=%s" % (osize, self.size))

    def log(self, buff):
        self.layout.log(buff)
        self.wake()
