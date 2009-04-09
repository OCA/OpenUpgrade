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
from osv import osv
import pooler


class request_quotation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(request_quotation, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_line_tax': self._get_line_tax,
            'get_tax': self._get_tax,
            'editor' : self.editor,
            'purchase' : self.purchase,
            'author':self.author,
        })
    def editor(self,o_id):
        self.cr.execute("select distinct p.editor from purchase_order_line pl left join product_product p on (pl.product_id=p.id) where pl.order_id=%d", (o_id,))
        res = map(lambda x: x[0], self.cr.fetchall())
        editor = []
        for r in res:
            if r:
                p = self.pool.get('res.partner').browse(self.cr, self.uid, r)
                editor.append({'id':p.id,'name':p.name})
            else:
                editor.append({'id':False,'name':''})
        return editor
    def purchase(self, editor_id, o_id):
        if editor_id:
            self.cr.execute("SELECT PL.id  FROM purchase_order_line PL,product_product P   where P.product_tmpl_id=PL.product_id and PL.order_id=%d and P.editor=%d", (o_id,editor_id or None))
        else:
            self.cr.execute("SELECT PL.id  FROM purchase_order_line PL,product_product P   where P.product_tmpl_id=PL.product_id and PL.order_id=%d and P.editor is NULL", (o_id,))
        res = self.cr.fetchall()
        line_id = map(lambda x: x[0], res)
        line = self.pool.get('purchase.order.line').browse(self.cr,self.uid,line_id)
        return line

    def author(self,product_id):

        author_id = self.pool.get('product.product').read(self.cr,self.uid,[product_id])[0];

        author_name = self.pool.get('library.author').read(self.cr,self.uid,author_id['author_ids']);

        name_list=[];

        for a_name in author_name:
            name_list.append(a_name['name']);

        return ' , '.join(name_list)
    # end def

    def _get_line_tax(self, line_obj):
        self.cr.execute("SELECT tax_id FROM purchase_order_taxe WHERE order_line_id=%d" % (line_obj.id))
        res = self.cr.fetchall() or None
        if not res:
            return ""
        if isinstance(res, list):
            tax_ids = [t[0] for t in res]
        else:
            tax_ids = res[0]
        res = [tax.name for tax in pooler.get_pool(cr.dbname).get('account.tax').browse(self.cr, self.uid, tax_ids)]
        return ",\n ".join(res)

    def _get_tax(self, order_obj):
        self.cr.execute("SELECT DISTINCT tax_id FROM purchase_order_taxe, purchase_order_line, purchase_order \
            WHERE (purchase_order_line.order_id=purchase_order.id) AND (purchase_order.id=%d)" % (order_obj.id))
        res = self.cr.fetchall() or None
        if not res:
            return []
        if isinstance(res, list):
            tax_ids = [t[0] for t in res]
        else:
            tax_ids = res[0]
        tax_obj = pooler.get_pool(cr.dbname).get('account.tax')
        res = []
        for tax in tax_obj.browse(self.cr, self.uid, tax_ids):
            self.cr.execute("SELECT DISTINCT order_line_id FROM purchase_order_line, purchase_order_taxe \
                WHERE (purchase_order_taxe.tax_id=%d) AND (purchase_order_line.order_id=%d)" % (tax.id, order_obj.id))
            lines = self.cr.fetchall() or None
            if lines:
                if isinstance(lines, list):
                    line_ids = [l[0] for l in lines]
                else:
                    line_ids = lines[0]
                base = 0
                for line in pooler.get_pool(cr.dbname).get('purchase.order.line').browse(self.cr, self.uid, line_ids):
                    base += line.price_subtotal
                res.append({'code':tax.name,
                    'base':base,
                    'amount':base*tax.amount})
        return res

report_sxw.report_sxw('report.purchase.quotation.bookstore','purchase.order','addons/bookstore/report/quotation.rml',parser=request_quotation)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

