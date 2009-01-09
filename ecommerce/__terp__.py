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
    "name" : "E-Commerce",
    "version" : "1.0",
    "author" : "e-tiny",
    "website" : "http://www.etiny.com",
    "depends" : ["delivery","base", "product","sale"],
    "category" : "Generic Modules/E-Commerce Shop",
    "init_xml" : [],
    "demo_xml" : ["ecommerce_demo_data.xml"],
    "description": """eCommerce Users can order on the website, orders are automatically imported in TinyERP.
                      You can configure products, categories of products, language, currency, carrier, payment
                      and also configure row,column,images.""",

    "update_xml" : [
                    "tools/ecom_product_view.xml",
                    "basic_info_view.xml",
                    "catalog/catalog_view.xml",
                    "tools/tools_wizard.xml",
                    "partner/partner_new_view.xml",
                    "sale_order/sale_order_view.xml",
                    "sale_order/sale_order_sequence.xml",
                    "report_shipping.xml", 
                  #  "security/ir.model.access.csv"                            
   ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

