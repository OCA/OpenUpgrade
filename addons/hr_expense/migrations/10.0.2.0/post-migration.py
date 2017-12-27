# -*- coding: utf-8 -*-
# Copyright 2017 Le Filament (<https://le-filament.com>)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def set_expense_sheet_address(env):
    """Set address for each employee."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense_sheet s
        SET address_id = e.address_home_id
        FROM hr_employee e
        WHERE s.employee_id = e.id""",
    )


def set_expense_responsible(env):
    """Set responsible on expenses by setting them to department manager user.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense_sheet s
        SET responsible_id = r.user_id
        FROM hr_department d,
             hr_employee e,
             resource_resource r
        WHERE s.department_id = d.id
            AND d.manager_id = e.id
            AND r.id = e.resource_id""",
    )


def set_expense_states(env):
    """Set correct states on hr.expense"""
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('state'), 'state', [
            ('submit', 'reported'),
            ('approved', 'reported'),
            ('post', 'done'),
            ('cancel', 'refused'),
        ], table='hr_expense',
    )


def fill_expense_product_account(env):
    """Set correct account corresponding to product subject to this expense."""
    for expense in env['hr.expense'].search([]):
        expense.account_id = expense.product_id.with_context(
            force_company=expense.company_id.id,
        ).product_tmpl_id._get_product_accounts()['expense']


def set_expense_sheet_accounting_date(env):
    """Set accounting_date to date from account move when it exists."""
    openupgrade.logged_query(
        env.cr, """
        UPDATE hr_expense_sheet hes
        SET accounting_date = am.date
        FROM account_move am
        WHERE hes.account_move_id = am.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    # Create new expense sheet for each expense registered
    # grouped by name and creation date
    cr.execute(
        '''INSERT INTO hr_expense_sheet
        (account_move_id, bank_journal_id, company_id, create_date,
        create_uid, currency_id, department_id, employee_id, journal_id,
        message_last_post, name, state, write_date, write_uid)
        SELECT DISTINCT ON (name, create_date)
            account_move_id, bank_journal_id, company_id, create_date,
            create_uid, currency_id, department_id, employee_id, journal_id,
            message_last_post, name, state, write_date, write_uid
        FROM hr_expense WHERE state != 'draft'
        ''')
    # Set sheet_id for each expense_id
    cr.execute(
        '''UPDATE hr_expense
        SET sheet_id = subquery.sheet_id
        FROM (
            SELECT hes.id AS sheet_id, he.id AS expense_id
            FROM hr_expense he, hr_expense_sheet hes
            WHERE he.name=hes.name and he.create_date=hes.create_date
        ) AS subquery
        WHERE id=subquery.expense_id
        ''')
    set_expense_sheet_address(env)
    set_expense_responsible(env)
    set_expense_states(env)
    fill_expense_product_account(env)
    set_expense_sheet_accounting_date(env)
    Sheet = env['hr.expense.sheet']
    sheets = Sheet.search([])
    env.add_todo(Sheet._fields['total_amount'], sheets)
    Sheet.recompute()
    openupgrade.load_data(
        cr, 'hr_expense', 'migrations/10.0.2.0/noupdate_changes.xml')
