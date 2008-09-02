# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2008 JAILLET Simon - CrysaLEAD - www.crysalead.fr
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
import osv
import pooler

_transaction_form = '''<?xml version="1.0"?>
<form string="Close Fiscal Year">
    <field name="fy_id"/>
    <field name="fy2_id"/>
    <field name="report_new"/>
    <field name="closing_name" colspan="3"/>
    <field name="opening_name" colspan="3"/>
    <field name="report_closing_journal" colspan="3"/>
    <field name="report_opening_journal" colspan="3"/>
    <field name="pl_credit" colspan="3"/>
    <field name="pl_debit" colspan="3"/>
    <separator string="Are you sure ?" colspan="4"/>
    <field name="sure"/>
</form>'''

_transaction_fields = {
    'fy_id': {'string':'Fiscal Year to close', 'type':'many2one', 'relation': 'account.fiscalyear','required':True, 'domain':[('state','=','draft')]},
    'fy2_id': {'string':'New Fiscal Year', 'type':'many2one', 'relation': 'account.fiscalyear', 'domain':[('state','=','draft')], 'required':True},
    'report_new': {'string':'Create new entries', 'type':'boolean', 'required':True, 'default': lambda *a:True},
    'closing_name': {'string':'Name of closing entries', 'type':'char', 'size': 64, 'required':True},
    'opening_name': {'string':'Name of opening entries', 'type':'char', 'size': 64, 'required':True},
    'report_closing_journal': {'string':'Closing Journal', 'type':'many2one', 'relation': 'account.journal', 'required':True},
    'report_opening_journal': {'string':'Opening Journal', 'type':'many2one', 'relation': 'account.journal', 'required':True},
    'pl_credit': {'string':'Net income (credit)', 'type':'many2one', 'relation': 'account.account', 'required':True},
    'pl_debit': {'string':'Net income (debit)', 'type':'many2one', 'relation': 'account.account', 'required':True},
    'sure': {'string':'Check this box', 'type':'boolean'},
}

def _data_load(self, cr, uid, data, context):
    data['form']['report_new'] = True
    return data['form']

def _data_save(self, cr, uid, data, context):
    if not data['form']['sure']:
        raise wizard.except_wizard('UserError', 'Closing of fiscal year canceled, please check the box !')
    pool = pooler.get_pool(cr.dbname)

    fy_id = data['form']['fy_id']
    if data['form']['report_new']:

                #Closing

        closing_journal = pool.get('account.journal').browse(cr, uid, data['form']['report_closing_journal'])
        if not closing_journal.default_credit_account_id or not closing_journal.default_debit_account_id:
            raise wizard.except_wizard('UserError',
                    'The journal must have default credit and debit account')
        if not closing_journal.centralisation:
            raise wizard.except_wizard('UserError',
                    'The journal must have centralised counterpart')

        periods=pool.get('account.period').search(cr, uid,[('fiscalyear_id','=',fy_id)])
        period_query_cond=str(tuple(periods))

        query = "SELECT id,date_stop FROM account_period WHERE date_stop=(SELECT MAX(date_stop) AS date_stop FROM account_period WHERE id IN "+str(period_query_cond)+")"
        cr.execute(query)
        result =cr.dictfetchall()
        period_id=result[0]['id']
        date_stop=result[0]['date_stop']

        query = "SELECT aa.code AS code, aml.account_id AS account_id, SUM(debit) as debit, SUM(credit) as credit FROM account_move_line aml LEFT JOIN account_account aa ON aa.id=aml.account_id WHERE aa.type = 'income' OR aa.type ='expense' AND period_id IN "+str(period_query_cond)+" GROUP BY code, account_id"

        cr.execute(query)

        profit_and_loss=0.0
        lines=cr.dictfetchall()
        for line in lines:
            balance=line['debit']-line['credit']
            if abs(balance)>0.0001:
                profit_and_loss+=balance
                pool.get('account.move.line').create(cr, uid, {
                    'debit': balance<0 and -balance,
                    'credit': balance>0 and balance,
                    'name': data['form']['closing_name'],
                    'date': date_stop,
                    'journal_id': closing_journal.id,
                    'period_id': period_id,
                    'account_id': line['account_id']
                }, {'journal_id': closing_journal.id, 'period_id':period_id})

        pool.get('account.move.line').create(cr, uid, {
            'debit': profit_and_loss>0 and profit_and_loss,
            'credit': profit_and_loss<0 and -profit_and_loss,
            'name': data['form']['closing_name'],
            'date': date_stop,
            'journal_id': closing_journal.id,
            'period_id': period_id,
            'account_id': profit_and_loss>0 and data['form']['pl_debit'] or data['form']['pl_credit']
        }, {'journal_id': closing_journal.id, 'period_id':period_id})


        #Opening

        period = pool.get('account.fiscalyear').browse(cr, uid, data['form']['fy2_id']).period_ids[0]
        opening_journal = pool.get('account.journal').browse(cr, uid, data['form']['report_opening_journal'])
        if not opening_journal.default_credit_account_id or not opening_journal.default_debit_account_id:
            raise wizard.except_wizard('UserError',
                    'The journal must have default credit and debit account')
        if not opening_journal.centralisation:
            raise wizard.except_wizard('UserError',
                    'The journal must have centralised counterpart')

        query_line = pool.get('account.move.line')._query_get(cr, uid,
                obj='account_move_line', context={'fiscalyear': fy_id})

        #query = "SELECT aa.code, aml.account_id, SUM(aml.debit) AS debit, SUM(aml.credit) AS credit, aa.type, aa.close_method FROM account_move_line aml LEFT JOIN account_account aa ON aa.id=aml.account_id WHERE period_id IN "+str(period_query_cond)+" GROUP BY aa.code, aml.account_id, aa.type, aa.close_method"
        # modify query because of deferral method removed from account object now it wll take deferral method from account-type object
        query = "SELECT aa.code, aml.account_id, SUM(aml.debit) AS debit, SUM(aml.credit) AS credit, aa.type, aat.close_method FROM account_move_line aml LEFT JOIN account_account aa ON aa.id=aml.account_id LEFT JOIN account_account_type aat ON aat.code=aa.type WHERE period_id IN "+str(period_query_cond)+" GROUP BY aa.code, aml.account_id, aa.type, aat.close_method"
        cr.execute(query)
        lines=cr.dictfetchall()

        for line in lines:
            if line['close_method']=='none' or line['type'] == 'view':
                continue
            balance=line['debit']-line['credit']
            if line['close_method']=='balance':
                if abs(balance)>0.0001:
                    pool.get('account.move.line').create(cr, uid, {
                        'debit': balance>0 and balance,
                        'credit': balance<0 and -balance,
                        'name': data['form']['opening_name'],
                        'date': period.date_start,
                        'journal_id': opening_journal.id,
                        'period_id': period.id,
                        'account_id': line['account_id']
                    }, {'journal_id': opening_journal.id, 'period_id':period.id})
            if line['close_method']=='unreconciled':
                offset = 0
                limit = 100
                while True:
                    cr.execute('SELECT name, quantity, debit, credit, account_id, ref, ' \
                                'amount_currency, currency_id, blocked, partner_id, ' \
                                'date_maturity, date_created ' \
                            'FROM account_move_line ' \
                            'WHERE account_id = %d ' \
                                'AND ' + query_line + ' ' \
                                'AND reconcile_id is NULL ' \
                            'ORDER BY id ' \
                            'LIMIT %d OFFSET %d', (line['account_id'], limit, offset))
                    result = cr.dictfetchall()
                    if not result:
                        break
                    for move in result:
                        move.update({
                            'date': period.date_start,
                            'journal_id': opening_journal.id,
                            'period_id': period.id,
                        })
                        pool.get('account.move.line').create(cr, uid, move, {
                            'journal_id': opening_journal.id,
                            'period_id': period.id,
                            })
                    offset += limit
            if line['close_method']=='detail':
                offset = 0
                limit = 100
                while True:
                    cr.execute('SELECT name, quantity, debit, credit, account_id, ref, ' \
                                'amount_currency, currency_id, blocked, partner_id, ' \
                                'date_maturity, date_created ' \
                            'FROM account_move_line ' \
                            'WHERE account_id = %d ' \
                                'AND ' + query_line + ' ' \
                            'ORDER BY id ' \
                            'LIMIT %d OFFSET %d', (line['account_id'],fy_id, limit, offset))
                    result = cr.dictfetchall()
                    if not result:
                        break
                    for move in result:
                        move.update({
                            'date': period.date_start,
                            'journal_id': opening_journal.id,
                            'period_id': period.id,
                        })
                        pool.get('account.move.line').create(cr, uid, move)
                    offset += limit

    cr.execute('UPDATE account_journal_period ' \
            'SET state = %s ' \
            'WHERE period_id IN (SELECT id FROM account_period WHERE fiscalyear_id = %d)',
            ('done',fy_id))
    cr.execute('UPDATE account_period SET state = %s ' \
            'WHERE fiscalyear_id = %d', ('done',fy_id))
    cr.execute('UPDATE account_fiscalyear ' \
            'SET state = %s ' \
            'WHERE id = %d', ('done',fy_id))

    return {}

class wiz_journal_close(wizard.interface):
    states = {
        'init': {
            'actions': [_data_load],
            'result': {'type': 'form', 'arch':_transaction_form, 'fields':_transaction_fields, 'state':[('end','Cancel'),('close','Close Fiscal Year')]}
        },
        'close': {
            'actions': [_data_save],
            'result': {'type': 'state', 'state':'end'}
        }
    }
wiz_journal_close('l10n.fr.fiscalyear.close')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

