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
from osv import fields, osv
import pooler
from tools import config
import time
from osv.osv import except_osv

class product_pricelist(osv.osv):
    _name = 'product.pricelist'
    _inherit = 'product.pricelist'
    _columns ={
        'visible_discount':fields.boolean('Visible Discount'),
    }

    _defaults = {
         'visible_discount':lambda *a: True,
   }
product_pricelist()

class sale_order_line(osv.osv):
    _name = "sale.order.line"
    _inherit = "sale.order.line"

    def product_id_change(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True,date_order=False):

        res=super(sale_order_line, self).product_id_change(cr, uid, ids, pricelist, product, qty,
            uom, qty_uos, uos, name, partner_id,
            lang, update_tax,date_order)
        result=res['value']
        pricelist_obj=self.pool.get('product.pricelist')
        product_obj = self.pool.get('product.product')
        if product:
            price=result['price_unit']
            product = product_obj.browse(cr, uid, product)
            pricelists=pricelist_obj.read(cr,uid,[pricelist],['visible_discount'])
            if(len(pricelists)>0 and pricelists[0]['visible_discount']):
                discount=(product.list_price-price) / product.list_price * 100
                result['price_unit']=product.list_price
                result['discount']=discount
            else:
                result['discount']=0.0
        return res



sale_order_line()

class account_invoice_line(osv.osv):
    _name = "account.invoice.line"
    _inherit = "account.invoice.line"

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, price_unit=False, address_invoice_id=False, context={}):
        res=super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, price_unit, address_invoice_id, context)
        if product:
            product = self.pool.get('product.product').browse(cr, uid, product, context=context)
            result=res['value']
            if type in ('in_invoice', 'in_refund'):
                real_price=product.standard_price
                if not price_unit and partner_id:
                    pricelist = self.pool.get('res.partner').browse(cr, uid, partner_id).property_product_pricelist_purchase.id
                    price_unit = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product.id, qty or 1.0, partner_id, {'uom': uom})[pricelist]
            else:
                real_price=product.list_price
                if partner_id:
                    pricelist = self.pool.get('res.partner').browse(cr, uid, partner_id).property_product_pricelist.id
                    price_unit = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],product.id, qty or 1.0, partner_id, {'uom': uom})[pricelist]


            if pricelist:
                pricelists=self.pool.get('product.pricelist').read(cr,uid,[pricelist],['visible_discount'])
                if(len(pricelists)>0 and pricelists[0]['visible_discount']):
                    discount=(real_price-price_unit) / real_price * 100
                    result['price_unit']=real_price
                    result['discount']=discount
                else:
                    result['discount']=0.0
        return res


account_invoice_line()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

