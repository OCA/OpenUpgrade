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
    "name" : "eSale Interface - Joomla",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Interfaces/CMS & eCommerce",
    "website" : "http://www.openerp.com",
    "depends" : ["product", "stock", "sale", "account", "account_tax_include",],
    "description": """Joomla (Virtuemart) eCommerce interface synchronisation.
Users can order on the website, orders are automatically imported in Tiny
ERP.

You can export products, product's categories, account taxes,  stock level and create links between
categories of products, taxes and languages.

If you product has an image attched, it send the image to the Joomla website.""",
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
            "security/esale_joomla_security.xml",
           # "security/ir.model.access.csv",
            "esale_joomla_view.xml",
            "esale_joomla_wizard.xml",
    ],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

