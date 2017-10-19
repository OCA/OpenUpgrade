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
        MIN(arm.create_uid), MIN(arm.create_date), MAX(arm.write_uid),
        MAX(arm.write_date), arm.name, arm.sequence, arm.has_second_line,
        act1.id, arm.label, att1.id, arm.amount_type, arm.amount,
        act2.id, arm.second_label, att2.id,
        arm.second_amount_type, arm.second_amount
        FROM account_reconcile_model as arm
        LEFT JOIN (SELECT id, name, type_tax_use
                   FROM account_tax
                   ) as at1
        ON at1.id = arm.tax_id
        LEFT JOIN (SELECT id, name, type_tax_use
              FROM account_tax_template
              ) as att1
        ON (att1.name = at1.name AND
            att1.type_tax_use = at1.type_tax_use)
        LEFT JOIN (SELECT id, name, code
                   FROM account_account) as acc1
        ON acc1.id = arm.account_id
        LEFT JOIN (SELECT id, name, code
                   FROM account_account_template) as act1
        ON (acc1.name = act1.name
            AND acc1.code = act1.code)
        LEFT JOIN (SELECT id, name, type_tax_use
                   FROM account_tax
                   ) as at2
        ON at2.id = arm.second_tax_id
        LEFT JOIN (SELECT id, name, type_tax_use
              FROM account_tax_template
              ) as att2
        ON (att2.name = at2.name AND
            att2.type_tax_use = at2.type_tax_use)
        LEFT JOIN (SELECT id, name, code
                   FROM account_account) as acc2
        ON acc2.id = arm.second_account_id
        LEFT JOIN (SELECT id, name, code
                   FROM account_account_template) as act2
        ON (acc2.name = act2.name
            AND acc2.code = act2.code)
        GROUP BY
         arm.name, arm.sequence, arm.has_second_line,
         act1.id, arm.label, att1.id, arm.amount_type, arm.amount,
         act2.id, arm.second_label, att2.id,
         arm.second_amount_type, arm.second_amount
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
