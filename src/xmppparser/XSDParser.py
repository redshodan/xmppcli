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


import os
from xmppparser import *
from . import stanzas
from .DumbParser import DumbParser


base_syntax = {}
nsed_xsd = {}
required_ns = ["xmppparser:base", "jabber:client"]
_recursor_stack = []

def parseXSDList(home, xsdlist = None):
    if xsdlist:
        xsdlist.extend(required_ns)
    globs = {}
    execfile(os.path.join(home, "xsd", "list.py"), globs)
    for mapping in globs["mappings"]:
        rootname = mapping[0]
        nodename = mapping[1]
        ns = mapping[2]
        if xsdlist and mapping[2] not in xsdlist:
            continue
        filename = os.path.join(home, "xsd", mapping[3])
        parser = parse(filename)
        if rootname:
            path = rootname.split("/")
            root = stanzas[path[0]]
            path = path[1:]
            for part in path:
                root = root.find(part)
        else:
            root = None
        if not isinstance(nodename, list):
            nodename = [nodename]
        for node in nodename:
            generateSyntax(parser, node, ns, root)

def parse(filename):
    parser = DumbParser()
    fp = file(filename)
    parser.parse(fp.read())
    fp.close()
    return parser

def generateSyntax(parser, name, ns, sparent):
    global _recursor_stack
    _recursor_stack = []
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
        if not ns in nsed_xsd:
            nsed_xsd[ns] = {}
        root = None
        for child in elem.children:
            if "name" in child.attrs:
                cname = child.attrs["name"].value()
                nsed_xsd[ns][cname] = child
                if not root and cname == name:
                    root = child
        if not root:
            raise Exception("Invalid XSD spec. Missing root element " + name)

        _scanNSes(schema, root)

        if sparent:
            for schild in sparent.children:
                if schild.name == name:
                    nsed = NSed(ns, vtype=_parseType(root))
                    schild.nsmap[ns] = nsed
                    for child in root.nsed(ns).children:
                        _recursor(schema, child , schild, None, ns, False)
                    return None
        schild = _recursor(schema, root, sparent, ns, None, False)
        if ns == "xmppparser:base":
            base_syntax[schild.name] = schild
        # Store the top level schema on this schema branch
        def _putter(elem, schema):
            elem.schema = schema
            for child in elem.children:
                _putter(child, schema)
        _putter(root, schema)
        if ns == "jabber:client":
            stanzas[schild.name] = schild
        return schild
    else:
        raise Exception("Could not find elem in xsd:", name, ns)

def _recursor(schema, xelem, sparent, ns, pns, is_ref):
    global _recursor_stack
    _scanNSes(xelem, sparent)
    if xelem.name == "xs:attribute":
        return _parseAttribute(schema, xelem, sparent, pns)
    elif (("ref" in xelem.attrs) or ("type" in xelem.attrs)):
        ref = None
        if "ref" in xelem.attrs:
            name = xelem.attrs["ref"].value()
            ref = _findRef(schema, name, sparent)
        if ((not ref) and ("type" in xelem.attrs)):
            name = xelem.attrs["type"].value()
            ref = _findRef(schema, name, sparent)
        if ref and ref.looped:
            sparent.nsed(pns).children.append(ref)
            return ref
        if (ref and (xelem.name == "xs:element") and not is_ref):
            if "name" in xelem.attrs:
                name = xelem.attrs["name"].value()
            else:
                name = ref.attrs["name"].value()
            schild = Elem(name, None, sparent, pns)
            schild.cdata.extend(_parseRestriction(schema, ref))
            schild.schema = schema
            sparent = schild
        if ref:
            if hasattr(ref, "schema"):
                schema = ref.schema
            _recursor_stack.append((ref.attrs["name"].value(), sparent))
            ret = _recursor(schema, ref, sparent, None, pns, True)
            _recursor_stack = _recursor_stack[:-1]
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
            ret1 = _recursor(schema, xchild, sparent, ns, pns, False)
            if not ret:
                ret = ret1
        return ret
    elif ((xelem.name != "xs:element") and ("name" not in xelem.attrs)):
        if xelem.name == "xs:choice":
            sparent.vtype = VTYPE_CHOICE
        for xchild in xelem.children:
            _recursor(schema, xchild, sparent, ns, pns, is_ref)
        return
    if (ns and (ns != "jabber:client")):
        nsed_ns = ns
    elif "xmlns" in xelem.attrs:
        nsed_ns = xelem.attrs["xmlns"]
    else:
        nsed_ns = None
    nsed = NSed(nsed_ns, cdata=_parseRestriction(schema, xelem),
                vtype=_parseType(xelem))
    name = xelem.attrs["name"].value()
    schild = Elem(name, [nsed], sparent, pns)
    schild.schema = schema
    if is_ref:
        _recursor_stack.append((name, schild))
    for xchild in xelem.children:
        # Dont pass on the schema NS after the first element
        _recursor(schema, xchild, schild, None, ns, False)
    if is_ref:
        _recursor_stack = _recursor_stack[:-1]
    return schild

def _scanNSes(xelem, sparent):
    for key, val in xelem.attrs.iteritems():
        if key.startswith("xmlns:"):
            sparent.nses[key.replace("xmlns:", "")] = val

def _parseRestriction(schema, xelem):
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

def _parseAttribute(schema, xelem, selem, ns):
    if (("use" in xelem.attrs) and (xelem.attrs["use"].value() == "required")):
        required = True
    else:
        required = False
    if "ref" in xelem.attrs:
        ref = _findRef(schema, xelem.attrs["ref"].value(), None)
        sattr = Attr(ref.name, ref.values, required, ref.vtype)
    else:
        sattr = Attr(xelem.nsed(ns).attrs["name"].value(),
                     _parseRestriction(schema, xelem), required,
                     _parseType(xelem))
    if selem:
        selem.nsed(ns).attrs[sattr.name] = sattr
    return sattr

def _parseType(xelem):
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

def _findRef(schema, name, selem):
    last_pelem = None
    for pname, pelem in reversed(_recursor_stack):
        if pname == name:
            if not pelem:
                pelem = last_pelem
            if not pelem:
                return None
            pelem.looped = True
            return pelem
        if pelem:
            last_pelem = pelem
    try:
        ns, ename = name.split(":")
        return nsed_xsd[selem.nses[ns].value()][ename]
    except Exception, e:
        pass
    if name in base_syntax:
        return base_syntax[name]
    for xchild in schema.children:
        if (("name" in xchild.attrs) and
            (xchild.attrs["name"].value() == name)):
            return xchild
    return None
