# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Therp BV (<http://therp.nl>).
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

from openerp import pooler, SUPERUSER_ID
from openerp.openupgrade import openupgrade, openupgrade_70

def migrate_invoice_addresses(cr, pool):
    # Contact id takes precedence over old partner id
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'account.invoice',
        'partner_id', openupgrade.get_legacy_name('address_contact_id'))
    # Invoice id takes precedence over contact id
    openupgrade_70.set_partner_id_from_partner_address_id(
        cr, pool, 'account.invoice',
        'partner_id', openupgrade.get_legacy_name('address_invoice_id'))

def migrate_invoice_names(cr, pool):
    """
    Join existing char values and obsolete note values into
    new text field name on the invoice line.
    """
    invoice_line_obj = pool.get('account.invoice.line')
    note_column = openupgrade.get_legacy_name('note')
    cr.execute(
        """
        SELECT id, %s, %s
        FROM account_invoice_line
        WHERE %s is not NULL
        AND %s != ''
        """ % (openupgrade.get_legacy_name('name'),
               note_column, note_column, note_column))
    for (invoice_line_id, name, note) in cr.fetchall():
        prefix = (name + '\n') if name else ''
        invoice_line_obj.write(
            cr, SUPERUSER_ID, [invoice_line_id],
            {'name': prefix + note})

def lock_closing_reconciliations(cr, pool):
    """
    Reconciliations on closing entries are now locked
    for deletion. Therefore, lock existing closing entries.
    """
    fiscalyear_obj = pool.get('account.fiscalyear')
    period_obj = pool.get('account.period')
    move_line_obj = pool.get('account.move.line')
    reconcile_obj = pool.get('account.move.reconcile')
    for fiscalyear_id in fiscalyear_obj.search(
            cr, SUPERUSER_ID, []):
        move_line_ids = move_line_obj.search(
            cr, SUPERUSER_ID,
            [('period_id.special', '=', True),
             ('period_id.fiscalyear_id', '=', fiscalyear_id)])
        reconcile_ids = reconcile_obj.search(
            cr, SUPERUSER_ID,
            [('line_id', 'in', move_line_ids)])
        reconcile_obj.write(
            cr, SUPERUSER_ID, reconcile_ids,
            {'opening_reconciliation': True})

@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_invoice_addresses(cr, pool)
    migrate_invoice_names(cr, pool)
    lock_closing_reconciliations(cr, pool)
    openupgrade.load_xml(
        cr, 'account',
        'migrations/7.0.1.1/data.xml')
