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
import time
import mx.DateTime

dates_form = '''<?xml version="1.0"?>
<form string="Select period">
    <field name="fiscalyear" colspan="4"/>
    <!--field name="periods" colspan="4"/-->
    <field name="date1"/>
    <field name="date2"/>
</form>'''

dates_fields = {
    'fiscalyear': {'string': 'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear',
        'help': 'Keep empty for all open fiscal year'},
    #'periods': {'string': 'Periods', 'type': 'many2many', 'relation': 'account.period', 'help': 'All periods if empty'},
    'date1': {'string':'Start of period', 'type':'date', 'required':True},
    'date2': {'string':'End of period', 'type':'date', 'required':True},
}

class GeneralLedger(wizard.interface):
    def _get_defaults(self, cr, uid, data, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
        data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
        context['fiscalyear']= fiscalyear_obj.find(cr, uid)
        year_start_date = fiscalyear_obj.browse(cr, uid, context['fiscalyear'] ).date_start
        year_end_date = fiscalyear_obj.browse(cr, uid, context['fiscalyear'] ).date_stop 
        data['form']['date1'] =  mx.DateTime.strptime(year_start_date,"%Y-%m-%d").strftime("%Y-%m-%d")
        data['form']['date2'] =  mx.DateTime.strptime(year_end_date,"%Y-%m-%d").strftime("%Y-%m-%d")
        return data['form']

    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('report','Print')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'account.general.ledger.custom.print', 'state':'end'}
        }
    }
GeneralLedger('account.general.ledger.report.custom')

