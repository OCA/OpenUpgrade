# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This migration script copyright (C) 2012 Therp BV (<http://therp.nl>)
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

import pooler
from openupgrade import openupgrade

def migrate_picking_journal(cr, pool):
    """
    Sale picking journals are now stock journals,
    defined in the stock module
    """
    stock_journal_obj = pool.get('stock.journal')
    cr.execute("""
        SELECT id, name, user_id
        FROM sale_journal_picking_journal
        """)
    journal_map = []
    for (sale_journal_id, name, user_id) in cr.fetchall():
        stock_journal_id = stock_journal_obj.create(
            cr, 1, {'name': name, 'user_id': user_id})
        journal_map.append((sale_journal_id, stock_journal_id))
    for (sale_journal_id, stock_journal_id) in journal_map:
        cr.execute(
            "UPDATE stock_picking "
            "SET stock_journal_id = %s "
            "WHERE " + openupgrade.get_legacy_name('journal_id') + " = %s",
            (stock_journal_id, sale_journal_id)
            )

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_picking_journal(cr, pool)
