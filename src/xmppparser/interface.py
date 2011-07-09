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

import os, re
from python import cmd
from xmppparser import *
import rlinterface

cmd.readline = rlinterface.readline


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

    def __init__(self, handler, stream_info, home, debug=False):
        import atexit, sys, termios
        self.__old_termios = termios.tcgetattr(sys.__stdin__.fileno())
        atexit.register(self.cleanup)

        cmd.Cmd.__init__(self)
        self.home = home
        self.xsdparser = load(os.path.join(self.home, "xsd"))
        self.cmdparser = load(os.path.join(self.home, "cmd"))
        self.debug = debug
        self.prompt = ">> "
        self.user_rawinput = True
        self.handler = handler
        self.stream_info = stream_info
        self.rl_prompt = False
        cmd.readline.set_startup_hook(self.rlStartup)
        delims = cmd.readline.get_completer_delims()
        delims = delims.replace(":", "")
        delims = delims.replace("/", "")
        delims = delims.replace("'", "")
        delims = delims.replace('"', "")
        delims = delims.replace('-', "")
        delims = delims.replace('#', "")
        cmd.readline.set_completer_delims(delims)
        self.roster = {}

        self.cmd_args = {}
        for name, stanza in self.cmdparser.stanzas.iteritems():
            self.cmd_args[stanza.name] = stanza.attrs
            self.makeCmd(stanza)

    def cleanup(self):
        import termios, sys
        termios.tcsetattr(sys.__stdin__.fileno(), termios.TCSANOW,
                          self.__old_termios)

    def setRoster(self, roster):
        self.roster = roster

    def makeCmd(self, stanza):
        if not hasattr(self, "complete_" + stanza.name):
            setattr(self, "complete_" + stanza.name, self.arg_complete)
            setattr(Interface, "complete_" + stanza.name, self.arg_complete)
        if not hasattr(self, "do_" + stanza.name):
            setattr(self, "do_" + stanza.name,
                    lambda *args: self.doCmd(stanza.name, *args))
            setattr(Interface, "do_" + stanza.name,
                    lambda *args: self.doCmd(stanza.name, *args))
        if not hasattr(self, "help_" + stanza.name):
            setattr(self, "help_" + stanza.name,
                    lambda *args: self.doHelp(stanza.name, *args))
            setattr(Interface, "help_" + stanza.name,
                    lambda *args: self.doHelp(stanza.name, *args))

    @logEx
    def doCmd(self, name, arg):
        argmap = self.collate_args(arg, name)
        if argmap:
            self.handler.handleCmd(name, argmap)

    @logEx
    def doHelp(self, name):
        doc = "Usage: " + name
        for attr in self.cmd_args[name]:
            doc += " [%s]" % attr
        print doc

    @logEx
    def collate_args(self, arg, cmd_name):
        cmd_args = self.cmd_args[cmd_name]
        args = self._white_space.split(arg)
        if not len(args):
            help_func = getattr(self, "help_" + cmd_name)
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
        for index in range(len(cmd_args.ordered)):
            if index >= len(ordered):
                break
            key = cmd_args.ordered[index]
            if key.name in argmap:
                return
            argmap[key.name] = ordered[index]
        return argmap

    @logEx
    def arg_complete(self, text, line, begidx, endix):
        args = self._white_space.split(line)
        parser = DumbParser(self.cmdparser, self.debug, True, self)
        parser.state = parser.STATE_ATTR_NAME
        parser.cur_elem = Elem(args[0:1][0], parent = parser.root)
        for arg in args:
            parser.cur_elem.attrs[arg] = Attr(arg, [""])
        parser.parse(" ".join(args[1:]))
        ret = parser.complete(text)
        return ret

    @logEx
    def completedefault(self, text, line, begidx, endix):
        if not line.startswith("<"):
            return []
        parser = DumbParser(self.xsdparser, self.debug, completer=self)
        parser.parse(line)
        return parser.complete(text)

    @logEx
    def default(self, line):
        if line == "EOF":
            # print
            return True
        self.handler.handleXML(line)

    @logEx
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

    ##
    ## Completer functions
    ##
    @logEx
    def doComplete(self, name, match):
        func = getattr(self, "complete_" + name)
        if func:
            return func(match)
        else:
            return []

    @logEx
    def complete_rosterTo(self, to):
        jids = self.roster.keys()
        jids.sort()
        if not len(to):
            return jids
        for jid in jids:
            if jid.startswith(to):
                return [jid]
        else:
            if "@" not in to:
                return [to + "@" + self.stream_info["hostname"]]
            else:
                return [to]

    @logEx
    def complete_from(self):
        return self.stream_info["jid"]

    @logEx
    def complete_hostJid(self, to):
        if not len(to):
            return []
        elif "@" in to:
            return [to]
        else:
            return [to + "@" + self.stream_info["hostname"]]

    ###
    ### Command functions
    ###

    @logEx
    def help_help(self):
        self.do_help()

    @logEx
    def do_roster(self, arg):
        argmap = self.collate_args(arg, "roster")
        if not argmap:
            return
        all = argmap["all"]
        print "Roster:"
        for jid, entry in self.roster.iteritems():
            if all:
                print "%s:" % jid
                for res, rentry in entry["resources"].iteritems():
                    pri = "0"
                    if "priority" in rentry and rentry["priority"]:
                        pri = rentry["priority"]
                    print "   %s(%s)" % (res, pri),
                    if (("status" in rentry) and rentry["status"] and
                        (rentry["status"] != "Available")):
                        print " status(%s)" % rentry["status"],
                    if "show" in rentry and rentry["show"]:
                        print " show(%s)" % rentry["show"],
                    print
            else:
                num = len(entry["resources"])
                if num > 1:
                    print "%s(%d)" % (jid, num)
                else:
                    print "%s" % jid
