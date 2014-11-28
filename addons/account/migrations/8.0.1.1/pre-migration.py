# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Akretion (http://www.akretion.com/)
#    @author: Alexis de Lattre <alexis.delattre@akretion.com>
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

column_renames = {
    'account_bank_statement_line': [
        ('analytic_account_id', None),
        ('type', None),
    ]
}

tables_renames = [
    (
        'account_bank_statement_line_move_rel',
        'bak_account_bank_statement_line_move_rel'
    ),
]


@openupgrade.migrate()
def migrate(cr, version):
    if not version:
        return

    cr.execute(
        """SELECT id FROM account_analytic_journal WHERE type='purchase' """)
    res = cr.fetchone()
    if res:
        openupgrade.add_xmlid(
            cr, 'account', 'exp', 'account.analytic.journal', res[0], True)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, tables_renames)
    # drop views that inhibit changing field types. They will be recreated
    # anyways
    for view in [
            'analytic_entries_report', 'account_entries_report',
            'report_invoice_created', 'report_aged_receivable']:
        cr.execute('drop view if exists %s cascade' % view)
