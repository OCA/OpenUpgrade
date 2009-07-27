# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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

from osv import osv,fields

class company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'pos_warn_virtual_stock': fields.boolean('No virtual stock warning',
            help="Shows a warning if there is not enough virtual stock in any of the products."),
        'pos_warn_sale_order': fields.boolean('Product in sale order warning',
            help="Shows a warning if a product added in the POS order has already been requested by the partner (the partner has a sale order with this product), so the user can decide if is better to do a POS order from a sale order."),
        'pos_prices_tax_include': fields.boolean('Prices tax included',
            help="Product prices have tax included."),
        'pos_journals': fields.many2many('account.journal', 'company_pos_journal_rel', 'journal_id', 'company_id', 'Payment journals', help="The journals used to pay with the POS.", domain="[('type', '=', 'cash')]"),
    }
    _defaults = {
        'pos_warn_virtual_stock': lambda *a: True,
        'pos_warn_sale_order': lambda *a: True,
        'pos_prices_tax_include': lambda *a: True,
    }
company()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
