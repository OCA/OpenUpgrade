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
    'name': 'Import accounting entries from Bob',
    'description': """
        This module provide an easy way to migrate your financial data from Bob software to OpenERP. It includes the import of
            * chart of accounts,
            * financial journals,
            * customers, suppliers and prospects,
            * contacts,
            * accounting entries

        Once the module is installed, all you have to do is run the configuration wizard and provide OpenERP the location of the Bob directory where is your data.
""",
    'category': 'Data Module',
    'init_xml':[],
    'author': 'Tiny',
    'depends': ['base_contact','account_l10nbe_domiciliation','l10n_be'],
    'version': '1.0',
    'active': False,
    'demo_xml': [],
    'update_xml':[
        'security/ir.model.access.csv',
        'misc_data.xml',
        'account_bob_import_config.xml',
    ],
    'installable': True,

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

