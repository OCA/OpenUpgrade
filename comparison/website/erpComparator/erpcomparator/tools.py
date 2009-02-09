
import os
import time
import datetime as DT

# xpath module replaces __builtins__['_'], which breaks TG i18n
import turbogears
turbogears.i18n.tg_gettext.install()

import turbogears as tg

from erpcomparator import rpc

def expr_eval(string, context={}):
    context['uid'] = rpc.session.uid
    if isinstance(string, basestring):
        string = string.replace("'active_id'", "active_id")
        return eval(string, context)
    else:
        return string

def node_attributes(node):
    result = {}
    attrs = node.attributes
    if attrs is None:
        return {}
    for i in range(attrs.length):
        result[attrs.item(i).localName] = attrs.item(i).nodeValue
    return result
    
# vim: ts=4 sts=4 sw=4 si et

