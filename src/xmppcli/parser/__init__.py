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


__all__ = ["Attr", "Elem", "NSed", "DumbParser", "XSDParser",
           "VTYPE_NONE", "VTYPE_STR", "VTYPE_INT", "VTYPE_UINT", "VTYPE_BOOL"]


(VTYPE_NONE, VTYPE_STR, VTYPE_INT, VTYPE_UINT, VTYPE_BOOL) = range(5)
vtypes = \
{
    VTYPE_NONE : "VTYPE_NONE",
    VTYPE_STR : "VTYPE_STR",
    VTYPE_INT : "VTYPE_INT",
    VTYPE_UINT : "VTYPE_UINT",
    VTYPE_BOOL : "VTYPE_BOOL"
}


class Attr(object):
    def __init__(self, name, values = None, required = False,
                 vtype = VTYPE_NONE):
        self.name = name
        self.required = required
        self.vtype = vtype
        if values:
            self.values = values
        else:
            self.values = []

    def value(self):
        if len(self.values):
            return self.values[0]
        else:
            return None

    def doPrint(self, indent):
        print indent + "     attr:", self.name, self.values, self.required,
        print vtypes[self.vtype]

class NSed(object):
    def __init__(self, ns = None, attrs = None, cdata = None, children = None,
                 vtype = VTYPE_NONE):
        if ns is None:
            self.nsname = "xmlns"
            self.ns = ns
        elif ns is tuple:
            self.nsname = ns[0]
            self.ns = ns[1]
        else:
            self.nsname = "xmlns"
            self.ns = ns
        self.attrs = {}
        if attrs:
            for attr in attrs:
                self.attrs[attr.name] = attr
        if self.ns:
            self.attrs[self.nsname] = Attr(self.nsname, [ns])
        if cdata:
            self.cdata = cdata
        else:
            self.cdata = []
        if children:
            self.children = children
        else:
            self.children = []
        self.vtype = vtype

class Elem(object):
    def __init__(self, name, nsmap = None, parent = None, multi=False):
        self.name = name
        self.default_nsed = NSed()
        self.nsmap = {}
        if nsmap:
            for nsed in nsmap:
                if nsed.ns:
                    self.nsmap[nsed.ns] = nsed
                else:
                    self.default_nsed = nsed
        self.parent = parent
        if self.parent:
            self.parent.nsed().children.append(self)
        self.multi = multi

    @property
    def attrs(self):
        return self.nsed().attrs

    @property
    def cdata(self):
        return self.nsed().cdata

    @property
    def children(self):
        return self.nsed().children

    @property
    def vtype(self):
        return self.nsed().vtype

    def nsed(self, ns = None):
        try:
            return self.nsmap[ns]
        except KeyError:
            pass
        return self.default_nsed

    def find(self, name):
        for child in self.children:
            if child.name == name:
                return child
        return None

    def doPrint(self, indent = "", ns = None, recurse = True):
        print indent, self, self.name, ":", vtypes[self.nsed(ns).vtype], ":",
        if self.parent:
            print self.parent.name, self.parent
        else:
            print
        for attr in self.nsed(ns).attrs.values():
            attr.doPrint(indent)
        if recurse:
            for child in self.nsed(ns).children:
                child.doPrint(indent + "  ", ns)


from .DumbParser import DumbParser
XSDParser = None
import XSDParser
