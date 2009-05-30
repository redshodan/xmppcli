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


import os, stat
import cPickle as pickle
from xmppparser import *
from .DumbParser import DumbParser


class XSDParser(object):
    def __init__(self, home, xsdlist = None):
        self.home = home
        self.xsdlist = xsdlist
        self.stanzas = {}
        self.base_syntax = {}
        self.nsed_xsd = {}
        self.required_ns = ["xmppparser:base", "jabber:client"]
        self._recursor_stack = []
        self.pickled_fname = os.path.join(self.home, "xsd", "stanzas.pkl")
        self.list_fname = os.path.join(self.home, "xsd", "list.py")

    def checkPickled(self, mappings):
        ptime = None
        try:
            info = os.stat(self.pickled_fname)
            if not stat.S_ISREG(info[stat.ST_MODE]):
                return False
            ptime = info[stat.ST_MTIME]
        except:
            return False
        info = os.stat(self.list_fname)
        if info[stat.ST_MTIME] > ptime:
            return False
        for mapping in mappings:
            filename = os.path.join(self.home, "xsd", mapping[3])
            info = os.stat(filename)
            if info[stat.ST_MTIME] > ptime:
                return False
        return True

    def load(self):
        if self.xsdlist:
            self.xsdlist.extend(self.required_ns)
        globs = {}
        execfile(self.list_fname, globs)
        if self.checkPickled(globs["mappings"]):
            pickled = open(self.pickled_fname, "rb")
            self.stanzas = pickle.load(pickled)
            pickled.close()
            return
        print "Loading XSD's for the first time, this may take a little time..."
        for mapping in globs["mappings"]:
            rootname = mapping[0]
            nodename = mapping[1]
            ns = mapping[2]
            if self.xsdlist and mapping[2] not in self.xsdlist:
                continue
            filename = os.path.join(self.home, "xsd", mapping[3])
            parser = self.parse(filename)
            root = None
            nsed = None
            if rootname:
                # Walk the path and create elements or NSeds if need be
                for rn in rootname:
                    if isinstance(rn, list):
                        name, rns = rn
                    else:
                        name, rns = (rn, None)
                    if not root:
                        root = self.stanzas[name]
                        nsed = root.findOrMakeNSed(rns)
                        continue
                    for child in nsed.children:
                        if child.name == name:
                            root = child
                            break
                    else:
                        for child in root.children:
                            if child.name == name:
                                tmp = child.deepCopy(root, nsed.ns)
                                tmp.parent = root
                                root = tmp
                                break
                        else:
                            raise Exception("Failed to find path: %s" %
                                            (str(rootname)))
                    nsed = root.findOrMakeNSed(rns)
            if root and nsed and nsed == root.default_nsed:
                nsed = None
            if nsed:
                rns = nsed.ns
            else:
                rns = None
            if not isinstance(nodename, list):
                nodename = [nodename]
            for node in nodename:
                self.generateSyntax(parser, node, ns, root, rns)

        print "Saving xsd information"
        pickled = open(self.pickled_fname, "wb")
        pickle.dump(self.stanzas, pickled)
        pickled.close()

    def parse(self, filename):
        parser = DumbParser(self)
        fp = file(filename)
        parser.parse(fp.read())
        fp.close()
        return parser
    
    def generateSyntax(self, parser, name, ns, sparent, sns):
        self._recursor_stack = []
        # Follow each xsd schema
        for elem in parser.root.children:
            if elem.name == "?xml":
                elem = elem.children[0]
            if elem.name != "xs:schema":
                raise Exception("Invalid XSD: " + filename)
            schema = elem
    
            if "targetNamespace" in elem.attrs:
                elemns = elem.attrs["targetNamespace"].value()
            else:
                elemns = elem.attrs["xmlns"].value()
            if elemns != ns:
                continue
    
            # Store each schema branch
            if not ns in self.nsed_xsd:
                self.nsed_xsd[ns] = {}
            root = None
            for child in elem.children:
                if "name" in child.attrs:
                    child.schema = schema
                    cname = child.attrs["name"].value()
                    self.nsed_xsd[ns][cname] = child
                    if not root and cname == name:
                        root = child
            if not root:
                if name:
                    raise Exception("Invalid XSD spec. Missing root element " +
                                    name)
                else:
                    return
    
            self._scanNSes(schema, root)
    
            if sns:
                self._recursor(schema, root, sparent, ns, sns, False)
                return
            elif sparent:
                for schild in sparent.children:
                    if schild.name == name:
                        if ns == "jabber:client":
                            nsed_ns = None
                        else:
                            nsed_ns = ns
                            nsed = schild.findOrMakeNSed(nsed_ns)
                            nsed.vtype = self._parseType(root)
                        for child in root.nsed(nsed_ns).children:
                            self._recursor(schema, child, schild, None, ns,
                                           False)
                        return None
            schild = self._recursor(schema, root, sparent, ns, None, False)
            if ns == "xmppparser:base":
                self.base_syntax[schild.name] = schild
            # Store the top level schema on this schema branch
            def _putter(elem, schema):
                elem.schema = schema
                for child in elem.children:
                    _putter(child, schema)
            _putter(root, schema)
            if ns == "jabber:client":
                self.stanzas[schild.name] = schild
            return schild
        else:
            raise Exception("Could not find elem in xsd:", name, ns)
    
    def _recursor(self, schema, xelem, sparent, ns, pns, is_ref):
        self._scanNSes(xelem, sparent)
        if xelem.name == "xs:attribute":
            return self._parseAttribute(schema, xelem, sparent, pns)
        elif (("ref" in xelem.attrs) or ("type" in xelem.attrs)):
            ref = None
            rns = None
            if "ref" in xelem.attrs:
                name = xelem.attrs["ref"].value()
                ref, rns = self._findRef(schema, name, sparent)
            if ((not ref) and ("type" in xelem.attrs)):
                name = xelem.attrs["type"].value()
                ref, ignore = self._findRef(schema, name, sparent)
            if ref and ref.looped:
                sparent.nsed(pns).children.append(ref)
                return ref
            if (ref and (xelem.name == "xs:element") and not is_ref):
                if "name" in xelem.attrs:
                    name = xelem.attrs["name"].value()
                else:
                    name = ref.attrs["name"].value()
                nsed = NSed(rns, cdata=self._parseRestriction(schema, ref),
                            vtype=self._parseType(ref))
                schild = Elem(name, [nsed], sparent, pns)
                schild.schema = schema
                sparent = schild
            if ref:
                if hasattr(ref, "schema"):
                    schema = ref.schema
                self._recursor_stack.append((ref.attrs["name"].value(), sparent))
                ret = self._recursor(schema, ref, sparent, None, pns, True)
                self._recursor_stack = self._recursor_stack[:-1]
                return ret
            elif "ref" in xelem.attrs:
                return
            elif is_ref:
                return
            else:
                pass
        elif (is_ref):
            ret = None
            for xchild in xelem.children:
                ret1 = self._recursor(schema, xchild, sparent, ns, pns, False)
                if not ret:
                    ret = ret1
            return ret
        elif ((xelem.name != "xs:element") and ("name" not in xelem.attrs)):
            if xelem.name == "xs:choice":
                sparent.vtype = VTYPE_CHOICE
            for xchild in xelem.children:
                self._recursor(schema, xchild, sparent, ns, pns, is_ref)
            return
        name = xelem.attrs["name"].value()
        nsed_ns = None
        if ":" in name:
            xmlns = "xmlns:" + name.split(":")[0]
            if xmlns in xelem.attrs:
                nsed_ns = xelem.attrs[xmlns]
        elif (ns and (ns != "jabber:client")):
            nsed_ns = ns
        elif "xmlns" in xelem.attrs:
            nsed_ns = xelem.attrs["xmlns"]
        nsed = NSed(nsed_ns, cdata=self._parseRestriction(schema, xelem),
                    vtype=self._parseType(xelem))
        schild = Elem(name, [nsed], sparent, pns)
        schild.schema = schema
        if is_ref:
            self._recursor_stack.append((name, schild))
        for xchild in xelem.children:
            # Dont pass on the schema NS after the first element
            self._recursor(schema, xchild, schild, None, ns, False)
        if is_ref:
            self._recursor_stack = self._recursor_stack[:-1]
        return schild
    
    def _scanNSes(self, xelem, sparent):
        for key, val in xelem.attrs.iteritems():
            if key.startswith("xmlns:"):
                sparent.nses[key.replace("xmlns:", "")] = val
    
    def _parseRestriction(self, schema, xelem):
        restriction = xelem.find("xs:restriction", True, ["xs:element",
                                                          "xs:group",
                                                          "xs:attribute"])
        values = []
        if restriction:
            for xchild in restriction.children:
                value = xchild.attrs["value"].value()
                if not len(value):
                    continue
                if xchild.name == "xs:enumeration":
                    values.append(value)
                elif xchild.name == "xs:pattern":
                    values.append(ValuePattern(value))
        return values
    
    def _parseAttribute(self, schema, xelem, selem, ns):
        if (("use" in xelem.attrs) and
            (xelem.attrs["use"].value() == "required")):
            required = True
        else:
            required = False
        if "ref" in xelem.attrs:
            ref, ignore = self._findRef(schema, xelem.attrs["ref"].value(), None)
            sattr = Attr(ref.name, ref.values, required, ref.vtype)
        else:
            sattr = Attr(xelem.nsed(ns).attrs["name"].value(),
                         self._parseRestriction(schema, xelem), required,
                         self._parseType(xelem))
        if selem:
            selem.nsed(ns).attrs[sattr.name] = sattr
        return sattr
    
    def _parseType(self, xelem):
        if "type" in xelem.attrs:
            xtype = xelem.attrs["type"].value()
        else:
            xtype = None
        if xtype in ["xs:token", "xs:string", "xs:anyURI"]:
            return VTYPE_STR
        elif xtype in ["xs:integer", "xs:int"]:
            return VTYPE_INT
        elif xtype in ["xs:unsignedInt", "xs:positiveInteger"]:
            return VTYPE_UINT
        elif xtype in ["xs:decimal"]:
            return VTYPE_FLOAT
        elif xtype in ["xs:boolean"]:
            return VTYPE_BOOL
        else:
            return VTYPE_NONE
    
    def _findRef(self, schema, name, selem):
        last_pelem = None
        for pname, pelem in reversed(self._recursor_stack):
            if pname == name:
                if not pelem:
                    pelem = last_pelem
                if not pelem:
                    return None, None
                pelem.looped = True
                return pelem, None
            if pelem:
                last_pelem = pelem
        try:
            ns, ename = name.split(":")
            xmlns = selem.nses[ns].value()
            return self.nsed_xsd[xmlns][ename], xmlns
        except Exception, e:
            pass
        if name in self.base_syntax:
            return self.base_syntax[name], None
        for xchild in schema.children:
            if (("name" in xchild.attrs) and
                (xchild.attrs["name"].value() == name)):
                return xchild, None
        return None, None
