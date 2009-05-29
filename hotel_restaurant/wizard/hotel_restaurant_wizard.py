# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
            'actions' : [],
            'result' : {'type' : 'action',
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


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: