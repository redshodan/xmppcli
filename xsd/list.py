###
### Mapping of xsd into complete syntax hierarchy. Order is important. The
### most used elements MUST be before ones that depend upon them.
###
### [root_name, node_name, node_ns, file_name]
###

mappings = \
[
    ### Basic xsd types
    [None, "xml:lang", "xmppcli:base", "xmppcli-base.xsd"],

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

    ### XEP-0050
    ["iq", "command", "http://jabber.org/protocol/commands", "XEP-0050.xsd"],
    ### XEP-0004, depends upon XEP-0050
    ["iq/command", "x", "jabber:x:data", "XEP-0004.xsd"],
]
