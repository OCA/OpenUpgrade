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
    "name":"Indian Accounting Profile",
    "version":"1.0",
    "author": 'Tiny & Axelor',
    "description":"""Profile Indian Accounting
    * Chart of Account
    * Payment Receipt methods
    * Accunting Reports
    * Indian Payroll and Loan Management
    """,
    "website" : "http://tinyerpindia.com",
    'category': 'Profile',
    "depends":[
        "account_base",
        "l10n_chart_in",
        "account_voucher",
        "account_voucher_payment",
        "account_voucher_workflow",
    ],
    "demo_xml":[],
    "update_xml":[],
    "active":False,
    "installable":True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

