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

import re, readline
from xmppcli import logEx


__all__ = ["Attr", "Elem", "DumbParser"]


class Attr(object):
    def __init__(self, name, values = None):
        self.name = name
        if values:
            self.values = values
        else:
            self.values = []

class Elem(object):
    def __init__(self, name, attrs = None, cdata = None, children = None,
                 parent = None):
        self.name = name
        self.attrs = {}
        if attrs:
            for attr in attrs:
                self.attrs[attr.name] = attr
        if cdata:
            self.cdata = cdata
        else:
            self.cdata = []
        if children:
            self.children = children
        else:
            self.children = []
        self.parent = parent
        if self.parent:
            self.parent.children.append(self)

    def doPrint(self, indent = "", recurse = True):
        print indent, self, self.name, ":", self.attrs, ":", self.children, ":",
        if self.parent:
            print self.parent.name, self.parent
        else:
            print
        if recurse:
            for child in self.children:
                child.doPrint(indent + "  ", False)

_stanza_error = Elem("error", [Attr("code"),
                               Attr("type", ["auth", "cancel", "continue",
                                             "modify", "wait"])])
_stanzas = \
{
    "presence" : \
    Elem("presence",
         [Attr("to"), Attr("from"), Attr("xmlns"), Attr("xml:lang"),
          Attr("type", ["error", "probe", "subscribe", "subscribed",
                        "unsubscribe", "unsubscribed"])],
         [],
         [Elem("show", None, ["away", "chat", "dnd", "xa"]),
          Elem("status"),
          Elem("priority"),
          _stanza_error]),
    "message" : \
    Elem("message",
         [Attr("to"), Attr("from"), Attr("xmlns"), Attr("id"), Attr("xml:lang"),
          Attr("type", ["chat", "error", "groupchat", "headline", "normal"])],
         [],
         [Elem("thread"),
          Elem("subject", [Attr("xml:lang")]),
          Elem("body", [Attr("xml:lang")]),
          Elem("x", [Attr("xmlns")]),
          _stanza_error]),
    "iq" : \
    Elem("iq",
         [Attr("to"), Attr("from"), Attr("xmlns"), Attr("id"), Attr("xml:lang"),
          Attr("type", ["error", "get", "result", "set"])],
         [],
         [Elem("query", [Attr("xmlns")]),
          _stanza_error])
}

class DumbParser(object):
    STATE_NONE = 0
    STATE_NAME = 1
    STATE_ATTR_NAME = 2
    STATE_ATTR_VAL = 3
    STATE_CLOSING = 5
    STATE_CDATA = 6

    _states = \
    {
        STATE_NONE : "none", STATE_NAME : "name", STATE_ATTR_NAME : "attr_name",
        STATE_ATTR_VAL : "attr_val", STATE_CLOSING : "closing",
        STATE_CDATA : "cdata"
    }

    def __init__(self, debug = False):
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
        for i in range(10 - len(state)):
            state = state + " "
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
                               self.cur_attr_val
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

    def complete(self, text):
        try:
            def recursor(elem, syn = None, target = None):
                if not syn:
                    if elem.name in _stanzas.keys():
                        syn = _stanzas[elem.name]
                    else:
                        return None, None
                else:
                    if len(syn.children):
                        for child in syn.children:
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
            if ((self.cur_elem != self.root) and len(self.root.children)):
                if self.state == self.STATE_CLOSING:
                    target = self.prev_elem
                else:
                    target = None
                target = self.cur_elem
                elem, syn = recursor(self.root.children[-1:][0], None, target)
            else:
                elem, syn = None, None
            if not elem or not syn:
                ret = [stanza for stanza in _stanzas.keys()
                       if stanza.startswith(text)]
                if len(ret) == 1:
                    return [ret[0] + " "]
                else:
                    if self.last_non_space_c == ">":
                        readline.insert_text("<")
                    return ret
            if self.state == self.STATE_NAME:
                ret = [e.name for e in syn.children
                       if e.name.startswith(text)]
                if len(ret) == 1:
                    return [ret[0] + " "]
                else:
                    return ret
            elif self.state == self.STATE_ATTR_NAME:
                if len(syn.attrs) == 0:
                    return [">"]
                elif ((self.last_c == "'") or (self.last_c == '"')):
                    return [" "]
                ret = [attr.name for attr in syn.attrs.values()
                       if attr.name.startswith(text)]
                if text in ret:
                    return [text + "='"]
                elif len(ret) == 1:
                    return [ret[0] + "='"]
                else:
                    return ret
            elif self.state == self.STATE_ATTR_VAL:
                attr = [attr for attr in syn.attrs.values()
                        if attr.name == self.cur_attr_name]
                if len(attr) and len(attr[0].values):
                    return [val for val in attr[0].values
                            if val.startswith(text)]
            elif self.state == self.STATE_CLOSING:
                if self.last_non_space_c2 == "<":
                    return [syn.name + ">"]
                else:
                    if self.last_non_space_c == "/":
                        return [">"]
                    if self.last_non_space_c == ">":
                        return [i.name for i in self.cur_elem.children
                                if ((not text) or
                                    (text and i.name.startswith(text)))]
                    else:
                        return [i.name for i in self.cur_elem.parent.children
                                if ((not text) or
                                    (text and i.name.startswith(text)))]
            elif self.state == self.STATE_CDATA:
                if not len(syn.cdata):
                    return ["<"]
                elif text in syn.cdata:
                    return [text + "</" + syn.name + ">"]
                else:
                    return [cdata for cdata in syn.cdata
                            if cdata.startswith(text)]
            else:
                ret = [attr.name for attr in syn.attrs.values()
                       if attr.name.startswith(text)]
                if text in ret:
                    return [" " + text + "='"]
                elif len(ret) == 1:
                    return [" " + ret[0] + "='"]
                else:
                    return [" " + i for i in ret]
        except Exception, e:
            logEx(e)
