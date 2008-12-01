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


import gloox
from xmppcli import *


class TagHandler(gloox.TagHandler):
    def __init__(self):
        gloox.TagHandler.__init__(self)
        self.output = []

    def reset(self):
        del self.output[:]

    def handleTag(self, tag):
        try:
            print "TAG", tag.xml()
            self.output.append(tag)
        except Exception, e:
            logEx(e)

_handler = TagHandler()
_parser = gloox.Parser(_handler)


def parse(xml):
    parser = DumbParser()
    print "parsing:", xml
    parser.parse(xml)
    def recursor(dp_elem, gl_parent):
        if gl_parent:
            gl_elem = gloox.Tag(gl_parent, dp_elem.name)
        else:
            gl_elem = gloox.Tag(dp_elem.name)
        for name, val in dp_elem.attrs.iteritems():
            gl_elem.addAttribute(name, val)
        for dp_cdata in dp_elem.cdata:
            gl_elem.addCData(dp_cdata)
        for dp_child in dp_elem.children:
            recursor(dp_child, gl_elem)
        return gl_elem
    elems = []
    for elem in parser.root.children:
        elems.append(recursor(elem, None))
    return elems
#     _handler.reset()
#     if _parser.feed(xml):
#         return _handler.output
#     else:
#         return []
