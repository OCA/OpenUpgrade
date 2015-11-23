# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association
#    @author: Sylvain LE GAL <https://twitter.com/legalsylvain>
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

import logging
from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade
logger = logging.getLogger('OpenUpgrade')

# copied from pre-migration
column_copies = {
    'project.task': [
        ('description', None, None),
    ],
}


# TODO - match company_type to is_company
def match_company_type_to_is_company(cr):
    cr.execute("""
        UPDATE res_partner
        SET company_type = (CASE WHEN is_company THEN 'company' ELSE 'person' END)
        """)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    for table_name in column_spec.keys():
        for (old, new, field_type) in column_spec[table_name]:
            convert_field_to_html(cr, table_name, get_legacy_name(old), old)
    match_company_type_to_is_company(cr)
