# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 Zikzakmedia SL (http://www.zikzakmedia.com) All Rights Reserved.
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

import time
import wizard

dates_form = '''<?xml version="1.0" encoding="utf-8"?>
<form string="Select period">
    <field name="d_from"/>
    <field name="d_to"/>
    <field name="channel_id"/>
</form>'''

dates_fields = {
    'd_from': {'string': 'Start', 'type':'date', 'required':True, 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'd_to':  {'string': 'End', 'type':'date', 'default': lambda *a: time.strftime('%Y-%m-%d')},
    'channel_id': {'string': 'Channel', 'type': 'many2one', 'relation':'radiotv.channel', 'required':True},
}

class wizard_broadcast_declaration_report(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('report','Print')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'radiotv.broadcast.declaration.report', 'state':'end'}
        }
    }
wizard_broadcast_declaration_report('radiotv.broadcast.declaration.report')
