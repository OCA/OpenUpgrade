# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
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
    'name': 'Business Process for Accounting Voucher',
    'version': '1.0',
    'category': 'Generic Modules/Indian Accounting',
    'description': """Business process for the Accounting Voucher
    We can define the rules for voucher > 1000 need Special Authorization
    """,
    'author': 'Tiny & Axelor',
    'website': 'http://tinyerpindia.com',
    'depends': [
        'account_voucher'
    ],
    'init_xml': [],
    'update_xml': [
        'account_voucher_workflow.xml',
        "account_voucher_view.xml"
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
