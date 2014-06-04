# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, a suite of business apps
#    This module Copyright (C) 2014 Therp BV (<http://therp.nl>).
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

from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID as uid
from openerp.openupgrade import openupgrade, openupgrade_80


def task_priority(cr):
    """
    Mapping old priorities to the new range
    """
    legacy_priority = openupgrade.get_legacy_name('priority')
    for old, new in [(4, 0), (3, 0), (2, 1), (1, 2), (0, 2)]:
        openupgrade.logged_query(
            cr, """
            UPDATE project_task SET priority = %s
            WHERE """ + legacy_priority + " = %s",
            (new, old))


@openupgrade.migrate()
def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    task_priority(cr)
    openupgrade_80.set_message_last_post(
        cr, uid, registry, ['project.project', 'project.task']
    )
    openupgrade.load_data(cr, 'project', 'migrations/8.0.1.1/noupdate_changes.xml')
