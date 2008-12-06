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


import os
from xmppcli.parser import *
from . import stanzas
from .DumbParser import DumbParser


base_syntax = {}


def parseXSDList(home):
    globs = {}
    execfile(os.path.join(home, "xsd", "list.py"), globs)
    for mapping in globs["mappings"]:
        filename = os.path.join(home, "xsd", mapping[3])
        rootname = mapping[0]
        nodename = mapping[1]
        patchin = False
        ns = mapping[2]
        parser = parse(filename)
        if rootname:
            path = rootname.split("/")
            root = stanzas[path[0]]
            path = path[1:]
            for part in path:
                root = root.find(part)
        else:
            root = None
        generateSyntax(parser, nodename, ns, root)

def parse(filename):
    parser = DumbParser()
    fp = file(filename)
    parser.parse(fp.read())
    fp.close()
    return parser

def generateSyntax(parser, name, ns, sparent):
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

        root = None
        elems = {}
        for child in elem.children:
            elems[child.name] = child
            if (((child.name == "xs:element") or
                 (child.name == "xs:attribute")) and
                (child.attrs["name"].value() == name)):
                root = child
        if not root:
            raise Exception("Invalid XSD spec. Missing root element " + name)

        if sparent:
            for schild in sparent.children:
                if schild.name == name:
                    nsed = NSed(ns, [Attr("xmlns", [ns])],
                                vtype=_parseType(root))
                    schild.nsmap[ns] = nsed
                    for child in root.nsed(ns).children:
                        _recursor(schema, child , schild, ns)
                    return None
        schild = _recursor(schema, root, sparent, ns)
        if isinstance(schild, Elem):
            schild.nsed(ns).attrs["xmlns"] = Attr("xmlns", [ns])
        if ns == "xmppcli:base":
            base_syntax[schild.name] = schild
        elif not sparent:
            stanzas[schild.name] = schild
        return schild
    else:
        raise Exception("Could not find elem in xsd:", name, ns)

def _recursor(schema, xelem, sparent, ns):
    if xelem.name == "xs:attribute":
        return _parseAttribute(schema, xelem, sparent, ns)
    elif "ref" in xelem.attrs:
        name = xelem.attrs["ref"].value()
        ref = _findRef(schema, name)
        if ref:
            return _recursor(schema, ref, sparent, ns)
    elif ((xelem.name != "xs:element") or ("name" not in xelem.attrs)):
        for xchild in xelem.children:
            _recursor(schema, xchild, sparent, ns)
    else:
        schild = Elem(xelem.attrs["name"].value(), parent=sparent, ns=ns)
        schild.nsed(ns).vtype = _parseType(xelem)
        schild.nsed(ns).cdata = _parseRestriction(schema, xelem)
        for xchild in xelem.children:
            _recursor(schema, xchild, schild, ns)
        return schild

def _parseRestriction(schema, xelem):
    restriction = xelem.find("xs:restriction", True, ["xs:element",
                                                      "xs:attribute"])
    values = []
    if restriction:
        for xchild in restriction.children:
            values.append(xchild.attrs["value"].value())
    return values

def _parseAttribute(schema, xelem, selem, ns):
    if (("use" in xelem.attrs) and (xelem.attrs["use"].value() == "required")):
        required = True
    else:
        required = False
    if "ref" in xelem.attrs:
        ref = _findRef(schema, xelem.attrs["ref"].values[0])
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
    elif xtype in ["xs:integer"]:
        return VTYPE_INT
    elif xtype in ["xs:unsignedInt", "xs:positiveInteger"]:
        return VTYPE_UINT
    elif xtype in ["xs:boolean"]:
        return VTYPE_BOOL
    else:
        return VTYPE_NONE

def _findRef(schema, name):
    if name in base_syntax:
        return base_syntax[name]
    for xchild in schema.children:
        if (("name" in xchild.attrs) and
            (xchild.attrs["name"].value() == name)):
            return xchild
    return None
