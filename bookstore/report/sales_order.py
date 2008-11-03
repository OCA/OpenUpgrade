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

class sales_order(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sales_order, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'qty':self.qty,
            'convert':self.french_convert,
            'author' : self.author
        })

    def french_convert(self,amount):
        amt = amount_to_text.amount_to_text_fr(amount,'Euro');
        amt_en = amount_to_text.amount_to_text_en(amount,'Euro');
        value={};
        value= {'french':amt, 'english':amt_en}
        return value;

    # end def

    def author(self,product_id):

        author_id = self.pool.get('product.product').read(self.cr,self.uid,[product_id])[0];

        author_name = self.pool.get('library.author').read(self.cr,self.uid,author_id['author_ids']);

        name_list=[];

        for a_name in author_name:
            name_list.append(a_name['name']);

        return ' , '.join(name_list)
    # end def

    def qty(self,order):
        ret_qty = 0.0;
        for order_line in order.order_line:
            ret_qty = ret_qty + order_line.product_uom_qty;

        return ret_qty;
    # end def

report_sxw.report_sxw('report.sale.order.bookstore', 'sale.order', 'addons/bookstore/report/sales_order.rml', parser=sales_order)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

