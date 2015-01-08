# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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

from openerp.openupgrade import openupgrade, openupgrade_80
from openerp.modules.registry import RegistryManager
from openerp import SUPERUSER_ID


def migrate_date_order(cr):
    """ Take the related user's timezone into account when converting
    date field to datetime."""
    cr.execute(
        """
        SELECT distinct(rp.tz)
        FROM sale_order so, res_users ru, res_partner rp
        WHERE rp.tz IS NOT NULL
            AND so.user_id=ru.id
            AND ru.partner_id=rp.id
        """)
    for timezone, in cr.fetchall():
        cr.execute("SET TIMEZONE=%s", (timezone,))
        openupgrade.logged_query(
            cr,
            """
            UPDATE sale_order so
            SET date_order={date_order}::TIMESTAMP AT TIME ZONE 'UTC'
            FROM res_partner rp, res_users ru
            WHERE {date_order} IS NOT NULL
                AND so.user_id=ru.id
                AND ru.partner_id=rp.id
                AND rp.tz=%s;
            """.format(date_order=openupgrade.get_legacy_name('date_order')),
            (timezone,))
    cr.execute("RESET TIMEZONE")


@openupgrade.migrate()
def migrate(cr, version):
    registry = RegistryManager.get(cr.dbname)
    openupgrade.load_data(
        cr, 'sale', 'migrations/8.0.1.0/noupdate_changes.xml')
    openupgrade_80.set_message_last_post(
        cr, SUPERUSER_ID, registry, ['sale.order'])
    migrate_date_order(cr)
