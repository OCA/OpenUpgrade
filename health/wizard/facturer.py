# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2007 E.V.I.. (http://www.vernichon.fr) All Rights Reserved.
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
import datetime
import time
facturer_form = '''<?xml version="1.0"?>
<form string="Charge">
    <field name="period_id"/>
    </form>'''

facturer_fields = {
        'period_id':  {'string':'Period', 'type':'many2one', 'relation': 'account.period', 'required':True},
}


def _init(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    period_obj = pool.get('account.period')
    data['form']['period_id'] = period_obj.find(cr, uid)[0]
    return data['form']


def _facturer(self, cr, uid, data, context):
    pool = pooler.get_pool(cr.dbname)
    resident = pooler.get_pool(cr.dbname).get('health.facturation')
    resident.facturer(cr,uid,data['ids'])
    return{}


class wizard_facturer(wizard.interface):
    states = {
        'init': {
            'actions': [_init],
            'result': {'type':'form', 'arch':facturer_form, 'fields':facturer_fields, 'state':[('end','Cancel'),('facturer','Charge')]}
        },
        'facturer': {
            'actions': [_facturer],
            'result': {'type' : 'state', 'state': 'end'}

            }
    }
wizard_facturer('facturation')
