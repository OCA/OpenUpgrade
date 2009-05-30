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
    "name" : "Accounting Base Properties",
    "version" : "1.0",
    "depends" : [
        "base",
    ],
    "author" : 'Tiny & Axelor',
    "description": """Accounting Base Properties is providing the,
    Basic properties for the Customer / Suppliers for the Accounting
    i.e. PAN No, TIN No, Sales Tax No, and Exise related Information
    """,
    "website" : "http://tinyerpindia.com",
    "category" : "Generic Modules/Indian Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "partner_view.xml",
        "wizard/account_setup_view.xml"
    ],
    "active": False,
    "installable": True
}
