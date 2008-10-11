# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: partner.py 1007 2005-07-25 13:18:09Z kayhman $
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
            cr.execute('select id from sale_order_line where order_id = %d and product_id = %d',(line.order_id.id,line.product_id.id))
            sale_line_id = cr.fetchall()[0][0]
            sale_line_obj = self.pool.get('sale.order.line').browse(cr, uid,sale_line_id )
            res[line.id] = round((sale_line_obj.price_unit*line.product_qty*(100.0-sale_line_obj.discount)/100.0) -(sale_line_obj.product_id.standard_price*line.product_qty),2)
        return res

    _columns = {
        'margin': fields.function(_delivery_margin, method=True, string='Margin'),
    }
sale_delivery_line()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

