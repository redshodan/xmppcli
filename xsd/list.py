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

    ### RFC 3920
    [None, ["empty", "stanzaErrorGroup", "text"],
     "urn:ietf:params:xml:ns:xmpp-stanzas", "RFC-3920-stanza-error.xsd"],

    ### RFC 3921
    # Core stanzas
    [None, "presence", "jabber:client", "RFC-3921-client.xsd"],
    [None, "message", "jabber:client", "RFC-3921-client.xsd"],
    [None, "iq", "jabber:client", "RFC-3921-client.xsd"],
    # Core IQ types
    [["iq"], "query", "jabber:iq:privacy", "RFC-3921-iq-privacy.xsd"],
    [["iq"], "query", "jabber:iq:roster", "RFC-3921-iq-roster.xsd"],

    ### XEP-0004
    [None, "x", "jabber:x:data", "XEP-0004.xsd"],
    ### XEP-0009
    [["iq"], "query", "jabber:iq:rpc", "XEP-0009.xsd"],
    ### XEP-0012
    [["iq"], "query", "jabber:iq:last", "XEP-0012.xsd"],
    ### XEP-0013
    [["iq"], "offline", "http://jabber.org/protocol/offline", "XEP-0013.xsd"],
    [["message"], "offline", "http://jabber.org/protocol/offline",
     "XEP-0013.xsd"],
    ### XEP-0016 -- handled by RFC3921-iq-privacy
    ### XEP-0020
    [["iq"], "feature", "http://jabber.org/protocol/feature-neg",
     "XEP-0020.xsd"],
    ### XEP-0027
    [["message"], "x", "jabber:x:encrypted", "XEP-0027-encrypted.xsd"],
    [["message"], "x", "jabber:x:signed", "XEP-0027-signed.xsd"],
    ### XEP-0030
    [["iq"], "query", "http://jabber.org/protocol/disco#info",
     "XEP-0030-disco-info.xsd"],
    [["iq"], "query", "http://jabber.org/protocol/disco#items",
     "XEP-0030-disco-items.xsd"],
    ### XEP-0033
    [["message"], "addresses", "http://jabber.org/protocol/address",
     "XEP-0033.xsd"],
    ### XEP-0045
    [["presence"], "x", "http://jabber.org/protocol/muc", "XEP-0045.xsd"],
    [["presence"], "x", "http://jabber.org/protocol/muc#user",
     "XEP-0045-user.xsd"],
    [["message"], "x", "http://jabber.org/protocol/muc#user",
     "XEP-0045-user.xsd"],
    [["iq"], "query", "http://jabber.org/protocol/muc#admin",
     "XEP-0045-admin.xsd"],
    [["iq"], "query", "http://jabber.org/protocol/muc#owner",
     "XEP-0045-owner.xsd"],
    [["iq"], "unique", "http://jabber.org/protocol/muc#unique",
     "XEP-0045-unique.xsd"],
    ### XEP-0047 - TBD: tie in 79
    [["iq"], ["open", "close"], "http://jabber.org/protocol/ibb",
     "XEP-0047.xsd"],
    [["iq"], "data", "http://jabber.org/protocol/ibb", "XEP-0047.xsd"],
    [["message"], "data", "http://jabber.org/protocol/ibb", "XEP-0047.xsd"],
    ### XEP-0048 - TBD: tie in to ??
    ### XEP-0049
    [["iq"], "query", "jabber:iq:private", "XEP-0049.xsd"],
    ### XEP-0050
    [["iq"], "command", "http://jabber.org/protocol/commands", "XEP-0050.xsd"],
    ### XEP-0054 - TBD: Need to convert DTD to XSD
    ### XEP-0055
    [["iq"], "query", "jabber:iq:search", "XEP-0055.xsd"],
    ### XEP-0059
    [["iq", ["query", "http://jabber.org/protocol/disco#items"]],
     "set", "http://jabber.org/protocol/rsm", "XEP-0059.xsd"],
    [["iq", ["query", "jabber:iq:search"]],
     "set", "http://jabber.org/protocol/rsm", "XEP-0059.xsd"],
    ### XEP-0060
    [None, None, "http://jabber.org/protocol/pubsub#errors",
     "XEP-0060-errors.xsd"],
    [["iq"], "error", "jabber:client", "XEP-0060-error-elem.xsd"],
    [["iq"], "pubsub", "http://jabber.org/protocol/pubsub", "XEP-0060.xsd"],
    [["iq"], "pubsub", "http://jabber.org/protocol/pubsub#owner",
     "XEP-0060-owner.xsd"],
    [["message"], "event", "http://jabber.org/protocol/pubsub#event",
     "XEP-0060-event.xsd"],
    ### XEP-0065
    [["iq"], "query", "http://jabber.org/protocol/bytestreams", "XEP-0065.xsd"],
    [["message"], "udpsuccess", "http://jabber.org/protocol/bytestreams",
     "XEP-0065.xsd"],
    ### XEP-0066
    [["iq"], "query", "jabber:iq:oob", "XEP-0066-iq-oob.xsd"],
    [["message"], "x", "jabber:x:oob", "XEP-0066-x-oob.xsd"],
    ### XEP-0070
    [["iq"], "confirm", "http://jabber.org/protocol/http-auth", "XEP-0070.xsd"],
    [["message"], "confirm", "http://jabber.org/protocol/http-auth",
     "XEP-0070.xsd"],
    ### XEP-0071 - TBD: ugh, a tad bit complex
    ### XEP-0072 - TBD: get the soap xsd when I have network
    ### XEP-0077 - Ignoring since its part of stream setup
    ### XEP-0079
    [None, None, "http://jabber.org/protocol/amp#errors",
     "XEP-0079-errors.xsd"],
    [["message"], "amp", "http://jabber.org/protocol/amp", "XEP-0079.xsd"],
    [["iq"], "error", "jabber:client", "XEP-0079-error-elem.xsd"],
    ### XEP-0080
    [["iq",
      ["pubsub", "http://jabber.org/protocol/pubsub"],
      ["publish", HList("node", "http://jabber.org/protocol/geoloc")],
      "item"],
     "geoloc", "http://jabber.org/protocol/geoloc", "XEP-0080.xsd"],
]
