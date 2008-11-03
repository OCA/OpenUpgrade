# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2008 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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

