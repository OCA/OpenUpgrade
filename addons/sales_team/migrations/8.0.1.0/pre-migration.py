# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sales_team migration module for Odoo
#    copyright: 2014-Today GRAP
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

from openerp.openupgrade import openupgrade

xmlid_renames = [
    ('crm.section_sales_department', 'sales_team.section_sales_department'),
]


@openupgrade.migrate(no_version=True)
def migrate(cr, version):
    openupgrade.rename_xmlids(cr, xmlid_renames)

    # Test fixup: there is a demo section in 7.0 with the same code as a
    # section that is included in this module, violating the uniqueness
    # constraint.
    cr.execute("UPDATE crm_case_section SET code = '_DM' WHERE code = 'DM'")
