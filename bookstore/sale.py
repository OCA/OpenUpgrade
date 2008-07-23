# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: sale.py 1005 2005-07-25 08:41:42Z nicoe $
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

import time
import netsvc
from osv import fields, osv
import ir
from mx import DateTime

class sale_order_line(osv.osv):
    _name = 'sale.order.line'
    _description = 'New Sale Order line'
    _inherit = 'sale.order.line'


    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):


        result = super(sale_order_line, self).product_id_change(cr, uid, ids,
            pricelist, product, qty, uom, qty_uos, uos, name, partner_id,lang,
            update_tax,date_order)

        if not product:
            return {'value': {'price_unit': 0.0, 'notes':'', 'weight' : 0}, 'domain':{'product_uom':[]}}
        product_res = self.pool.get('product.product').read(cr,uid,[product])[0];
        if product_res['virtual_available']>=qty and qty!=0.0:
            result['value']['type']='make_to_stock';
        return result;
sale_order_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

