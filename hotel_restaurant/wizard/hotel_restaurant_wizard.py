##############################################################################
#
# Copyright (c) 2005-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
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
from osv import fields
from osv import osv
import time
import ir
from mx import DateTime
import datetime
import pooler
from tools import config
import wizard
import netsvc
import pooler

kot_form = """<?xml version="1.0"?>
<form string="Create Kot">
    <separator colspan="4" string="Do you really want to create the Kot?" />
    <field name="grouped" />
</form>
"""
kot_fields = {
    'grouped' : {'string':'Group the kots', 'type':'boolean', 'default': lambda x,y,z: False}
}

ack_form = """<?xml version="1.0"?>
<form string="Create Kots">
    <separator string="Kots created" />
</form>"""

ack_fields = {}

res_form= """<?xml version="1.0"?>
<form string="Reservation List">
     <field name="date_start" />
     <field name="date_end" />
</form>
"""

res_field= {
    'date_start': {'string':'Start Date','type':'datetime','required': True},
    'date_end': {'string':'End Date','type':'datetime','required': True},

}

result_form = """<?xml version="1.0"?>
<form string="Create Kots">
    <separator string="Reservation List" />
</form>"""

result_fields = {}



def _makeKot(self, cr, uid, data, context):


#    order_obj = pooler.get_pool(cr.dbname).get('hotel.reservation')
#    newinv = []
#    for o in order_obj.browse(cr, uid, data['ids'], context):
#        for i in o.folio_id:
#           newinv.append(i.id)
#    return {
#        'domain': "[('id','in', ["+','.join(map(str,newinv))+"])]",
#        'name': 'Folios',
#        'view_type': 'form',
#        'view_mode': 'tree,form',
#        'res_model': 'hotel_reservation.folio',
#        'view_id': False,
#        'type': 'ir.actions.act_window'
#
#    }
    return {}

class make_kot(wizard.interface):
    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : kot_form,
                    'fields' : kot_fields,
                    'state' : [('end', 'Cancel'),('kot', 'Create Kots') ]}
        },
        'kot' : {
            'actions' : [_makeKot],
            'result' : {'type' : 'action',
                    'action' : _makeKot,
                    'state' : 'end'}
        },
    }
make_kot("hotel.kot.make_kot")

class get_reservation_list(wizard.interface):

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : res_form,
                    'fields' : res_field,
                    'state' : [('end', 'Cancel'),('print_report', 'Reservation List') ]}
        },
        'print_report' : {
            'actions' : [],
            'result' : {'type' : 'print',
                    'report':'hotel.table.res',
                    'state' : 'end'}
        },
    }
get_reservation_list("hotel.table.reservation")