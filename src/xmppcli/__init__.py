# Copyright (C) 2008 James Newton
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


def logEx(e):
    import traceback
    print
    print traceback.print_exc()
    print e


def run():
    import thread
    client = XMPPClient()
    thread.start_new_thread(XMPPClient.run, (client,))
    ui = Interface(client, client.stream_info)
    ui.run()

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


from .parser import Attr, Elem, DumbParser
from .interface import Interface, StanzaHandler
from .client import XMPPClient
