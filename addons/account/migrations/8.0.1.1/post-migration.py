# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Akretion
#    (<http://www.akretion.com>).
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

from itertools import groupby

from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade, openupgrade_80


def update_link_to_moves(cr):
    cr.execute('''
        SELECT statement_line_id, move_id
        FROM bak_account_bank_statement_line_move_rel
        ORDER BY statement_line_id;
    ''')
    rows = cr.fetchall()
    for k, v in groupby(rows, key=lambda r: r[0]):
        v = list(v)
        assert len(v) == 1
        openupgrade.logged_query(
            cr,
            '''UPDATE account_bank_statement_line
            SET journal_entry_id = %s
            WHERE id = %s;''',
            args=(v[0][1], v[0][0])
        )


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    uid = SUPERUSER_ID
    openupgrade_80.set_message_last_post(
        cr, uid, pool, ['account.bank.statement', 'account.invoice']
    )
    update_link_to_moves(cr)
