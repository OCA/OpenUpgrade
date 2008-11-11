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
import time
import datetime
import pooler

model_form = """<?xml version="1.0"?>
<form string="Select Message">
    <field name="model"/>
</form>"""

model_fields = {
    'model': {'string': 'Account Model', 'type': 'many2many', 'relation': 'account.model', 'required': False},
   }

form = """<?xml version="1.0"?>
<form string="Use Model">
    <label string="Move Lines Created"/>
</form>
"""
fields = {
          }
def _create_entries(self, cr, uid, data, context):
    pool_obj = pooler.get_pool(cr.dbname)
    model_ids = data['form']['model'][0][2]
    data_model = pool_obj.get('account.model').browse(cr,uid,model_ids)
    move_ids = []
    for model in data_model:
            period_id = pool_obj.get('account.period').find(cr,uid, context=context)
            if not period_id:
                raise wizard.except_wizard('No period found !', 'Unable to find a valid period !')
            period_id = period_id[0]
            name = model.name
            if model.journal_id.sequence_id:
                name = pool_obj.get('ir.sequence').get_id(cr, uid, model.journal_id.sequence_id.id)
            move_id = pool_obj.get('account.move').create(cr, uid, {
                'name': name,
                'ref': model.ref,
                'period_id': period_id,
                'journal_id': model.journal_id.id,
            })
            move_ids.append(move_id)
            for line in model.lines_id:
                val = {
                    'move_id': move_id,
                    'journal_id': model.journal_id.id,
                    'period_id': period_id
                }
                val.update({
                    'name': line.name,
                    'quantity': line.quantity,
                    'debit': line.debit,
                    'credit': line.credit,
                    'account_id': line.account_id.id,
                    'move_id': move_id,
                    'ref': line.ref,
                    'partner_id': line.partner_id.id,
                    'date': time.strftime('%Y-%m-%d'),
                    'date_maturity': time.strftime('%Y-%m-%d')
                })
                c = context.copy()
                c.update({'journal_id': model.journal_id.id,'period_id': period_id})
                id_line = pool_obj.get('account.move.line').create(cr, uid, val, context=c)
    if not move_ids:
        raise wizard.except_wizard('Error', 'You should enter atleast one Account Model!')
    return {}

class use_model(wizard.interface):
    states = {
        'init': {
            'actions': [],
            'result': {'type':'form', 'arch':model_form, 'fields':model_fields, 'state':[('end','Cancel'),('create','Create Entries')]},
        },
        'create': {
            'actions': [_create_entries],
            'result': {'type': 'form','arch':form, 'fields':fields, 'state':[('end','Ok')]}
        },
    }

use_model("cci_use_model")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

