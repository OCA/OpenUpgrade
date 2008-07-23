# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: make_invoice.py 1070 2005-07-29 12:41:24Z nicoe $
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
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
#
##############################################################################

import wizard
import netsvc
import pooler

from osv import fields, osv
form = """<?xml version="1.0"?>
<form string="Copy Events">
    <field name="nbr_event"/>
</form>
"""
fields = {
      'nbr_event': {'string':'Event Copied', 'type':'char', 'readonly':True},
          }

def _makecopy(self, cr, uid, data, context):
    pool_obj=pooler.get_pool(cr.dbname)
    obj_event=pool_obj.get('event.event')
    count = 0
    for id in data['ids']:
        count = count + 1
        obj_event.copy(cr, uid, id)
    return {'nbr_event' : str(count)}

class event_copy(wizard.interface):
    states = {
        'init' : {
               'actions' : [_makecopy],
               'result': {'type': 'form', 'arch': form, 'fields': fields, 'state':[('end','Ok')]}
            },
    }
event_copy("event.event_copy")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

