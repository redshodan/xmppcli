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
### A list of protocol fillers to enable for tab completion
###

### [category, type]
disco_identies = \
[
    ### XEP-0072
    ["automation", "soap"],
    ### XEP-0094
    ["gateway", "aim"], ["gateway", "msn"], ["gateway", "yahoo"],
]

disco_features = \
[
    ### XEP-0054
    "vcard-temp",
    ### XEP-0066
    "jabber:iq:oob", "jabber:x:oob",
    ### XEP-0072
    "http://jabber.org/protocol/soap",
    ### XEP-0079
    "http://jabber.org/protocol/amp",
    ### XEP-0084
    "urn:xmpp:avatar:data", "urn:xmpp:avatar:metadata",
    ### XEP-0085
    "http://jabber.org/protocol/chatstates",
    ### XEP-0092
    "jabber:iq:version",
    ### XEP-0094
    "jabber:iq:agents",
    ### XEP-0095
    "http://jabber.org/protocol/si",
    "http://jabber.org/protocol/si/profile/file-transfer",
    ### XEP-0115
    "http://jabber.org/protocol/caps",
    ### XEP-0154
    "urn:xmpp:tmp:profile",
]

feature_neg = \
[
    ### XEP-0047
    "http://jabber.org/protocol/ibb",
    ### XEP-0065
    "http://jabber.org/protocol/bytestreams",
    ### XEP-0066
    "jabber:iq:oob",
]

pubsub_nodes = \
[
    ### XEP-0084
    "urn:xmpp:avatar:data", "urn:xmpp:avatar:metadata",
]
