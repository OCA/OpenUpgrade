# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade
from psycopg2.extensions import AsIs


def map_expense_state(env):
    # Mapping values of state field for hr_expense.
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('state'), 'state',
        [('confirm', 'submit'), ('accepted', 'approve'), ('done', 'post'),
         ('paid', 'done'), ('cancelled', 'cancel')],
        table=openupgrade.get_legacy_name('hr_expense_expense'))


def hr_expense(env):
    """"Set remaining data from old hr_expense_expense table in hr_expense,
    that corresponds to the old hr_expense_line table.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense he
        SET company_id = ot.company_id,
            currency_id = ot.currency_id,
            journal_id = ot.journal_id,
            employee_id = ot.employee_id,
            state = ot.state,
            account_move_id = ot.account_move_id,
            payment_mode = 'own_account'
        FROM %(old_table)s ot
        WHERE ot.id = he.expense_id
        """, {
            'old_table': AsIs(
                openupgrade.get_legacy_name('hr_expense_expense')
            )
        },
    )
    Expense = env['hr.expense']
    expenses = Expense.search([])
    env.add_todo(Expense._fields['total_amount'], expenses)
    env.add_todo(Expense._fields['untaxed_amount'], expenses)
    Expense.recompute()


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    map_expense_state(env)
    hr_expense(env)
