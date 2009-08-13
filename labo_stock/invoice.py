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
import pooler
import mx.DateTime
from mx.DateTime import RelativeDateTime

from tools import config


class account_invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit ='account.invoice.line'

    def product_id_change(self, cr, uid, ids, product, uom, qty=0, name='', type='out_invoice', partner_id=False, price_unit=False, address_invoice_id=False, context={}):
        res = super(account_invoice_line, self).product_id_change(cr, uid, ids, product, uom, qty, name, type, partner_id, price_unit, address_invoice_id, context)
        if not product:
            return res
        if partner_id and (type not in ('in_invoice', 'in_refund')):
            pricelist = self.pool.get('res.partner').browse(cr, uid, partner_id).property_product_pricelist.id
            if not pricelist:
                raise osv.except_osv('No Pricelist !',
                    'You have to select a partner in the invoice form which has not pricelist defined!\n'
                    'Please set pricelist to partner before choosing a product.')
            invoice_date = time.strftime('%Y-%m-%d')
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                product, qty or 1.0, partner_id, {
                    'uom': uom,
                    'date': invoice_date,
                    })[pricelist]
            if price is False:
                raise osv.except_osv('No valid pricelist line found !',
                    "Couldn't find a pricelist line matching this product and quantity.\n"
                    "You have to change either the product, the quantity or the pricelist.")
            res['value']['price_unit'] = price
        return res

account_invoice_line()