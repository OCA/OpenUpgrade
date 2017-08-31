# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    # Insert appropiate enties in account_reconcile_model_template
    cr.execute(
        '''INSERT INTO account_reconcile_model_template
        (create_uid, create_date, write_uid, write_date,
         name, sequence, has_second_line,
         account_id, label, tax_id, amount_type, amount,
        second_account_id, second_label, second_tax_id, second_amount_type,
        second_amount)
        SELECT
        MIN(create_uid), MIN(create_date), MAX(write_uid), MAX(write_date),
         name, sequence, has_second_line,
         account_id, label, tax_id, amount_type, amount,
        second_account_id, second_label, second_tax_id, second_amount_type,
        second_amount
        FROM account_reconcile_model
        GROUP BY
         name, sequence, has_second_line,
         account_id, label, tax_id, amount_type, amount,
        second_account_id, second_label, second_tax_id, second_amount_type,
        second_amount
        ''')
    # Update move_name in account_payment from account_move
    cr.execute(
        '''UPDATE account_payment
        SET move_name = subquery.name
        FROM (SELECT DISTINCT ON (aml.payment_id) am.name, aml.payment_id
              FROM account_move am
              JOIN account_move_line aml ON am.id = aml.move_id
              WHERE NOT aml.payment_id IS NULL
              ORDER BY aml.payment_id, am.name
             ) AS subquery
        WHERE account_payment.id = subquery.payment_id
        ''')
    # Move old rate_diff_partial_rec_id in account_move to
    # exchange_partial_rec_id in account_full_reconcile:
    cr.execute(
        '''UPDATE account_full_reconcile
        SET exchange_partial_rec_id = subquery.rate_diff_partial_rec_id
        , exchange_move_id = subquery.move_id
        FROM (
            SELECT
                apr.full_reconcile_id,
                am.rate_diff_partial_rec_id,
                am.id as move_id
            FROM account_partial_reconcile apr
            JOIN account_move am
            ON apr.id = am.rate_diff_partial_rec_id
        ) AS subquery
        WHERE account_full_reconcile.id = subquery.full_reconcile_id
        ''')
    # Update move_name on account_bank_statement_line:
    cr.execute(
        '''UPDATE account_bank_statement_line
        SET move_name = subquery.name
        FROM (
            SELECT
                am.name,
                am.statement_line_id
            FROM account_move am
        ) AS subquery
        WHERE account_bank_statement_line.id = subquery.statement_line_id
        ''')
    openupgrade.load_data(
        cr, 'account', 'migrations/10.0.1.1/noupdate_changes.xml',
    )
