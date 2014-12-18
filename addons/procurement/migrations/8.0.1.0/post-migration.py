# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 ONESTEiN B.V.
#              (C) 2014 Therp BV
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

from openerp.openupgrade import openupgrade, openupgrade_80
from openerp import pooler, SUPERUSER_ID


def post_messages(cr, pool):
    """ The obsolete message and note fields on procurements are replaced
    by posting messages on the chatter. Posting existing messages here."""
    procurement_obj = pool['procurement.order']
    for field in ('note', 'message'):
        cr.execute(
            """
            SELECT id, {column} FROM procurement_order
            WHERE {column} IS NOT NULL AND {column} != ''
            """.format(column=openupgrade.get_legacy_name(field)))
        for proc_id, message in cr.fetchall():
            procurement_obj.message_post(
                cr, SUPERUSER_ID, [proc_id], body=message)


def process_states(cr):
    """Map obsolete active states to 'running' and let the scheduler decide
    if these procurements are actually 'done'. Warn if there are procurements
    in obsolete draft state"""
    openupgrade.logged_query(
        cr, "UPDATE procurement_order SET state = %s WHERE state in %s",
        ('running', ('ready', 'waiting')))
    cr.execute(
        "SELECT COUNT(*) FROM procurement_order WHERE state = 'draft'")
    count = cr.fetchone()[0]
    if count:
        openupgrade.message(
            cr, 'procurement', 'procurement_order', 'state',
            'In this database, %s procurements are in draft state. In '
            'Odoo 8.0, these procurements cannot be processed further.',
            count)


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    post_messages(cr, pool)
    openupgrade_80.set_message_last_post(
        cr, SUPERUSER_ID, pool, ['procurement.order'])
    process_states(cr)
