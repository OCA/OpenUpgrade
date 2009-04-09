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

{
    'name': 'E-Commerce',
    'version': '1.0',
    'author': 'Tiny',
    'website': 'http://www.openerp.com',
    'category': 'Generic Modules/E-Commerce',
    'depends': ['delivery'],
    'description': """
ecommerce users can order on the website, orders are automatically imported in OpenERP.

You can export products, product's categories, product images and create links between
categories of products, currency and languages to website.

Delivery of products manage by carriers.

Different payment methods are available for users to make payment.

You can display products in table on website using rows and columns specified in webshop.
                 """,
    'init_xml': [],
    'demo_xml': ['ecommerce_demo.xml'],
    'update_xml': [
        'ecommerce_wizard.xml',
        'ecommerce_view.xml',
        'partner/partner_view.xml',
        'catalog/catalog_view.xml',       
        'sale_order/sale_order_view.xml',
        'sale_order/sale_order_sequence.xml',
        'ecommerce_report.xml', 
        'security/ir.model.access.csv'
    ],
    'installable': True,
    'active': False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
