import re


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

    def __init__(self, debug = False):
        self.root = Elem("root")
        self.cur_elem = self.root
        self.prev_elem = None
        self.last_elem = None
        self.in_quote = 0
        self.cur_name = ""
        self.in_name = 0
        self.cur_attr_name = ""
        self.in_attr_name = 0
        self.cur_attr_val = ""
        self.in_attr_val = 0
        self.closing_tag = 0
        self.in_cdata = 0
        self.last_c = ""
        self.last_non_space_c = ""
        self.last_non_space_c2 = ""
        self.debug = debug

    def summarize(self, c):
        if not self.debug:
            return
        if not c:
            print
            print "FINAL STATE"
        print c, "in_quote:", self.in_quote,
        print "closing_tag", self.closing_tag, "in_name", self.in_name,
        print "in_attr_name", self.in_attr_name,
        print "in_attr_val", self.in_attr_val, "in_cdata", self.in_cdata,
        print "cur_name:", self.cur_name, "cur_attr_name", self.cur_attr_name,
        print "cur_attr_val", self.cur_attr_val, "last_c", self.last_c,
        print "last_nsc", self.last_non_space_c

    def parse(self, val):
        for c in val:
            if ((c != " ") and (c != "\t") and (c != "\r") and (c != "\n") and
                (self.last_c == self.last_non_space_c)):
                self.last_non_space_c2 = self.last_non_space_c
            self.summarize(c)
            if ((c == "\"") or (c == "\'")):
                if self.in_quote == c:
                    self.in_quote = 0
                    if self.in_attr_val:
                        self.in_attr_val = 0
                        self.cur_elem.attrs[self.cur_attr_name] = \
                               self.cur_attr_val
                        self.cur_attr_name = ""
                        self.cur_attr_val = ""
                elif self.in_quote:
                    pass
                else:
                    self.in_quote = c
            elif self.in_quote:
                if self.in_attr_val:
                    self.cur_attr_val += c
                else:
                    pass
            elif c == ">":
                if not self.closing_tag:
                    self.in_cdata = 1
                self.closing_tag = 0
                self.cur_attr_name = ""
                self.cur_attr_val = ""
                if self.in_name:
                    self.in_name = 0
                    if len(self.cur_name):
                        self.cur_elem = Elem(self.cur_name,
                                             parent=self.cur_elem)
            elif c == "<":
                self.cur_name = ""
                self.in_name = 1
                self.in_cdata = 0
            elif self.closing_tag:
                pass
            elif ((c == " ") or (c == "\t") or (c == "\r") or (c == "\n")):
                if ((self.last_c == " ") or (self.last_c == "\t") or
                    (self.last_c == "\r") or (self.last_c == "\n")):
                    pass
                if self.in_name:
                    self.in_name = 0
                    self.in_attr_name = 1
                    self.cur_attr_name = ""
                    self.cur_attr_value = ""
                    if len(self.cur_name):
                        self.cur_elem = Elem(self.cur_name,
                                             parent=self.cur_elem)
                elif self.in_attr_name:
                    self.in_attr_name = 0
                    self.cur_elem.attrs[self.cur_attr_name] = None
                else:
                    self.in_attr_name = 1
                    self.cur_attr_name = ""
                    self.cur_attr_value = ""
            elif c == "/":
                if self.in_name:
                    self.in_name = 0
                    if len(self.cur_name):
                        self.cur_elem = Elem(self.cur_name,
                                             parent=self.cur_elem)
                self.in_attr_name = 0
                self.closing_tag = 1
                self.prev_elem = self.cur_elem
                self.cur_elem = self.cur_elem.parent
            elif c == "=":
                if self.in_attr_name:
                    self.in_attr_name = 0
                    self.cur_elem.attrs[self.cur_attr_name] = None
                self.in_attr_val = 1
                self.cur_attr_val = ""
            else:
                if self.in_name:
                    self.cur_name += c
                elif self.in_attr_name:
                    self.cur_attr_name += c
                elif self.in_attr_val:
                    self.cur_attr_val += c
                elif self.in_cdata:
                    pass
                else:
                    self.in_attr_name = 1
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
            if len(self.root.children):
                if self.closing_tag:
                    target = self.prev_elem
                else:
                    target = None
                elem, syn = recursor(self.root.children[-1:][0], None, target)
            else:
                elem, syn = None, None
            if not elem or not syn:
                ret = [stanza for stanza in _stanzas.keys()
                       if stanza.startswith(text)]
                if len(ret) == 1:
                    return [ret[0] + " "]
            if self.in_name:
                ret = [e.name for e in syn.children
                       if e.name.startswith(text)]
                if len(ret) == 1:
                    return [ret[0] + " "]
                else:
                    return ret
            elif self.in_attr_name:
                ret = [attr.name for attr in syn.attrs.values()
                       if attr.name.startswith(text)]
                if text in ret:
                    return [text + "='"]
                elif len(ret) == 1:
                    return [ret[0] + "='"]
                else:
                    return ret
            elif self.in_attr_val:
                attr = [attr for attr in syn.attrs.values()
                        if attr.name == self.cur_attr_name]
                if len(attr) and len(attr[0].values):
                    return [val for val in attr[0].values
                            if val.startswith(text)]
            elif self.closing_tag:
                if self.last_non_space_c2 == "<":
                    return [syn.name + ">"]
                else:
                    return [">"]
            elif self.in_cdata:
                if text in syn.cdata:
                    return [text + "</" + syn.name + ">"]
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
            try:
                print
                print repr(e)
            except Exception, e:
                print e
