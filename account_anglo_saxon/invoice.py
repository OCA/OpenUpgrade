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

from osv import fields, osv

class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    
    def move_line_get(self, cr, uid, invoice_id, context=None):
        res = super(account_invoice_line,self).move_line_get(cr, uid, invoice_id, context)
        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
        if inv.type in ('out_invoice','in_refund'):
            for i_line in inv.invoice_line:
                if i_line.product_id:
                    dacc = i_line.product_id.product_tmpl_id.property_stock_account_output and i_line.product_id.product_tmpl_id.property_stock_account_output.id
                    if not dacc:
                        dacc = i_line.product_id.categ_id.property_stock_account_output_categ and i_line.product_id.categ_id.property_stock_account_output_categ.id
                    
                    cacc = i_line.product_id.product_tmpl_id.property_account_expense and i_line.product_id.product_tmpl_id.property_account_expense.id
                    if not cacc:
                        cacc = i_line.product_id.categ_id.property_account_expense_categ and i_line.product_id.categ_id.property_account_expense_categ.id
                    res.append({
                        'type':'src',
                        'name': i_line.name[:64],
                        'price_unit':i_line.product_id.product_tmpl_id.standard_price,
                        'quantity':i_line.quantity,
                        'price':i_line.product_id.product_tmpl_id.standard_price * i_line.quantity,
                        'account_id':dacc,
                        'product_id':i_line.product_id.id,
                        'uos_id':i_line.uos_id.id,
                        'account_analytic_id':i_line.account_analytic_id.id,
                        'taxes':i_line.invoice_line_tax_id,
                        })
                    
                    res.append({
                        'type':'src',
                        'name': i_line.name[:64],
                        'price_unit':i_line.product_id.product_tmpl_id.standard_price,
                        'quantity':i_line.quantity,
                        'price': -1 * i_line.product_id.product_tmpl_id.standard_price * i_line.quantity,
                        'account_id':cacc,
                        'product_id':i_line.product_id.id,
                        'uos_id':i_line.uos_id.id,
                        'account_analytic_id':i_line.account_analytic_id.id,
                        'taxes':i_line.invoice_line_tax_id,
                        })
        return res    
account_invoice_line()
#    def move_line_get(self, cr, uid, invoice_id, context=None):
#        res = super(account_invoice_line,self).move_line_get(cr, uid, invoice_id, context)
#        inv = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
#        if inv.type in ('out_invoice','in_refund'):
#            for i_line in inv.invoice_line:
#                if i_line.product_id:
#                    dacc = i_line.product_id.product_tmpl_id.property_account_sending_goods and i_line.product_id.product_tmpl_id.property_account_sending_goods.id
#                    if not dacc:
#                        dacc = i_line.product_id.categ_id.property_account_sending_goods_categ and i_line.product_id.categ_id.property_account_sending_goods_categ.id
#                    
#                    cacc = i_line.product_id.product_tmpl_id.property_account_expense and i_line.product_id.product_tmpl_id.property_account_expense.id
#                    if not cacc:
#                        cacc = i_line.product_id.categ_id.property_account_expense_categ and i_line.product_id.categ_id.property_account_expense_categ.id
#                    res.append({
#                        'type':'src',
#                        'name': i_line.name[:64],
#                        'price_unit':i_line.product_id.product_tmpl_id.standard_price,
#                        'quantity':i_line.quantity,
#                        'price':i_line.product_id.product_tmpl_id.standard_price * i_line.quantity,
#                        'account_id':dacc,
#                        'product_id':i_line.product_id.id,
#                        'uos_id':i_line.uos_id.id,
#                        'account_analytic_id':i_line.account_analytic_id.id,
#                        'taxes':i_line.invoice_line_tax_id,
#                        })
#                    
#                    res.append({
#                        'type':'src',
#                        'name': i_line.name[:64],
#                        'price_unit':i_line.product_id.product_tmpl_id.standard_price,
#                        'quantity':i_line.quantity,
#                        'price': -1 * i_line.product_id.product_tmpl_id.standard_price * i_line.quantity,
#                        'account_id':cacc,
#                        'product_id':i_line.product_id.id,
#                        'uos_id':i_line.uos_id.id,
#                        'account_analytic_id':i_line.account_analytic_id.id,
#                        'taxes':i_line.invoice_line_tax_id,
#                        })
#        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: