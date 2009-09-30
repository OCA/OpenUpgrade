#!/usr/bin/env python
#-*- coding:utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    d$
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
    "name" : "Multi-Currency Invoice",
    "version" : "1.1",
    "depends" : ["account"],
    "author" : "Tiny",
    "description": """Multi-Currency Invoice
    that will allows user to change the invoice currency.
    """,
    'author': 'Tiny',
    'website': 'http://www.openerp.com',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': [
        "invoice_multi_currency_wizard.xml",
        "invoice_multi_currency_view.xml"
    ],
    'demo_xml': [
        
    ],
    'installable': True,
    'active': False,
}
