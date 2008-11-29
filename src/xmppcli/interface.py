import cmd, re
from xmppcli.parser import *
from xmppcli import logEx


__all__ = ["ansiColor", "Interface", "StanzaHandler"]


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


class StanzaHandler(object):
    def handlePresence(self, argmap):
        print "handlePresence:", argmap

    def handleMessage(self, argmap):
        print "handleMessage:", argmap

    def handleIQ(self, argmap):
        print "handleIQ:", argmap


class Interface(cmd.Cmd):

    _white_space = re.compile("[ \\t\\n\\r]*")
    _message_args = ["to", "type", "subject", "body", "thread"]
    _presence_args = ["to", "type", "priority", "show", "status"]
    _iq_args = ["to", "type", "id", "xmlns", "child"]

    def __init__(self, handler, stream_info):
        import atexit, sys, termios
        self.__old_termios = termios.tcgetattr(sys.__stdin__.fileno())
        atexit.register(self.cleanup)

        cmd.Cmd.__init__(self)
        self.user_rawinput = True
        self.handler = handler
        self.stream_info = stream_info

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
            parser = DumbParser()
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
            parser = DumbParser()
            parser.parse(line)
            return parser.complete(text)
        except Exception, e:
            logEx(e)
        return []

    def default(self, line):
        print
        print "DEFAULT", line
        print

    def do_EOF(self, arg):
        print
        return True

    def emptyline(self):
        pass

    def run(self):
        try:
            self.cmdloop()
        except KeyboardInterrupt:
            print
        except Exception, e:
            logEx(e)

    ###
    ### Command functions
    ###

    def help_presence(self):
        print "Usage: presence [to] [type] [priority] [show] [status]"

    def do_presence(self, arg):
        argmap = self.collate_args(arg, self._presence_args,
                                   self.help_presence)
        if argmap:
            self.handler.handlePresence(argmap)

    def complete_presence(self, text, line, begidx, endix):
        return self.arg_complete(text, line, begidx, endix)
