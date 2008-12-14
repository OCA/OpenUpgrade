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

from osv import fields,osv
import pooler
from tools import config
import time

class sale_delivery_line(osv.osv):
    _inherit = "sale.delivery.line"
    def _delivery_margin(self, cr, uid, ids, field_name, arg, context):
        res = {}
        for line in self.browse(cr, uid, ids):
            res[line.id] = 0
            cr.execute('select id from sale_order_line where order_id = %s and product_id = %s',(line.order_id.id,line.product_id.id))
            sale_line_id = cr.fetchall()[0][0]
            sale_line_obj = self.pool.get('sale.order.line').browse(cr, uid,sale_line_id )
            res[line.id] = round((sale_line_obj.price_unit*line.product_qty*(100.0-sale_line_obj.discount)/100.0) -(sale_line_obj.product_id.standard_price*line.product_qty),2)
        return res

    _columns = {
        'margin': fields.function(_delivery_margin, method=True, string='Margin'),
    }
sale_delivery_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

