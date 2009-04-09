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
    'name': 'Pro-forma invoices and their payments Management',
    'version': '1.0',
    'category': 'Generic Modules/Accounting',
    'description': """
        Once a pro-forma invoice is created, the module sends automatically mail 
        and call actions after X days.
        It's the same principle than account_followup but for proforma invoice only. 
        Only followups by email, no need to do reports. 
        Also, at each steps, we should be able to call several functions. 
        (for example, if a pro-forma is canceled, it will close a delivery order)
""",
    'author': 'Tiny',
    'website': 'http://www.openerp.com',
    'depends': ['account'],
    'init_xml': [],
    'update_xml': [
        'proforma_followup_view.xml',
        'proforma_followup_data.xml',
    ],
    'demo_xml': ['proforma_followup_demo.xml',],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
