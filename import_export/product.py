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

#----------------------------------------------------------
# Products
#----------------------------------------------------------
class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'taxes_id': fields.many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id', 'Product Taxes', domain=[('parent_id','=',False)]),

        'property_account_income_europe': fields.property(
          'account.account',
          type='many2one',
          relation='account.account',
          string="Income Account for Europe",
          method=True,
          view_load=True,
          group_name="Accounting Properties",
          help="This account will be used, instead of the default one, to value incoming stock for the current product"),

        'property_account_expense_europe': fields.property(
          'account.account',
          type='many2one',
          relation='account.account',
          string="Expense Account for Europe",
          method=True,
          view_load=True,
          group_name="Accounting Properties",
          help="This account will be used, instead of the default one, to value outgoing stock for the current product"),

        'property_account_income_world': fields.property(
          'account.account',
          type='many2one',
          relation='account.account',
          string="Outside Europe Income Account",
          method=True,
          view_load=True,
          group_name="Accounting Properties",
          help="This account will be used, instead of the default one, to value incoming stock for the current product"),

        'property_account_expense_world1': fields.property(
          'account.account',
          type='many2one',
          relation='account.account',
          string="Outside Europe Expense Account",
          method=True,
          view_load=True,
          group_name="Accounting Properties",
          help="This account will be used, instead of the default one, to value outgoing stock for the current product"),
    }

#end class
product_template()


class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {

        'property_account_income_europe': fields.property(
          'account.account',
          type='many2one',
          relation='account.account',
          string="Income Account for Europe",
          method=True,
          view_load=True,
          group_name="Accounting Properties",
          help="This account will be used, instead of the default one, to value incoming stock for the current product"),

        'property_account_expense_europe': fields.property(
          'account.account',
          type='many2one',
          relation='account.account',
          string="Expense Account for Europe",
          method=True,
          view_load=True,
          group_name="Accounting Properties",
          help="This account will be used, instead of the default one, to value outgoing stock for the current product"),

        'property_account_income_world': fields.property(
          'account.account',
          type='many2one',
          relation='account.account',
          string="Outside Europe Income Account",
          method=True,
          view_load=True,
          group_name="Accounting Properties",
          help="This account will be used, instead of the default one, to value incoming stock for the current product"),

        'property_account_expense_world': fields.property(
          'account.account',
          type='many2one',
          relation='account.account',
          string="Outside Europe Expense Account",
          method=True,
          view_load=True,
          group_name="Accounting Properties",
          help="This account will be used, instead of the default one, to value outgoing stock for the current product"),
    }
#end class
product_category()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

