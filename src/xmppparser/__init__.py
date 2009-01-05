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


_debug = False


def logEx(e):
    import traceback
    print
    print traceback.print_exc()
    print e


(VTYPE_NONE, VTYPE_STR, VTYPE_INT, VTYPE_UINT, VTYPE_FLOAT,
 VTYPE_BOOL, VTYPE_CHOICE) = range(7)
vtypes = \
{
    VTYPE_NONE : "VTYPE_NONE",
    VTYPE_STR : "VTYPE_STR",
    VTYPE_INT : "VTYPE_INT",
    VTYPE_UINT : "VTYPE_UINT",
    VTYPE_FLOAT : "VTYPE_FLOAT",
    VTYPE_BOOL : "VTYPE_BOOL",
    VTYPE_CHOICE : "VTYPE_CHOICE",
}

# Stanza syntax tree
stanzas = {}

class ValuePattern(object):
    def __init__(self, pattern):
        self.pattern = pattern

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

    def doPrint(self, indent=""):
        print indent + "     attr:", self.name, self.values, self.required,
        print vtypes[self.vtype]

class Elem(object):
    ALL = object()

    def __init__(self, name, nsmap = None, parent = None, ns = None):
        self.name = name
        self.default_nsed = None
        self.nsmap = {}
        if nsmap:
            for nsed in nsmap:
                if nsed.ns:
                    self.nsmap[nsed.ns] = nsed
                    if not self.default_nsed:
                        self.default_nsed = nsed
                else:
                    self.default_nsed = nsed
        if not self.default_nsed:
            self.default_nsed = NSed()
        self.parent = parent
        if self.parent:
            self.parent.nsed(ns).children.append(self)
            for nsed in self.nsmap.values():
                nsed.extendNS(self.parent.nsed(nsed.ns))
            if self.parent.ns:
                self.default_nsed.extendNS(self.parent.default_nsed)
        self.multi = False
        self.looped = False

    @property
    def ns(self):
        return self.nsed().ns

    @property
    def nses(self):
        return self.nsed().nses

    @property
    def attrs(self):
        return self.nsed().attrs

    @property
    def cdata(self):
        return self.nsed().cdata

    @property
    def children(self):
        return self.nsed().children

    def vtype_get(self):
        return self.nsed().vtype
    def vtype_set(self, vtype):
        self.nsed().vtype = vtype
    vtype = property(vtype_get, vtype_set)

    def nsed(self, ns = None):
        try:
            return self.nsmap[ns]
        except KeyError:
            pass
        return self.default_nsed

    def find(self, name, recurse = False, filter = []):
        def recursor():
            for child in self.children:
                if child.name not in filter:
                    return child.find(name, recurse, filter)
        for child in self.children:
            if child.name == name:
                return child
        if recurse:
            return recursor()
        return None

    def isEmpty(self):
        if len(self.nsmap) or not self.default_nsed.isEmpty():
            return False
        else:
            return True

    def doPrint(self, indent = "", ns = ALL, recurse = True, doloop = True):
        if self.looped:
            if doloop:
                doloop = False
            else:
                print indent, "elem:", self.name, ": LOOPED"
                return
        print indent, "elem:", self.name, ":", vtypes[self.nsed(ns).vtype],
        if _debug and self.parent:
            print ": parent=" + self.parent.name
        else:
            print
        if len(self.nsmap):
            header = True
        else:
            header = False
        if ns == self.ALL:
            if self.default_nsed not in self.nsmap.values():
                self.default_nsed.doPrint(indent, ns, recurse, header, doloop)
            for nsed in self.nsmap.values():
                nsed.doPrint(indent, ns, recurse, doloop=doloop)
        else:
            self.nsed(ns).doPrint(indent, ns, recurse, header, doloop)

class NSed(object):
    def __init__(self, ns = None, attrs = None, cdata = None, children = None,
                 vtype = VTYPE_NONE):
        self.ns = ns
        self.nses = {}
        self.attrs = {}
        if attrs:
            for attr in attrs:
                self.attrs[attr.name] = attr
        if self.ns:
            self.attrs["xmlns"] = Attr("xmlns", [ns])
        if cdata:
            self.cdata = cdata
        else:
            self.cdata = []
        if children:
            self.children = children
        else:
            self.children = []
        self.vtype = vtype

    def extendNS(self, parent_nsed):
        for key, val in parent_nsed.nses.iteritems():
            if val != self.ns:
                self.nses[key] = val

    def isEmpty(self):
        if (len(self.attrs) or len(self.cdata) or len(self.children)):
            return False
        else:
            return True

    def doPrint(self, indent="", ns = Elem.ALL, recurse = True, header=True,
                doloop=True):
        if header:
            print indent, "NS:",
            if self.ns:
                print self.ns
            else:
                print "default"
        if _debug and len(self.nses):
            print indent, "    nses:",
            for key, val in self.nses.iteritems():
                print key, ":", val.values[0],
            print
        if len(self.cdata):
            print indent, "    cdata:",
            for cd in self.cdata:
                if isinstance(cd, str):
                    print cd,
                else:
                    print "pattern(%s)" % cd.pattern,
            print
        for attr in self.attrs.values():
            attr.doPrint(indent)
        if recurse:
            for child in self.children:
                child.doPrint(indent + "  ", ns, doloop=doloop)

def init(home):
    XSDParser.parseXSDList(home)


from .DumbParser import DumbParser
XSDParser = None
import XSDParser

from .interface import Interface
from . import interface
