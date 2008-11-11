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
import netsvc
import pooler
import time
import datetime

form_journal = """<?xml version="1.0"?>
<form string="Select Journal">
    <field name="journal" />
</form>
"""
fields_journal = {
    'journal': {'string':'Cash Type', 'type':'many2one', 'relation':'account.journal' ,'required':True,'domain' :[('type', '=', 'cash')]},
}

form_notify = """<?xml version="1.0"?>
<form string="Notification">
    <field name="message" nolabel="1" width="300"/>
</form>
"""
fields_notify = {
    'message': {'string':'', 'type':'text', 'readonly':True,'size':'100'},
}

form_next = """<?xml version="1.0"?>
<form string="Amount and Reference">
    <field name="amt" colspan="2"/>
    <field name="ref" colspan="2"/>
</form>
"""
fields_next = {
    'amt': {'string':'Amount', 'type':'float', 'required':True},
    'ref': {'string':'Reference', 'type':'char', 'required':True},
}

def _rec_enc_cash(self, cr, uid, data, context):

    pool_link= pooler.get_pool(cr.dbname)
    pool_link_statement=pool_link.get('account.bank.statement')
    statement_ids=pool_link_statement.search(cr,uid,[('date','=',time.strftime('%Y-%m-%d')),('state','=','draft')])
    message='Your Cash Entries Have Been Encoded to Bank Statement '
    vals={}
    obj_current_model=pool_link.get(data['model']).browse(cr,uid,data['ids'])

    statements_lines=[]

    for item in obj_current_model:
        res={}
        res['name']=item.name
        res['ref']=data['form']['ref']
        res['amount']=data['form']['amt']
        if 'order_partner_id' in item:
            res['partner_id']=item.order_partner_id.id
            if not res['partner_id']:
                raise wizard.except_wizard(_('Warning'), _('No Partner Defined on Embassy folder'))
            data_account=pool_link.get('account.bank.statement.line').onchange_partner_id(cr,uid,line_id=[],partner_id=item.order_partner_id.id,type='general',currency_id=False)
        else:
            res['partner_id']=item.partner_id.id
            if not res['partner_id']:
                raise wizard.except_wizard(_('Warning'), _('No Partner Defined on Embassy folder'))
            data_account=pool_link.get('account.bank.statement.line').onchange_partner_id(cr,uid,line_id=[],partner_id=item.partner_id.id,type='general',currency_id=False)
        res['account_id']=data_account['value']['account_id']
        statements_lines.append([0,0,res])

    vals['line_ids']=statements_lines

    if statement_ids:
        pool_link_statement.write(cr,uid,statement_ids[0],vals)
        message += pool_link_statement.browse(cr,uid,statement_ids[0]).name
    else:
        vals['journal_id']=data['form']['journal']
        statement_id=pool_link_statement.create(cr,uid,vals,context)
        message += pool_link_statement.browse(cr,uid,statement_id).name

    data['form']['message']=message
    return data['form']


class receive_encode_cash(wizard.interface):
    def _default_next(self, cr, uid, data, context):
        pool_obj= pooler.get_pool(cr.dbname)
        obj_journal=pool_obj.get('account.journal').browse(cr,uid,data['form']['journal'])
        seq = pool_obj.get('ir.sequence').get(cr, uid,obj_journal.sequence_id.code)
        data['form']['ref']=seq
        return data['form']

    states = {
        'init' : {
            'actions' : [],
            'result' : {'type' : 'form' ,   'arch' : form_journal,
                    'fields' : fields_journal,
                    'state' : [('end','Cancel'),('go','Next')]}
        },
        'go' : {
            'actions' : [_default_next],
            'result' : {'type' : 'form' ,   'arch' : form_next,
                    'fields' : fields_next,
                    'state' : [('end','Cancel'),('encode','Encode')]}
        },
        'encode': {
            'actions': [_rec_enc_cash],
            'result' : {'type' : 'form' ,   'arch' : form_notify,
                    'fields' : fields_notify,
                    'state' :[('end','Ok')]}
        }
    }

receive_encode_cash("cci_missions.rec_enc_cash")
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

