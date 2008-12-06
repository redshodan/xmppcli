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

from xmppcli.parser import Attr, NSed, Elem

stanza_error = Elem("error",
                    [NSed(None, [Attr("code"),
                                 Attr("type", ["auth", "cancel", "continue",
                                               "modify", "wait"])])])
iq_privacy = \
NSed('jabber:iq:privacy', None, None,
     [Elem("active", [NSed(None, [Attr("name")])]),
      Elem("default", [NSed(None, [Attr("name")])]),
      Elem("list",
           [NSed(None, None, None,
                 [Elem("item",
                       [NSed(None,
                             [Attr("action", ["allow", "deny"]),
                              Attr("type", ["group", "jid", "subscription"]),
                              Attr("value")],
                             [],
                             [Elem("iq"), Elem("message"),
                              Elem("presence-in"),
                              Elem("presence-out")])])])])])

stanzas = \
{
    "presence" : \
    Elem("presence",
         [NSed(None,
               [Attr("to"), Attr("from"), Attr("xmlns"), Attr("xml:lang"),
                Attr("type", ["error", "probe", "subscribe", "subscribed",
                              "unsubscribe", "unsubscribed"])],
               [],
               [Elem("show", [NSed(None, None, ["away", "chat", "dnd", "xa"])]),
                Elem("status"),
                Elem("priority"),
                stanza_error])]),
    "message" : \
    Elem("message",
         [NSed(None,
               [Attr("to"), Attr("from"), Attr("xmlns"), Attr("id"),
                Attr("xml:lang"),
                Attr("type", ["chat", "error", "groupchat", "headline",
                              "normal"])],
               [],
               [Elem("thread"),
                Elem("subject", [NSed(None, [Attr("xml:lang")])]),
                Elem("body", [NSed(None, [Attr("xml:lang")])]),
                Elem("x", [NSed(None, [Attr("xmlns")])]),
                stanza_error])]),
    "iq" : \
    Elem("iq",
         [NSed(None,
               [Attr("to"), Attr("from"), Attr("xmlns"), Attr("id"),
                Attr("xml:lang"),
                Attr("type", ["error", "get", "result", "set"])],
               [],
               [Elem("query",
                     [NSed(None, [Attr("xmlns")]),
                      iq_privacy]),
                stanza_error])])
}


