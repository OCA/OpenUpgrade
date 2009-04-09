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

class sale_category_report(report_sxw.rml_parse):
    # o must be an instance of sale_order. Returns a list of 2-tuple
    # (category name, [list of sale_order_line of this category])
    def order_lines_by_categ(self, o):
        # result is a dictionnary where keys are category
        # names and values are lists of sale_category_sale_order_line.

        self.pool = pooler.get_pool(self.cr.dbname)
        ids = self.pool.get('product.category').search(self.cr, self.uid, [('parent_id','=',False)])
        cats = map(lambda x: (x, (x.sequence,)), self.pool.get('product.category').browse(self.cr, self.uid, ids))
        pos = 0
        result = {}
        while pos<len(cats):
            for c2 in cats[pos][0].child_id[::-1]:
                cats.insert(pos+1, (c2, cats[pos][1]+(cats[pos][0].sequence,)))
            for line in o.order_line:
                if line.product_id.categ_id == cats[pos][0]:
                    result.setdefault( (cats[pos][1], cats[pos][0].complete_name), []).append(line)
            pos += 1
        return sorted(result.items())

    def __init__(self, cr, uid, name, context):
        super(sale_category_report, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time' : time,
            'order_lines_by_categ' : self.order_lines_by_categ,
        } )

report_sxw.report_sxw(
    'report.sale_category.print',
    'sale.order',
    'addons/sale_category/report/sale_category_report.rml',
    parser=sale_category_report)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

