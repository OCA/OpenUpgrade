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
from report import report_sxw
from tools import amount_to_text

class account_invoice(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(account_invoice, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'qty':self.qty,
            'convert':self.french_convert,
            'author' : self.author,
            'partner_ref':self.partner_ref
        })

    def partner_ref(self,production_id):

        sql = 'select order_id from sale_order_line where production_lot_id = %d '

        self.cr.execute(sql%(production_id))

        res = [];
        res=self.cr.fetchall();


        sales_order = self.pool.get('sale.order').read(self.cr,self.uid,[res[0][0]]);


        partner_ref = sales_order[0]['client_order_ref']
        name = sales_order[0]['name']

        value ={'partner_ref':partner_ref,'name':name}
        return value;

    def author(self,product_id):
        if not product_id : return ''
        author_id = self.pool.get('product.product').read(self.cr,self.uid,[product_id])[0];

        author_name = self.pool.get('library.author').read(self.cr,self.uid,author_id['author_ids']);

        name_list=[];

        name="Authors -"

        for a_name in author_name:
            name_list.append(a_name['name']);

        return ', '.join(name_list)

    # end def

    def french_convert(self,amount):
        amt = amount_to_text.amount_to_text_fr(amount,'Euro');
        amt_en = amount_to_text.amount_to_text_en(amount,'Euro');
        value={};
        value= {'french':amt, 'english':amt_en}
        return value;

    # end def

    def qty(self,invoice):
        ret_qty = 0.0;
        for invoice_line in invoice.invoice_line:
            if invoice_line.product_id.type<>'service':
                ret_qty = ret_qty + invoice_line.quantity;
        return ret_qty;
    # end def


report_sxw.report_sxw('report.account.invoice.bookstore', 'account.invoice', 'addons/bookstore/report/invoice.rml', parser=account_invoice)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

