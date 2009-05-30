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

import re, readline
from . import *


class DumbParser(object):
    (STATE_NONE,
     STATE_NAME,
     STATE_ATTR_NAME,
     STATE_ATTR_VAL,
     STATE_CLOSING,
     STATE_CDATA,
     STATE_COMMENT) = range(7)

    _states = \
    {
        STATE_NONE : "none", STATE_NAME : "name", STATE_ATTR_NAME : "attr_name",
        STATE_ATTR_VAL : "attr_val", STATE_CLOSING : "closing",
        STATE_CDATA : "cdata"
    }

    def __init__(self, xsdparser, debug = False):
        self.xsdparser = xsdparser
        self.root = Elem("root")
        self.root.parent = self.root
        self.cur_elem = self.root
        self.prev_elem = None
        self.last_elem = None
        self.cur_name = ""
        self.cur_attr_name = ""
        self.cur_attr_val = ""
        self.cdata = ""
        self.last_c = " "
        self.last_non_space_c = " "
        self.last_non_space_c2 = " "
        self.quote = 0
        self.state = self.STATE_NONE
        self.debug = debug

    def summarize(self, c):
        if not self.debug:
            return
        if not c:
            print
            print "FINAL STATE"
        state = self._states[self.state]
        state += "".join([" " for c in range(10 - len(state))])
        if c == None:
            print " ",
        else:
            print c,
        print "state", state, "quote", self.quote, "last_c", self.last_c,
        print "last_nsc", self.last_non_space_c,
        print "last_nsc2", self.last_non_space_c2,
        print "cur_name:", self.cur_name, "cur_attr_name", self.cur_attr_name,
        print "cur_attr_val", self.cur_attr_val

    def parse(self, val):
        for c in val:
            if ((c != " ") and (c != "\t") and (c != "\r") and (c != "\n") and
                (self.last_c == self.last_non_space_c)):
                self.last_non_space_c2 = self.last_non_space_c
            self.summarize(c)
            if ((c == "\"") or (c == "\'")):
                if self.quote == c:
                    self.quote = 0
                    if self.state == self.STATE_ATTR_VAL:
                        self.state = self.STATE_ATTR_NAME
                        self.cur_elem.attrs[self.cur_attr_name] = \
                               Attr(self.cur_attr_name, [self.cur_attr_val])
                        self.cur_attr_name = ""
                        self.cur_attr_val = ""
                elif self.quote:
                    pass
                else:
                    self.quote = c
            elif self.quote:
                if self.state == self.STATE_ATTR_VAL:
                    self.cur_attr_val += c
                else:
                    pass
            elif c == ">":
                self.cur_attr_name = ""
                self.cur_attr_val = ""
                if ((self.state == self.STATE_NAME) and len(self.cur_name)):
                    self.cur_elem = Elem(self.cur_name, parent=self.cur_elem)
                if self.state == self.STATE_CLOSING:
                    self.prev_elem = self.cur_elem
                    self.cur_elem = self.cur_elem.parent
                if self.state == self.STATE_COMMENT:
                    self.state = self.STATE_NONE
                else:
                    self.state = self.STATE_CDATA
            elif c == "<":
                self.cur_name = ""
                self.state = self.STATE_NAME
                if len(self.cdata):
                    self.cur_elem.cdata.append(self.cdata)
                self.cdata = ""
            elif self.state == self.STATE_CLOSING:
                pass
            elif ((c == " ") or (c == "\t") or (c == "\r") or (c == "\n")):
                if ((self.last_c == " ") or (self.last_c == "\t") or
                    (self.last_c == "\r") or (self.last_c == "\n")):
                    pass
                if self.state == self.STATE_NAME:
                    self.state = self.STATE_ATTR_NAME
                    self.cur_attr_name = ""
                    self.cur_attr_value = ""
                    if len(self.cur_name):
                        self.cur_elem = Elem(self.cur_name,
                                             parent=self.cur_elem)
            elif c == "/":
                if ((self.state == self.STATE_NAME) and len(self.cur_name)):
                    self.cur_elem = Elem(self.cur_name, parent=self.cur_elem)
                self.state = self.STATE_CLOSING
            elif c == "=":
                if self.state == self.STATE_ATTR_NAME:
                    self.cur_elem.attrs[self.cur_attr_name] = None
                self.cur_attr_val = ""
                self.state = self.STATE_ATTR_VAL
            elif ((c == "!") and self.last_c == "<"):
                self.state = self.STATE_COMMENT
            else:
                if self.state == self.STATE_NAME:
                    self.cur_name += c
                elif self.state == self.STATE_ATTR_NAME:
                    self.cur_attr_name += c
                elif self.state == self.STATE_ATTR_VAL:
                    self.cur_attr_val += c
                elif self.state == self.STATE_CDATA:
                    self.cdata += c
                else:
                    self.state = self.STATE_ATTR_NAME
                    self.cur_attr_name = c
            self.last_c = c
            if ((c != " ") and (c != "\t") and (c != "\r") and (c != "\n")):
                self.last_non_space_c = c
        self.summarize(None)

    @logEx
    def complete(self, text):
        def recursor(elem, syn = None, target = None):
            xmlns = elem.parent.findMainNS()
            if not syn:
                if elem.name in self.xsdparser.stanzas.keys():
                    syn = self.xsdparser.stanzas[elem.name]
                else:
                    return None, None
            else:
                if len(syn.nsed(xmlns).children):
                    for child in syn.nsed(xmlns).children:
                        if elem.name == child.name:
                            syn = child
                            break
                    else:
                        return None, None
            if elem is target:
                return elem, syn
            elif len(elem.children):
                return recursor(elem.children[-1:][0], syn, target)
            else:
                return elem, syn
        if ((self.cur_elem != self.root) and
            len(self.root.children)):
            if self.state == self.STATE_CLOSING:
                target = self.prev_elem
            else:
                target = None
            target = self.cur_elem
            elem, syn = recursor(self.root.children[-1:][0], None,
                                 target)
        else:
            elem, syn = None, None
        if not elem or not syn:
            ret = [stanza for stanza in self.xsdparser.stanzas.keys()
                   if stanza.startswith(text)]
            if len(ret) == 1:
                return [ret[0] + " "]
            else:
                if self.last_non_space_c == ">":
                    readline.insert_text("<")
                return ret
        xmlns = elem.findMainNS()
        if self.state == self.STATE_NAME:
            names = [c.name for c in elem.children]
            ret = [e for e in syn.nsed(xmlns).children
                   if (e.name.startswith(text) and
                       (e.multi or e.name not in names))]
            if (len(ret) == 1):
                if ret[0].isEmpty():
                    return [ret[0].name + "/>"]
                elif len(text):
                    return [ret[0].name + " "]
            ret = [e.name for e in ret]
            if len(text):
                return ret
            else:
                return ret + ["/"]
        elif self.state == self.STATE_ATTR_NAME:
            if ((self.last_c == "'") or (self.last_c == '"')):
                return [text + " "]
            elif len(syn.nsed(xmlns).attrs) == 0:
                return [">"]
            ret = [attr.name for attr in syn.nsed(xmlns).attrs.values()
                   if attr.name.startswith(text) and
                       attr.name not in elem.attrs.keys()]
            if len(ret) == 0:
                return [">"]
            elif text in ret:
                if syn.nsed(xmlns).attrs[text].vtype == VTYPE_FLAG:
                    return [text + " "]
                else:
                    return [text + "='"]
            elif len(ret) == 1:
                if syn.nsed(xmlns).attrs[ret[0]].vtype == VTYPE_FLAG:
                    return [ret[0] + " "]
                else:
                    return [ret[0] + "='"]
            else:
                return ret
        elif self.state == self.STATE_ATTR_VAL:
            if self.quote:
                quote = self.quote
            else:
                quote = "'"
            nqt = text.lstrip(quote)
            vallist = None
            if (len(syn.nsmap) and
                ((self.cur_attr_name == "xmlns") or
                 self.cur_attr_name.startswith("xmlns:"))):
                vallist = syn.nsmap.keys()
            else:
                attr = [attr for attr in syn.nsed(xmlns).attrs.values()
                        if attr.name == self.cur_attr_name]
                if len(attr) and len(attr[0].values):
                    vallist = attr[0].values
            if vallist:
                ret = [quote + val for val in vallist
                       if isinstance(val, str) and val.startswith(nqt)]
                if len(ret) == 1:
                    return [ret[0] + quote]
                else:
                    return ret
            else:
                return [text + quote]
        elif self.state == self.STATE_CLOSING:
            if self.last_non_space_c2 == "<":
                if self.last_non_space_c == "/":
                    return ["/" + syn.name + ">"]
                else:
                    return [syn.name + ">"]
            else:
                if self.last_non_space_c == "/":
                    return ["/>"]
                if self.last_non_space_c == ">":
                    return [i.name for i in self.cur_elem.children
                            if ((not text) or
                                (text and i.name.startswith(text)))]
                else:
                    return [i.name for i in
                            self.cur_elem.parent.children
                            if ((not text) or
                                (text and i.name.startswith(text)))]
        elif self.state == self.STATE_CDATA:
            if not len(syn.nsed(xmlns).cdata):
                return ["<"]
            elif text in syn.nsed(xmlns).cdata:
                return [text + "</" + syn.name + ">"]
            else:
                ret = [cdata for cdata in syn.nsed(xmlns).cdata
                       if isinstance(cdata, str) and
                       cdata.startswith(text)]
                if len(ret):
                    return ret
                else:
                    return ["<"]
        else:
            ret = [attr.name for attr in syn.nsed(xmlns).attrs.values()
                   if attr.name.startswith(text)]
            if text in ret:
                return [" " + text + "='"]
            elif len(ret) == 1:
                return [" " + ret[0] + "='"]
            else:
                return [" " + i for i in ret]
