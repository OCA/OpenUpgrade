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
import pooler

class wizard_account_chart(wizard.interface):
    _account_chart_arch = '''<?xml version="1.0"?>
    <form string="Account charts">
        <field name="fiscalyear"/>
        <field name="target_move"/>
        <separator string="Simulations" colspan="4"/>
        <field name="states" colspan="4" nolabel="1"/>
    </form>'''

    _account_chart_fields = {
        'fiscalyear': {'string': 'Fiscal year', 'type':'many2one','relation': 'account.fiscalyear', 'required': True },
        'states': {'string':'States', 'type':'many2many', 'relation':'account.journal.simulation'},
        'target_move':{'string': 'Target Moves', 'type': 'selection', 'selection': [('all','All Entries'),('posted_only','All Posted Entries')], 'required': True, 'default': lambda *a:"all"},
    }

    def _get_defaults(self, cr, uid, data, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
        return data['form']


    def _account_chart_open_window(self, cr, uid, data, context):
        pool = pooler.get_pool(cr.dbname)
        mod_obj = pool.get('ir.model.data')
        act_obj = pool.get('ir.actions.act_window')

        result = mod_obj._get_id(cr, uid, 'account', 'action_account_tree')
        id = mod_obj.read(cr, uid, [result], ['res_id'])[0]['res_id']
        result = act_obj.read(cr, uid, [id])[0]

        ctx = {'fiscalyear': data['form']['fiscalyear'], 'target_move':data['form']['target_move']}

        if data['form']['states']:
            ctx['journal_state']=[]
            sim_obj = pooler.get_pool(cr.dbname).get('account.journal.simulation')
            for a in sim_obj.read(cr, uid, data['form']['states'][0][2], ['code'], context):
                ctx['journal_state'].append(a['code'])
        result['context'] = str(ctx)
        return result

    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type': 'form', 'arch':_account_chart_arch, 'fields':_account_chart_fields, 'state': [('end', 'Cancel'), ('open', 'Open Charts')]}
        },
        'open': {
            'actions': [],
            'result': {'type': 'action', 'action':_account_chart_open_window, 'state':'end'}
        }
    }
wizard_account_chart('account.simulation.chart')
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

