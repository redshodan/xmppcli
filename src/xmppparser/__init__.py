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

class HList(list):
    def __init__(self, *args):
        self.extend(args)

    def __hash__(self):
        ret = 0
        for item in self:
            ret += item.__hash__()
        return ret

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
        print indent + "     attr(%s):" % self.name, self.values, self.required,
        print vtypes[self.vtype]

class Elem(object):
    ALL = object()

    def __init__(self, name, nsmap = None, parent = None, ns = None):
        self.name = name
        self.default_nsed = None
        #self.nsmap = NSMap()
        self.nsmap = {}
        if nsmap:
            for nsed in nsmap:
                nsed.parent = self
                if nsed.ns:
                    self.nsmap[nsed.ns] = nsed
                    if not self.default_nsed:
                        self.default_nsed = nsed
                else:
                    self.default_nsed = nsed
        if not self.default_nsed:
            self.default_nsed = NSed()
            self.default_nsed.parent = self
        self.parent = parent
        if self.parent:
            self.parent.nsed(ns).children.append(self)
            for nsed in self.nsmap.values():
                nsed.extendNS(self.parent.nsed(nsed.ns))
            if self.parent.ns:
                self.default_nsed.extendNS(self.parent.default_nsed)
        self.pns = ns
        self.multi = False
        self.looped = False

    def deepCopy(self, parent, pns = None):
        copy = Elem("COPY")
        copy.name = self.name
        copy.default_nsed = self.default_nsed.deepCopy(copy)
        for key, val in self.nsmap.iteritems():
            copy.nsmap[key] = val.deepCopy(copy)
        copy.parent = parent
        copy.pns = self.pns
        if parent:
            if not pns:
                pns = self.pns
            parent.nsed(pns).children.append(copy)
        copy.multi = self.multi
        copy.looped = self.looped
        return copy

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

    def find(self, name, recurse=False, filter=[], ns=None):
        for child in self.nsed(ns).children:
            if child.name == name:
                return child
        if recurse:
            for child in self.children:
                if child.name not in filter:
                    return child.find(name, recurse, filter, ns)
        return None

    def findOrMakeNSed(self, ns):
        if not ns:
            return self.default_nsed
        elif ns in self.nsmap:
            return self.nsmap[ns]
        else:
            nsed = NSed(ns)
            self.nsmap[ns] = nsed
            nsed.parent = self
            return nsed

    def isEmpty(self):
        if len(self.nsmap) or not self.default_nsed.isEmpty():
            return False
        else:
            return True

    def doPrint(self, indent = "", ns = ALL, recurse = True, doloop = True):
        if self.parent:
            pname = self.parent.name
        else:
            pname = ""
        if self.looped:
            if doloop:
                doloop = False
            else:
                print indent, "elem(%s):" % self.name, pname, ": LOOPED"
                return
        print indent, "elem(%s):" % self.name, pname, ":",
        print vtypes[self.nsed(ns).vtype],
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
        self.parent = None

    def deepCopy(self, parent):
        copy = NSed()
        copy.ns = self.ns
        copy.nses.update(self.nses)
        copy.attrs.update(self.attrs)
        copy.cdata.extend(self.cdata)
        for child in self.children:
            copy.children.append(child.deepCopy())
        copy.vtype = self.vtype
        copy.parent = parent
        return copy

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
            if self.ns:
                pns = self.ns
            else:
                pns = "default"
            print indent, "NS(%s):" % pns, self.parent.name
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
