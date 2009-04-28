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
