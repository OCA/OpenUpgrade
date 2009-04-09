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
    "name" : "Products Lot Foundry",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Enterprise Specific Modules/Metal Industries",
    "depends" : ["base", "account", "product", "stock", "sale"],
    "init_xml" : [],
    "demo_xml" : ["product_lot_foundry_demo.xml"],
    "description": "Lots management for a metal company: cutting, heatcode, sizes",
    "update_xml" : ["security/ir.model.access.csv","product_lot_foundry_view.xml","sale_order_view.xml"],
    "active": False,
    "installable": True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

