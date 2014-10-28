# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, a suite of business apps
# This module Copyright (C) 2014 Therp BV (<http://therp.nl>).
#    @contributor: Onestein <www.onestein.nl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import pooler, SUPERUSER_ID as uid
from openerp.openupgrade import openupgrade, openupgrade_80


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)

    openupgrade.map_values(
        cr,
        openupgrade.get_legacy_name('priority'),
        'priority',
        [('4', '0'), ('3', '0'), ('2', '1'), ('1', '2'), ('0', '2')],
        table='project_issue', write='sql')

    openupgrade_80.set_message_last_post(cr, uid, pool, ['project.issue'])

    openupgrade.load_data(
        cr, 'project_issue', 'migrations/8.0.1.0/noupdate_changes.xml')
