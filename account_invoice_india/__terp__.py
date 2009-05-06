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
    "name" : "Accounting Base Configuration and Properties",
    "version" : "1.0",
    "depends" : [
        "base",
        "account",
    ],
    "author" : 'Tiny & Axelor',
    "description": """Accounting Base Properties Reports and Wizards,
    Basic properties for the Customer / Suppliers for the Accounting
    Wizards to Allowd to create a Party Accounts, 
    Reports that provides Indian Accounting Reports for Invoice
    """,
    "website" : "http://tinyerpindia.com",
    "category" : "Generic Modules/Indian Accounting",
    "init_xml" : [
    ],
    "demo_xml" : [
    ],
    "update_xml" : [
        "account_sequence.xml",
       "account_report.xml",
       "account_wizard.xml",
       "account_invoice_view.xml"
    ],
    "active": False,
    "installable": True
}
