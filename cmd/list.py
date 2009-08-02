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

###
### Mapping of xsd into complete syntax hierarchy. Order is important. The
### most used elements MUST be before ones that depend upon them.
###
### [root_name, node_name, node_ns, file_name, mapped-to-ns]
###

from xmppparser import HList


mappings = \
[
    ### Basic xsd types
    [None, "xml:lang", "xmppparser:base", "xmppparser-base.xsd"],

    # presence
    [None, "presence", "jabber:client", "cmds.xsd"],
    [None, "available", "jabber:client", "cmds.xsd"],
    [None, "away", "jabber:client", "cmds.xsd"],
    [None, "xa", "jabber:client", "cmds.xsd"],
    [None, "dnd", "jabber:client", "cmds.xsd"],
    [None, "unavailable", "jabber:client", "cmds.xsd"],
    [None, "subscribe", "jabber:client", "cmds.xsd"],

    # Roster
    [None, "roster", "jabber:client", "cmds.xsd"],

]
