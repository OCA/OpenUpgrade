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

from turbogears import view
from erpcomparator import rpc

def tg_query(*args, **kw):
    """Returns url querrystring from the provided arguments...
    for example:

    >>> print tg_query('/graph', 'pie', width=100, height=100)
    >>> "/graph/pie?width=100&height=100"

    """
    result = []
    for k, v in kw.items():
        result += ['%s=%s'%(k, v)]

    url = '/'.join([ustr(a) for a in args])
    return ((url or '') and url + '?') + '&'.join(result)

def add_root_vars(root_vars):
    return root_vars.update({'rpc': rpc})

def add_vars(vars):
    from cherrypy import root

    std_vars = {
        'root': root,
        'query': tg_query
    }

    return vars.update(std_vars)

view.root_variable_providers.append(add_root_vars)
view.variable_providers.append(add_vars)

# vim: ts=4 sts=4 sw=4 si et

