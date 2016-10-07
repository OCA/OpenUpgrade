# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module Copyright (C) 2012-2014 OpenUpgrade community
#    https://launchpad.net/~openupgrade-committers
#
#    Contributors:
#    Therp BV <http://therp.nl>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'OpenUpgrade Records',
    'version': '0.2',
    'category': 'Normal',
    'description': """Allow OpenUpgrade records to be
stored in the database and compare with other servers.

This module depends on OpenERP client lib:

    easy_install openerp-client-lib

""",
    'author': 'OpenUpgrade Community',
    'maintainer': 'OpenUpgrade Community',
    'contributors': ['Therp BV'],
    'website': 'https://launchpad.net/~openupgrade-committers',
    'depends': [],
    'init_xml': [],
    'update_xml': [
        'view/openupgrade_record.xml',
        'view/comparison_config.xml',
        'view/analysis_wizard.xml',
        'view/generate_records_wizard.xml',
        'view/install_all_wizard.xml',
        'security/ir.model.access.csv',
        ],
    'demo_xml': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'external_dependencies': {
        'python': ['openerplib'],
        },
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
