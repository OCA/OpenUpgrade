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

class product_category(osv.osv):
    _inherit = "product.category"
    _columns = {
        'property_account_creditor_price_difference_categ': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Price Difference Account",
            method=True,
            view_load=True,
            help="This account will be used to value price difference between purchase price and cost price."),                
#        'property_account_received_goods_categ': fields.property(
#            'account.account',
#            type='many2one',
#            relation='account.account',
#            string="Incoming goods",
#            method=True,
#            view_load=True,
#            help="This account will be used to value incoming stock for the current product category"),
#        'property_account_sending_goods_categ': fields.property(
#            'account.account',
#            type='many2one',
#            relation='account.account',
#            string="Outgoing goods",
#            method=True,
#            view_load=True,
#            help="This account will be used to value outgoing stock for the current product category"),
    }
product_category()

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'property_account_creditor_price_difference': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Price Difference Account",
            method=True,
            view_load=True,
            help="This account will be used to value price difference between purchase price and cost price."),                
#        'property_account_received_goods': fields.property(
#            'account.account',
#            type='many2one',
#            relation='account.account',
#            string="Incoming goods",
#            method=True,
#            view_load=True,
#            help="This account will be used instead of the default one to value incoming stock for the current product"),
#        'property_account_sending_goods': fields.property(
#            'account.account',
#            type='many2one',
#            relation='account.account',
#            string="Outgoing goods",
#            method=True,
#            view_load=True,
#            help="This account will be used instead of the default one to value outgoing stock for the current product"),
    }
product_template()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

