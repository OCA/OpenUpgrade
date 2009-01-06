###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# The OpenERP web client is distributed under the "OpenERP Public License".
# It's based on Mozilla Public License Version (MPL) 1.1 with following 
# restrictions:
#
# -   All names, links and logos of Tiny, Open ERP and Axelor must be 
#     kept as in original distribution without any changes in all software 
#     screens, especially in start-up page and the software header, even if 
#     the application source code has been changed or updated or code has been 
#     added.
#
# -   All distributions of the software must keep source code with OEPL.
# 
# -   All integrations to any other software must keep source code with OEPL.
#
# If you need commercial licence to remove this kind of restriction please
# contact us.
#
# You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
#
###############################################################################

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

