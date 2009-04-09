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

class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
 
    def invoice_line_create(self, cr, uid, ids, context={}):
        def _get_line_qty(line):
            if (line.order_id.invoice_quantity=='order') or not line.procurement_id:
                return line.product_uos_qty or line.product_uom_qty
            else:
                return self.pool.get('mrp.procurement').quantity_get(cr, uid, line.procurement_id.id, context)
        create_ids = []
        for line in self.browse(cr, uid, ids, context):
            if not line.invoiced:
                a = None;
                if line.product_id:
                    #code addedd by Axelor Sarl START
                    if line.order_id.partner_id.partner_location:
                        if line.order_id.partner_id.partner_location == 'local':

                            if line.product_id.product_tmpl_id.property_account_income:
                                a =  line.product_id.product_tmpl_id.property_account_income[0];
                            else:
                                a =  line.product_id.product_tmpl_id.categ_id.property_account_income_categ[0];
                                #print "TEST .........",line.product_id.product_tmpl_id.categ_id.property_account_income;
                            #end if
                        elif line.order_id.partner_id.partner_location == 'europe':
                            if line.product_id.product_tmpl_id.property_account_income_europe:
                                a =  line.product_id.product_tmpl_id.property_account_income_europe[0];
                            else:
                                a =  line.product_id.product_tmpl_id.categ_id.property_account_income_europe[0];
                            #end if
                        elif line.order_id.partner_id.partner_location == 'outside':
                            if line.product_id.product_tmpl_id.property_account_income_world:
                                a =  line.product_id.product_tmpl_id.property_account_income_world[0];
                            else:
                                a =  line.product_id.product_tmpl_id.categ_id.property_account_income_world[0];
                            #end if
                        #end if
                    else:
                        a = self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ', 'product.category', context=context);
                    #End if
                    #code addedd by Axelor Sarl END
                else:
                    a = self.pool.get('ir.property').get(cr, uid, 'property_account_income_categ', 'product.category', context=context)

                uosqty = _get_line_qty(line)
                uos_id = (line.product_uos and line.product_uos.id) or False
                inv_id = self.pool.get('account.invoice.line').create(cr, uid, {
                    'name': line.name,
                    'account_id': a,
                    'price_unit': line.price_unit,
                    'quantity': uosqty,
                    'discount': line.discount,
                    'uos_id': uos_id,
                    'product_id': line.product_id.id or False,
                    'invoice_line_tax_id': [(6,0,[x.id for x in line.tax_id])],
                    'note': line.notes,
                })
                cr.execute('insert into sale_order_line_invoice_rel (order_line_id,invoice_id) values (%s,%s)', (line.id, inv_id))
                self.write(cr, uid, [line.id], {'invoiced':True})
                create_ids.append(inv_id)
        return create_ids
sale_order_line();
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

