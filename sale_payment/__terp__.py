# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2008 Zikzakmedia S.L. (http://zikzakmedia.com) All Rights Reserved.
#                       Jordi Esteve <jesteve@zikzakmedia.com>
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
    "name" : "Sale payment type",
    "version" : "1.0",
    "author" : "Zikzakmedia",
    "website": "www.zikzakmedia.com",
    "license" : "GPL-3",
    "category" : 'Generic Modules/Sales & Purchases',
    "description": """Adds payment type and bank account to sale process.

The sale order inherits payment type and bank account (if the payment type is related to bank accounts) from partner as default. Next, the invoice based on this sale order inherits the payment information from it.

Also computes payment type and bank account of invoices created from picking lists (extracted from partner info).

Based on previous work of Readylan (version for 4.2).
""",
    "depends" : [
        "account_payment",
        "account_payment_extension",
        "sale",
        "stock",
        ],
    "init_xml" : [],
    "demo_xml" : [],
    "update_xml" : [
        "sale_payment_view.xml",
        ],
    "active": False,
    "installable": True
}
