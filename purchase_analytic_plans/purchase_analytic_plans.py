# -*- encoding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2004-2006 TINY SPRL. (http://tiny.be) All Rights Reserved.
#
# $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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

from osv import fields
from osv import osv
import time
import netsvc

import ir
from mx import DateTime
import pooler
from tools import config

class purchase_order_line(osv.osv):
    _name='purchase.order.line'
    _inherit='purchase.order.line'
    _columns = {
        'analytics_id':fields.many2one('account.analytic.plan.instance','Analytic Distribution'),
    }

purchase_order_line()

class purchase_order(osv.osv):
    _name='purchase.order'
    _inherit='purchase.order'

    def action_invoice_create(self, cr, uid, ids, *args):
        res = False
        for o in self.browse(cr, uid, ids):
            il = []
            for ol in o.order_line:

                if ol.product_id:
                    a = ol.product_id.product_tmpl_id.property_account_expense.id
                    if not a:
                        a = ol.product_id.categ_id.property_account_expense_categ.id
                    if not a:
                        raise osv.except_osv('Error !', 'There is no expense account defined for this product: "%s" (id:%d)' % (line.product_id.name, line.product_id.id,))
                else:
                    a = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category')
                il.append((0, False, {
                    'name': ol.name,
                    'account_id': a,
                    'price_unit': ol.price_unit or 0.0,
                    'quantity': ol.product_qty,
                    'product_id': ol.product_id.id or False,
                    'uos_id': ol.product_uom.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in ol.taxes_id])],
                    'analytics_id': ol.analytics_id.id,
                }))

            a = o.partner_id.property_account_payable.id
            inv = {
                'name': o.partner_ref or o.name,
                'reference': "P%dPO%d" % (o.partner_id.id, o.id),
                'account_id': a,
                'type': 'in_invoice',
                'partner_id': o.partner_id.id,
                'currency_id': o.pricelist_id.currency_id.id,
                'address_invoice_id': o.partner_address_id.id,
                'address_contact_id': o.partner_address_id.id,
                'origin': o.name,
                'invoice_line': il,
            }
            inv_id = self.pool.get('account.invoice').create(cr, uid, inv, {'type':'in_invoice'})
            self.pool.get('account.invoice').button_compute(cr, uid, [inv_id], {'type':'in_invoice'}, set_total=True)

            self.write(cr, uid, [o.id], {'invoice_id': inv_id})
            res = inv_id
        return res
purchase_order()