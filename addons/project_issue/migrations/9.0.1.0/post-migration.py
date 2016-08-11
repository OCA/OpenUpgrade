# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenUpgrade module for Odoo
#    @copyright 2014-Today: Odoo Community Association, Microcom
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

from openupgradelib import openupgrade
from openerp.modules.registry import RegistryManager

column_defaults = {
    'project.issue': [
        ('kanban_state', 'normal')
    ]
}


@openupgrade.migrate()
def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)

    openupgrade.set_defaults(cr, registry, column_defaults, force=False)
    openupgrade.load_data(
        cr, 'project_issue', 'migrations/9.0.1.0/noupdate_changes.xml')
