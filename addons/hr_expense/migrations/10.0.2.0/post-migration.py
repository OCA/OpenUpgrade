# -*- coding: utf-8 -*-
# Copyright 2017 Le Filament (<https://le-filament.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    # Create new expense sheet for each expense registered
    cr.execute(
        '''INSERT INTO hr_expense_sheet
        (account_move_id, bank_journal_id, company_id, create_date,
        create_uid, currency_id, department_id, employee_id, journal_id,
        message_last_post, name, state, total_amount, write_date, write_uid)
        SELECT
            account_move_id, bank_journal_id, company_id, create_date,
            create_uid, currency_id, department_id, employee_id, journal_id,
            message_last_post, name, state, total_amount, write_date, write_uid
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

    # Set address for each employee
    cr.execute(
        '''UPDATE hr_expense_sheet
        SET address_id = subquery.address_home_id
        FROM (
            SELECT address_home_id, id
            FROM hr_employee
        ) AS subquery
        WHERE employee_id = subquery.id
        ''')

    # Set responsible for each expense by setting to department manager when department is filled in
    cr.execute(
        '''UPDATE hr_expense_sheet
        SET responsible_id = subquery.manager_id
        FROM (
            SELECT manager_id, id
            FROM hr_department
        ) AS subquery
        WHERE department_id = subquery.id
        ''')

    # Set correct reported state for hr_expense
    cr.execute(
        '''UPDATE hr_expense
        SET state='reported'
        WHERE state='submit' or state='approved'
        ''')

    # Set correct done state for hr_expense
    cr.execute(
        '''UPDATE hr_expense
        SET state='done'
        WHERE state='post' or state='done'
        ''')

    # Set correct refused state for hr_expense
    cr.execute(
        '''UPDATE hr_expense
        SET state='refused'
        WHERE state='cancel'
        ''')

    # Set correct account corresponding to product subject to this expense
    cr.execute(
        '''SELECT distinct he.product_id, pp.product_tmpl_id
        FROM hr_expense he, product_product pp
        WHERE he.product_id=pp.id
        ''')
    product_ids = cr.fetchall()
    for product in product_ids:
        product_template = "'product_template," + str(product[1]) + "'"
        cr.execute(
           '''UPDATE hr_expense
           SET account_id=(
                SELECT to_number(substring(value_reference from 17),'99999')
                FROM ir_property
                WHERE res_id like %s limit 1)
           WHERE product_id=%s
           ''' % (product_template, product[0], ))

    # Set accounting_date to date from account_analytic_line when it exists
    cr.execute(
        '''UPDATE hr_expense_sheet hes
        SET accounting_date = am.date
        FROM account_move am
        WHERE hes.account_move_id = am.id;
        ''')
    openupgrade.load_data(
        cr, 'hr_expense', 'migrations/10.0.2.0/noupdate_changes.xml')
