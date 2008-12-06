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
from . import syntax
from .DumbParser import DumbParser


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
        path = rootname.split("/")
        root = syntax.stanzas[path[0]]
        path = path[1:]
        for part in path:
            root = root.find(part)
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
            if ((child.name == "xs:element") and
                (child.attrs["name"].value() == name)):
                root = child
        if not root:
            raise Exception("Invalid XSD spec. Missing root element " + name)

        for schild in sparent.children:
            if schild.name == name:
                nsed = NSed(ns, [Attr("xmlns", [ns])], vtype=_parseType(root))
                schild.nsmap[ns] = nsed
                for child in root.nsed(ns).children:
                    _recursor(schema, root, schild)
                return
        else:
            schild = _recursor(schema, root, sparent)
            schild.attrs["xmlns"] = Attr("xmlns", [ns])
            return

def _recursor(schema, xelem, sparent):
    if xelem.name == "xs:attribute":
        _parseAttribute(schema, xelem, sparent)
    elif "ref" in xelem.attrs:
        name = xelem.attrs["ref"].value()
        for xchild in schema.children:
            if (("name" in xchild.attrs) and
                (xchild.attrs["name"].value() == name)):
                _recursor(schema, xchild, sparent)
                return
    elif ((xelem.name != "xs:element") or ("name" not in xelem.attrs)):
        for xchild in xelem.children:
            _recursor(schema, xchild, sparent)
    else:
        schild = Elem(xelem.attrs["name"].value(), parent = sparent)
        schild.nsed().vtype = _parseType(xelem)
        for xchild in xelem.children:
            _recursor(schema, xchild, schild)
        return schild

def _parseAttribute(schema, xelem, selem):
    if len(xelem.children):
        xchild = xelem.find("xs:simpleType")
        if xchild:
            xchild = xchild.find("xs:restriction")
    else:
        xchild = xelem
    if (("use" in xelem.attrs) and (xelem.attrs["use"].value() == "required")):
        required = True
    else:
        required = False
    sattr = Attr(xelem.attrs["name"].value(), None, required, _parseType(xelem))
    for xchild in xchild.children:
        sattr.values.append(xchild.attrs["value"].value())
    selem.attrs[sattr.name] = sattr

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
