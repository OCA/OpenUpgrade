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
    "name" : "EZ Publish eCommerce Interface",
    "version" : "1.0",
    "author" : "Tiny",
    "category" : "Interfaces/CMS & eCommerce",
    "website" : "http://www.openerp.com",
    "description": "Module to interface with the EZ Publish ecommerce system.",
    "depends" : ["product", "stock", "sale"],
    "init_xml" : [],
    "demo_xml" : ["esale_demo.xml"],
    "update_xml" : ["esale_view.xml"],
    "active": False,
    "installable": False
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

