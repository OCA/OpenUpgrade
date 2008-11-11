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
import netsvc
from osv import fields, osv


class purchase_order(osv.osv):
    _inherit = 'purchase.order';

    def action_invoice_create(self, cr, uid, ids, *args):
        res = False
        for o in self.browse(cr, uid, ids):
            il = []
            for ol in o.order_line:
                a = False
                if ol.product_id:
                    if ol.order_id.partner_id.partner_location == 'local':
                        if ol.product_id.product_tmpl_id.property_account_expense:
                            a = ol.product_id.product_tmpl_id.property_account_expense;
                        else:
                            a =  ol.product_id.product_tmpl_id.categ_id.property_account_expense_categ[0];
                        #end if
                    elif ol.order_id.partner_id.partner_location == 'europe':
                        if ol.product_id.product_tmpl_id.property_account_expense_europe:
                            a = ol.product_id.product_tmpl_id.property_account_expense_europe;
                        else:
                            a =  ol.product_id.product_tmpl_id.categ_id.property_account_expense_europe[0];
                        #end if
                    elif ol.order_id.partner_id.partner_location == 'outside':
                        if ol.product_id.product_tmpl_id.property_account_expense_world:
                            a = ol.product_id.product_tmpl_id.property_account_expense_world1;
                        else:
                            a = ol.product_id.product_tmpl_id.categ_id.property_account_expense_world[0];
                    #end if
                    if not a:
                        a = ol.product_id.categ_id.property_account_expense_categ[0]

                else:
                    a = self.pool.get('ir.property').get(cr, uid, 'property_account_expense_categ', 'product.category')
                il.append((0, False, {
                    'name': ol.name,
                    'account_id': a,
                    'price_unit': ol.price_unit or 0.0,
                    'quantity': ol.product_qty,
                    'product_id': ol.product_id.id or False,
                    'uos_id': ol.product_uom.id or False,
                    'invoice_line_tax_id': [(6, 0, [x.id for x in ol.taxes_id])]
                }))

            ac = o.partner_id.property_account_payable[0]
            inv = {
                'name': o.name,
                'reference': "P%dPO%d" % (o.partner_id.id, o.id),
                'account_id': ac,
                'type': 'in_invoice',
                'partner_id': o.partner_id.id,
                'currency_id': o.pricelist_id.currency_id.id,
                'project_id': o.project_id.id,
                'address_invoice_id': o.partner_address_id.id,
                'address_contact_id': o.partner_address_id.id,
                'origin': o.name,
                'invoice_line': il,
            }
            inv_id = self.pool.get('account.invoice').create(cr, uid, inv)

            self.write(cr, uid, [o.id], {'invoice_id': inv_id})
            res = inv_id
        return res
    #end def
#end class

purchase_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

