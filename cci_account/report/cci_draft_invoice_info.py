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
import time
import pooler
from report import report_sxw


STATE = [
    ('none', 'Non Member'),
    ('canceled', 'Canceled Member'),
    ('old', 'Old Member'),
    ('waiting', 'Waiting Member'),
    ('invoiced', 'Invoiced Member'),
    ('associated', 'Associated Member'),
    ('free', 'Free Member'),
    ('paid', 'Paid Member'),
]

class account_invoice_draft(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice_draft, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'partner_objects':self.partner_objects,
            'member_type':self.member_type,
            'nationality':self.nationality,
            'lines':self.lines,
            'sum_amt_untaxed':self.sum_amt_untaxed,
            'sum_amt_tax':self.sum_amt_tax,
            'sum_total':self.sum_total,
        })
        self.sum_untaxed=0.00
        self.sum_tax=0.00
        self.sum_tot=0.00

    def partner_objects(self,ids={}):
        if not ids:
            ids = self.ids
        partner_objects = pooler.get_pool(self.cr.dbname).get('res.partner').browse(self.cr, self.uid, ids)
        return partner_objects

    def member_type(self, object):
        membership=object.membership_state
        for member_type in STATE:
            if membership==member_type[0]:
                membership=member_type[1]
                break
        return membership

    def nationality(self, object):
        nationality='Not Mentioned'
        if object.address:
            for ads in object.address:
                if ads.type=='default':
                  if ads.country_id:
                        if ads.country_id.code=='BE':
                            nationality='Belgian'
                        else:
                            nationality='Non-Belgian'

        return nationality

    def lines(self, object):
        result=[]
        obj_inv=pooler.get_pool(self.cr.dbname).get('account.invoice')
        list_ids=obj_inv.search(self.cr,self.uid,[('state','=','draft'),('partner_id','=',object.id),('type','=','out_invoice')])
        invoices=obj_inv.browse(self.cr,self.uid,list_ids)

        self.sum_untaxed=0.00
        self.sum_tax=0.00
        self.sum_tot=0.00
        for invoice in invoices:

            self.sum_untaxed +=invoice.amount_untaxed

            self.sum_tax +=invoice.amount_tax

            self.sum_tot +=invoice.amount_total

            if not invoice.invoice_line:
                continue

            for line in invoice.invoice_line:

                res={}
                res['name']=line.name
                res['date']=invoice.date_invoice
                untaxed=line.price_unit * line.quantity
                discounted=(untaxed) * line.discount / 100

                res['amt_untaxed']=(untaxed) - discounted
                tax_info=pooler.get_pool(self.cr.dbname).get('account.tax').compute(self.cr,self.uid,line.invoice_line_tax_id, line.price_unit,line.quantity)
                taxed = 0.00
                if tax_info:
                    for record in tax_info:
                        taxed += record['amount']
                res['vat']=taxed

                res['total']=untaxed - discounted + taxed
                res['gen_acc']=line.account_id.name
                res['analytic_acc']=line.account_analytic_id and line.account_analytic_id.name or '-'
                result.append(res)

        return result

    def sum_amt_untaxed(self):
        return self.sum_untaxed

    def sum_amt_tax(self):
        return self.sum_tax

    def sum_total(self):
        return self.sum_tot

report_sxw.report_sxw('report.partner.draft_invoices', 'res.partner', 'addons/cci_account/report/cci_draft_invoice_info.rml', parser=account_invoice_draft,header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

