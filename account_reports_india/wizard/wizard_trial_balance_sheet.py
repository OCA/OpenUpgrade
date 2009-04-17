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

import wizard
import pooler
import time
import mx.DateTime

dates_form = '''<?xml version="1.0"?>
<form string="Select period">
    <field name="company_id" colspan="4"/>
    <newline/>
    <field name="fiscalyear" colspan="4"/>
    <newline/>
    <field name="empty_account" colspan="2"/>
    <newline/>
    <field name="date_from" colspan="4"/>
    <field name="date_to" colspan="4"/>
</form>'''

dates_fields = {
    'company_id': {'string': 'Company', 'type': 'many2one', 'relation': 'res.company', 'required': True},
    'fiscalyear': {'string': 'Fiscal year', 'type': 'many2one', 'relation': 'account.fiscalyear',
        'help': 'Keep empty for all open fiscal year'},
    'empty_account':{'string':'Include Empty Account:', 'type':'boolean'},
    'date_from': {'string':"Start date",'type':'date','required':True},
    'date_to': {'string':"End date",'type':'date','required':True},
}

class wizard_trial_balance(wizard.interface):
    def _get_defaults(self, cr, uid, data, context):
        fiscalyear_obj = pooler.get_pool(cr.dbname).get('account.fiscalyear')
        data['form']['fiscalyear'] = fiscalyear_obj.find(cr, uid)
        year_start_date = fiscalyear_obj.browse(cr, uid, data['form']['fiscalyear'] ).date_start
        year_end_date = fiscalyear_obj.browse(cr, uid, data['form']['fiscalyear'] ).date_stop
        data['form']['date_from'] =  mx.DateTime.strptime(year_start_date,"%Y-%m-%d").strftime("%Y-%m-%d")
        data['form']['date_to'] =  mx.DateTime.strptime(year_end_date,"%Y-%m-%d").strftime("%Y-%m-%d")
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id:
            company_id = user.company_id.id
        else:
            company_id = pooler.get_pool(cr.dbname).get('res.company').search(cr, uid, [('parent_id', '=', False)])[0]
        data['form']['company_id'] = company_id
        
        # to process company IDS
        user = pooler.get_pool(cr.dbname).get('res.users').browse(cr, uid, uid, context=context)
        company_ids = pooler.get_pool(cr.dbname).get('res.company')._get_company_children(cr, uid, user.company_id.id)
        dates_fields['company_id']['domain'] = "[('id','in',"+str(company_ids) +")]" 
        return data['form']
       
    states = {
        'init': {
            'actions': [_get_defaults],
            'result': {'type':'form', 'arch':dates_form, 'fields':dates_fields, 'state':[('end','Cancel'),('report','Print')]}
        },
        'report': {
            'actions': [],
            'result': {'type':'print', 'report':'trial.balance.sheet', 'state':'end'}
        }}
wizard_trial_balance('trial.balance.sheet.report')
