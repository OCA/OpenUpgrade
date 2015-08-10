# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2013 Sylvain LE GAL
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
from openerp.openupgrade import openupgrade


def migrate_hr_expense_account_move(cr, pool):
    """
    Fill the field account_move_id with account_invoice information.
    """
    cr.execute("""
        UPDATE hr_expense_expense e
        SET account_move_id=i.move_id
        FROM account_invoice i
        WHERE e.account_move_id is Null AND e.{0}=i.id
        """.format(openupgrade.get_legacy_name('invoice_id')))


def migrate_hr_expense_expense_ref(cr, pool):
    """
    Join existing 'note' values and obsolete 'ref' values into
    text field 'note' on the 'hr.expense.expense' model.
    """
    expense_obj = pool.get('hr.expense.expense')
    cr.execute("""
        SELECT id, {0}, {1}
        FROM hr_expense_expense
        WHERE {1} is not NULL AND {1} != ''
        """.format('note',
                   openupgrade.get_legacy_name('ref')))
    for (expense_id, note, ref) in cr.fetchall():
        note = note + '\n' if note else ''
        expense_obj.write(
            cr, SUPERUSER_ID, [expense_id],
            {'note': note + ref})


def set_hr_expense_line_uom(cr, pool):
    line_obj = pool.get('hr.expense.line')
    product_obj = pool.get('product.product')
    cr.execute("""
        SELECT id, product_id
        FROM hr_expense_line
        WHERE uom_id is Null
        """)
    for (line_id, product_id) in cr.fetchall():
        if product_id:
            uom_id = product_obj.browse(
                cr, SUPERUSER_ID, product_id, context=None).uom_id.id
        else:
            uom_id = line_obj._get_uom_id(cr, SUPERUSER_ID, context=None)
        line_obj.write(
            cr, SUPERUSER_ID, [line_id],
            {'uom_id': uom_id})


def migrate_hr_expense_expense_state(cr, pool):
    """
    Change obsolete 'state' values for hr_expense_expense.state;
    Manage workflow modifications.
    """
    model_obj = pool.get('ir.model.data')

    # recover compatible states
    cr.execute("""
        UPDATE hr_expense_expense
        SET state = {0}
        WHERE {0} != 'invoiced'
        """.format(openupgrade.get_legacy_name('state')))

    # set 'done' state instead of 'invoiced'
    cr.execute("""
        UPDATE hr_expense_expense
        SET state = 'done'
        WHERE {0} = 'invoiced'
        """.format(openupgrade.get_legacy_name('state')))

    # change wkf items that are in state 'paid' and 'invoiced',
    # setting act_id to act_done id. (before was act_paid id);
    act_done_id = model_obj.get_object(
        cr, SUPERUSER_ID, 'hr_expense', 'act_done').id
    cr.execute("""
        UPDATE wkf_workitem
        SET act_id = {0}
        WHERE inst_id IN (
            SELECT id
            FROM wkf_instance
            WHERE res_type='hr.expense.expense' AND res_id in (
                SELECT id
                FROM hr_expense_expense
                WHERE {1} in ('paid', 'invoiced')
            )
        );""".format(act_done_id,
                     openupgrade.get_legacy_name('state')))

    # Change wkf workitems from subflow to function
    cr.execute("""
        UPDATE wkf_workitem
        SET subflow_id = Null, state='complete'
        WHERE inst_id IN (
            SELECT id
            FROM wkf_instance
            WHERE res_type='hr.expense.expense' AND res_id in (
                SELECT id
                FROM hr_expense_expense
                WHERE {0}='invoiced'
            )
        );""".format(openupgrade.get_legacy_name('state')))

    # No more flow_end in hr_expense worfklow
    cr.execute("""
    UPDATE wkf_instance
        SET state='active'
        WHERE res_type='hr.expense.expense' AND res_id in (
            SELECT id
            FROM hr_expense_expense
            WHERE {0}='paid');""".format(openupgrade.get_legacy_name('state')))

    # Demote state of formerly 'invoiced' expenses for which no move was found
    # above
    cr.execute("""
    UPDATE hr_expense_expense
    SET state='accepted'
    WHERE account_move_id IS NULL AND {0}='invoiced'""".format(
        openupgrade.get_legacy_name('state')))
    # And adjust their workflow items in order to be able to do something
    # useful with them afterwards
    act_accepted_id = model_obj.get_object(
        cr, SUPERUSER_ID, 'hr_expense', 'act_accepted').id
    cr.execute("""
        UPDATE wkf_workitem
        SET act_id = {0}
        WHERE inst_id IN (
            SELECT id
            FROM wkf_instance
            WHERE res_type='hr.expense.expense' AND res_id in (
                SELECT id
                FROM hr_expense_expense
                WHERE {1}='invoiced' AND account_move_id IS NULL
            )
        );""".format(act_accepted_id, openupgrade.get_legacy_name('state')))


@openupgrade.migrate()
def migrate(cr, version):
    pool = pooler.get_pool(cr.dbname)
    migrate_hr_expense_account_move(cr, pool)
    migrate_hr_expense_expense_ref(cr, pool)
    set_hr_expense_line_uom(cr, pool)
    migrate_hr_expense_expense_state(cr, pool)
