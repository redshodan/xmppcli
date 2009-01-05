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

import cmd, re, readline
from xmppparser import *


__all__ = ["Interface", "StanzaHandler"]


_ansi_colors = \
{
    "BLACK" : "\033[30m",
    "RED" : "\033[31m",
    "GREEN" : "\033[32m",
    "YELLOW" : "\033[33m",
    "BLUE" : "\033[34m",
    "MAGENTA" : "\033[35m",
    "CYAN" : "\033[36m",
    "WHITE" : "\033[37m",

    "BLACKBG" : "\033[40m",
    "REDBG" : "\033[41m",
    "GREENBG" : "\033[42m",
    "YELLOWBG" : "\033[43m",
    "BLUEBG" : "\033[44m",
    "MAGENTABG" : "\033[45m",
    "CYANBG" : "\033[46m",
    "WHITEBG" : "\033[47m",

    "RESET" : "\033[0;0m",
    "BOLD" : "\033[1m",
    "REVERSE" : "\033[2m"
}

def ansiColor(name):
    if name in _ansi_colors:
        return _ansi_colors[name]
    else:
        return ""


class Interface(cmd.Cmd):

    _white_space = re.compile("[ \\t\\n\\r]*")
    _message_args = ["to", "type", "subject", "body", "thread"]
    _presence_args = ["to", "type", "priority", "show", "status"]
    _iq_args = ["to", "type", "id", "xmlns", "child"]

    def __init__(self, handler, stream_info, debug=False):
        import atexit, sys, termios
        self.__old_termios = termios.tcgetattr(sys.__stdin__.fileno())
        atexit.register(self.cleanup)

        cmd.Cmd.__init__(self)
        self.debug = debug
        self.prompt = ">> "
        self.user_rawinput = True
        self.handler = handler
        self.stream_info = stream_info
        self.rl_prompt = False
        readline.set_startup_hook(self.rlStartup)
        delims = readline.get_completer_delims()
        delims = delims.replace(":", "")
        delims = delims.replace("/", "")
        delims = delims.replace("'", "")
        delims = delims.replace('"', "")
        delims = delims.replace('-', "")
        delims = delims.replace('#', "")
        readline.set_completer_delims(delims)

    def cleanup(self):
        import termios, sys
        termios.tcsetattr(sys.__stdin__.fileno(), termios.TCSANOW,
                          self.__old_termios)

    def makeTo(self, to):
        if "@" not in to:
            return to + "@" + self.stream_info["hostname"]
        else:
            return to

    def collate_args(self, arg, arg_names, help_func):
        args = self._white_space.split(arg)
        if not len(args):
            help_func()
            return None, None
        argmap = {}
        ordered = []
        for arg in args:
            words = arg.split("=")
            if len(words) > 1:
                val = words[1].lstrip("'").rstrip("'").lstrip('"').rstrip('"')
                argmap[words[0]] = val
            else:
                ordered.append(arg)
        for index in range(len(arg_names)):
            if index >= len(ordered):
                break
            key = arg_names[index]
            if key in argmap:
                print
                print key, "already in keyword arguments"
                return
            argmap[key] = ordered[index]
        return argmap

    def arg_complete(self, text, line, begidx, endix):
        try:
            args = self._white_space.split(line)
            parser = DumbParser(self.debug)
            parser.in_attr_name = 1
            parser.cur_elem = Elem(args[0:1][0], parent = parser.root)
            parser.parse(" ".join(args[1:]))
            return parser.complete(text)
        except Exception, e:
            logEx(e)

    def completedefault(self, text, line, begidx, endix):
        try:
            if not line.startswith("<"):
                return []
            parser = DumbParser(self.debug)
            parser.parse(line)
            return parser.complete(text)
        except Exception, e:
            logEx(e)
        return []

    def default(self, line):
        if line == "EOF":
            print
            return True
        self.handler.handleUIXML(line)

    def emptyline(self):
        pass

    def run(self):
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print
        except Exception, e:
            logEx(e)

    def rlStartup(self):
        self.rl_prompt = True

    def handleIncomingXML(self, xml):
        if self.rl_prompt:
            self.rl_prompt = False
            print
        print ansiColor("RED") + "<<<< " + xml + ansiColor("RESET")

    def handleOutgoingXML(self, xml):
        if self.rl_prompt:
            self.rl_prompt = False
            print
        print ansiColor("CYAN") + ">>>> " + xml + ansiColor("RESET")

    ###
    ### Command functions
    ###

    def help_help(self):
        self.do_help()

    def help_presence(self):
        print "Usage: presence [to] [type] [priority] [show] [status]"

    def do_presence(self, arg):
        argmap = self.collate_args(arg, self._presence_args,
                                   self.help_presence)
        if argmap:
            self.handler.handleUIPresence(argmap)

    def complete_presence(self, text, line, begidx, endix):
        return self.arg_complete(text, line, begidx, endix)
