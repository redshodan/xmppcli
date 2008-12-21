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
### [root_name, node_name, node_ns, file_name]
###

mappings = \
[
    ### Basic xsd types
    [None, "xml:lang", "xmppparser:base", "xmppparser-base.xsd"],

    ### RFC 3921
    # Core stanzas
    [None, "presence", "jabber:client", "RFC-3921-client.xsd"],
    [None, "message", "jabber:client", "RFC-3921-client.xsd"],
    [None, "iq", "jabber:client", "RFC-3921-client.xsd"],
    # Core IQ types
    ["iq", "query", "jabber:iq:privacy", "RFC-3921-iq-privacy.xsd"],
    ["iq", "query", "jabber:iq:roster", "RFC-3921-iq-roster.xsd"],

    ### XEP-0009
    ["iq", "query", "jabber:iq:rpc", "XEP-0009.xsd"],
    ### XEP-0012
    ["iq", "query", "jabber:iq:last", "XEP-0012.xsd"],
    ### XEP-0013
    ["iq", "offline", "http://jabber.org/protocol/offline", "XEP-0013.xsd"],
    ["message", "offline", "http://jabber.org/protocol/offline",
     "XEP-0013.xsd"],

    ### XEP-0016 -- handled by RFC3921-iq-privacy

    ### XEP-0020
    ["iq", "feature", "http://jabber.org/protocol/feature-neg", "XEP-0020.xsd"],

    ### XEP-0050
    ["iq", "command", "http://jabber.org/protocol/commands", "XEP-0050.xsd"],
    ### XEP-0004, depends upon XEP-0050
    ["iq/command", "x", "jabber:x:data", "XEP-0004.xsd"],
]
