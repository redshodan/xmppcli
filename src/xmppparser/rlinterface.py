# Copyright (C) 2011 James Newton
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

import os, sys, termios, types



class RLInterface(object):
    LEFT_ARROW = "\033[[D"
    RIGHT_ARROW = "\033[[C"
    UP_ARROW = "\033[[A"
    DOWN_ARROW = "\033[[B"
    DEL = "\177"
    
    def __init__(self, show_comps_cb=None, redisplay_cb=None):
        self.stdin = sys.stdin.fileno()
        if not show_comps_cb:
            self.show_comps_cb = self._showComps
        else:
            self.show_comps_cb = show_comps_cb
        if not redisplay_cb:
            self.redisplay_cb = self._redisplay
        else:
            self.redisplay_cb = redisplay_cb
        self.completer = None
        self._line_buffer = []
        self._line_txt = None
        self.delims = "`~!@#$%^&*()-=+[{]}\\|;:'\",<>/?"
        self.begidx = 0
        self.endidx = 0
        self.prompt = ""
        self.startup_hook = None

    @property
    def line_txt(self):
        if not self._line_txt:
            self._line_txt = "".join(self.line_buffer)
        return self._line_txt
    @line_txt.setter
    def line_txt(self, txt):
        self._line_txt = txt

    @property
    def line_buffer(self):
        return self._line_buffer
    @line_buffer.setter
    def line_buffer(self, buff):
        self._line_buffer = buff
        self.line_txt = None
        
    def get_completer(self):
        return self.completer

    def set_completer(self, completer):
        self.completer = completer
        return self.completer

    def parse_and_bind(self, bindstr):
        return None

    def readline(self, prompt):
        try:
            self.startInput()
            self.prompt = prompt
            os.write(sys.stdout.fileno(), prompt)
            self.line_buffer = []
            while True:
                c = os.read(self.stdin, 1)
                if len(c) == 0:
                    break
                elif c == "\n":
                    os.write(sys.stdout.fileno(), c)
                    break
                elif c == self.DEL:
                    self._doDel()
                else:
                    os.write(sys.stdout.fileno(), c)
                self.handleInput(c)
            return self.line_txt
        except Exception, e:
            print
            import traceback
            traceback.print_exc()

    def startInput(self):
        if self.startup_hook:
            self.startup_hook()

    def handleInput(self, string):
        for c in string:
            if c == '\t':
                self._doComplete()
            else:
                self.line_buffer.append(c)
                self.line_txt = None

    def endInput(self):
        txt = self.line_txt
        self.line_buffer = []
        return txt

    def _doComplete(self):
        length = len(self.line_txt)
        for idx in range(self.begidx, length):
            if self.line_txt[idx] not in self.delims:
                self.begidx = idx
                break
        else:
            self.begidx = length
        for idx in range(self.begidx, length):
            if self.line_txt[idx] in self.delims:
                self.endidx = idx
                break
        else:
            self.endidx = length
        count = 0
        comps = []
        ret = True
        while ret:
            ret = self.completer(self.line_txt[self.begidx:self.endidx], count)
            count = count + 1
            if ret:
                comps.append(ret)
        # Choice selected, apply it.
        if len(comps) == 1:
            self.line_buffer[self.begidx:self.endidx] = comps[0]
            self.begidx = self.begidx + len(comps[0])
            self.endidx = self.begidx
            self.line_txt = None
        else:
            self.show_comps_cb(comps)
        self.redisplay()

    def _doDel(self):
        print "_doDel"
        pass

    def _showComps(self, comps):
        os.write(sys.stdout.fileno(), "\n" + str(comps) + "\n")
        
    def redisplay(self):
        self.redisplay_cb()

    def _redisplay(self):
        os.write(sys.stdout.fileno(), "\n" + self.prompt + self.line_txt)
    
    def set_stdin(self, stdin):
        if isinstance(stdin, types.FileType):
            self.stdin = stdin.fileno()
        else:
            self.stdin = stdin

        self.tty = os.open(os.ttyname(self.stdin), os.O_RDWR)
        self.orig_tty = termios.tcgetattr(self.tty)
        new = termios.tcgetattr(self.tty)
        new[3] = new[3] & ~(termios.ICANON|termios.ECHO|
                            termios.ECHOE|termios.ECHOK|
                            termios.IEXTEN|termios.ECHONL)
        termios.tcsetattr(self.tty, termios.TCSANOW, new)

    def get_line_buffer(self):
        return self.line_txt

    def get_begidx(self):
        return self.begidx
     
    def get_endidx(self):
        return self.endidx

    def insert_text(self, txt):
        # print "insert_text", txt
        for c in txt:
            self.line_buffer.append(c)
        self.line_txt = None
        return None

    def set_startup_hook(self, hook):
        self.startup_hook = hook
        return None

    def get_completer_delims(self):
        return self.delims

    def set_completer_delims(self, delims):
        self.delims = delims
        return self.delims


rli = RLInterface()

import readline
rlm = readline
rlm.readline = raw_input
def set_stdin(stdin):
    pass
rlm.set_stdin = set_stdin


readline = rli
# readline = rlm
# print "readline:", readline
