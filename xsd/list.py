###
### Mapping of xsd into complete syntax hierarchy. Order is important. The
### most used elements MUST be before ones that depend upon them.
###
### [root_name, node_name, node_ns]
###
mappings = \
[
    [None, "xml:lang", "xmppcli:base"],
    [None, "presence", "jabber:client"],
    [None, "message", "jabber:client"],
    [None, "iq", "jabber:client"],
    ["iq", "query", "jabber:iq:privacy"],
    ["iq", "query", "jabber:iq:roster"],
]
