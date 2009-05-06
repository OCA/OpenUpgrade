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


activity_res_form= """<?xml version="1.0"?>
<form string="Activity List">
     <field name="date_start" />
     <field name="date_end" />
     <field name="room_no" />
</form>
"""

activity_res_field= {
    'date_start': {'string':'Start Date','type':'datetime','required': True},
    'date_end': {'string':'End Date','type':'datetime','required': True},
    'room_no': {'string': 'Room No.', 'type': 'many2one', 'relation': 'hotel.room','required':True},
    
}

activity_result_form = """<?xml version="1.0"?>
<form string="Activity List">
    <separator string="Activity List" />
</form>"""

activity_fields = {}

class get_housekeeping_activity_list(wizard.interface):

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form',
                    'arch' : activity_res_form,
                    'fields' : activity_res_field,
                    'state' : [('print_activity_list','Activity List'),('end', 'Cancel')]}
        },
        'print_activity_list': {
            'action' : [],
            'result' : {'type' : 'print',
                    'report':'activity.detail',
                    'state' : 'end'}             
        },    
    
       
    }
get_housekeeping_activity_list("hotel.housekeeping.activity_list")     

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
