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

import pooler
import time
from report import report_sxw

class third_party_ledger(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(third_party_ledger, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'lines': self.lines,
            'sum_debit_partner': self._sum_debit_partner_crdr,
            'sum_credit_partner': self._sum_credit_partner_crdr,
            'sum_debit': self._sum_debit,
            'sum_credit': self._sum_credit,
            'get_company': self._get_company,
            'get_currency': self._get_currency,
            'partners': self.partners,
            'balance_partner':self.balance_partner
        })

    def partners(self, form):
        data = {'form':form}
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='line',
                context={'fiscalyear': data['form']['fiscalyear']})
        self.cr.execute(
                "SELECT DISTINCT line.partner_id " \
                "FROM account_move_line AS line, account_account AS account " \
                "WHERE line.partner_id IS NOT NULL " \
                    "AND line.date >= %s " \
                    "AND line.date <= %s " \
                    "AND " + line_query + " " \
                    "AND line.account_id = account.id " \
                    "AND account.company_id = %s " \
                    "AND account.active",
                (data['form']['date1'], data['form']['date2'],
                    data['form']['company_id']))
        new_ids = form['partners'][0][2] #[id for (id,) in self.cr.fetchall()]
#        self.cr.execute(
#            "SELECT a.id " \
#            "FROM account_account a " \
#            "LEFT JOIN account_account_type t " \
#                "ON (a.type=t.code) " \
#            "WHERE t.partner_account=TRUE " \
#                "AND a.company_id = %d " \
#                "AND a.active", (data['form']['company_id'],))
        self.cr.execute('SELECT a.id ' \
            'FROM account_account a ' \
                'WHERE a.company_id = %s ' \
                'AND a.active', (form['company_id'],))
        self.account_ids = ','.join([str(a) for (a,) in self.cr.fetchall()])
        self.partner_ids = ','.join(map(str, new_ids))
        objects = self.pool.get('res.partner').browse(self.cr, self.uid, new_ids)

        objects = self.pool.get('res.partner').browse(self.cr, self.uid, form['partners'][0][2])
        return objects

    def lines(self, partner):
        partner_id = self.data['partners'][0][2]
        if not partner.id in partner_id:
            return {}
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid, obj='l',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        sSQL = "SELECT m.id as id, l.date, j.code, m.name as ref, l.name, a.name as aname,l.ref, l.debit, l.credit " \
                "FROM account_account a, account_move m, account_move_line l " \
                "LEFT JOIN account_journal j " \
                    "ON (l.journal_id = j.id) " \
                "WHERE l.partner_id = " + str(partner.id) + " AND l.account_id = a.id AND m.id = l.move_id " \
                    "AND l.account_id IN (" + self.account_ids + ") " \
                    "AND l.date >= '" + self.datas['form']['date1'] + "'"\
                    "AND l.date <= '" +self.datas['form']['date2'] + "'" \
                    "AND " + line_query + " " \
                "ORDER BY l.date,m.name,l.ref "
        self.cr.execute(sSQL)
        res = self.cr.dictfetchall()
        sum = 0.0
        if res:
            for r in res:
                ans = r['debit'] - r['credit']
                name = ""
                if r['debit'] > 0:
                    aids = account_move_line_obj.search(self.cr, self.uid,[('debit','=','0'), ('move_id','=',r['id'])])
                    name = account_move_line_obj.browse(self.cr, self.uid, aids[0]).account_id.name
                elif r['credit'] > 0:
                    aids = account_move_line_obj.search(self.cr, self.uid,[('credit','=','0'), ('move_id','=',r['id'])])
                    name = account_move_line_obj.browse(self.cr, self.uid, aids[0]).account_id.name
    
                r['aname'] = name
                sum += ans
                ans = sum
                if ans > 0:
                    ans = str(ans) + " Dr."
                else:
                    ans = ans * -1
                    ans = str(ans) + " Cr."
                   
                r['progress'] = ans
        return res

    def _sum_debit_partner(self, partner):
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
                "SELECT sum(debit) " \
                "FROM account_move_line " \
                "WHERE partner_id = %s " \
                    "AND account_id IN (" + self.account_ids + ") " \
                    "AND date >= %s " \
                    "AND date <= %s " \
                    "AND " + line_query,
                (partner.id, self.datas['form']['date1'], self.datas['form']['date2']))
        
        ans = self.cr.fetchone()[0]
        return ans or 0.0
        
    def _sum_debit_partner_crdr(self, partner):
        ans = self._sum_debit_partner(partner)
        ans = str(ans) + " Dr."
        return ans
    
    def _sum_credit_partner(self, partner):
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
                "SELECT sum(credit) " \
                "FROM account_move_line " \
                "WHERE partner_id=%s " \
                    "AND account_id IN (" + self.account_ids + ") " \
                    "AND date >= %s " \
                    "AND date <= %s " \
                    "AND " + line_query,
                (partner.id, self.datas["form"]["date1"], self.datas["form"]["date2"]))
        ans = self.cr.fetchone()[0]
        return ans or 0.0
    
    def _sum_credit_partner_crdr(self, partner):
        ans = self._sum_credit_partner(partner)
        ans = str(ans) + " Cr."
        return ans
    
    def balance_partner(self, partner):
        debit = self._sum_debit_partner(partner)
        credit =self._sum_credit_partner(partner)
        ans = debit - credit
        if ans > 0:
            ans = str(ans) + " Dr."
        else:
            ans = ans * -1
            ans = str(ans) + " Cr."
        return ans
         
    def _sum_debit(self):
        if not self.ids:
            return 0.0
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
                "SELECT sum(debit) " \
                "FROM account_move_line " \
                "WHERE partner_id IN (" + self.partner_ids + ") " \
                    "AND account_id IN (" + self.account_ids + ") " \
                    "AND date >= %s " \
                    "AND date <= %s " \
                    "AND " + line_query,
                (self.datas['form']['date1'], self.datas['form']['date2']))

        ans = self.cr.fetchone()[0]
        
        return ans or 0.0
        
    def _sum_credit(self):
        if not self.ids:
            return 0.0
        account_move_line_obj = pooler.get_pool(self.cr.dbname).get('account.move.line')
        line_query = account_move_line_obj._query_get(self.cr, self.uid,
                obj='account_move_line',
                context={'fiscalyear': self.datas['form']['fiscalyear']})
        self.cr.execute(
                "SELECT sum(credit) " \
                "FROM account_move_line " \
                "WHERE partner_id IN (" + self.partner_ids + ") " \
                    "AND account_id IN (" + self.account_ids + ") " \
                    "AND date >= %s " \
                    "AND date <= %s " \
                    "AND " + line_query,
                (self.datas['form']['date1'], self.datas['form']['date2']))
        ans = self.cr.fetchone()[0]
        return ans or 0.0

    
    def _get_company(self, form):
        self.data = form
        return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).name

    def _get_currency(self, form):
        return pooler.get_pool(self.cr.dbname).get('res.company').browse(self.cr, self.uid, form['company_id']).currency_id.name

report_sxw.report_sxw('report.account.third_party_wise_ledger', 'res.partner',
        'addons/account_invoice_india/report/third_party_ledger.rml',parser=third_party_ledger,
        header=False)
