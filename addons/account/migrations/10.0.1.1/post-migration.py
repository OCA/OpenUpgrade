# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_refund_invoice_id(env):
    """This method fills the new field refund_invoice_id in invoices using
    the information of the OCA/account-invoicing module
    account_invoice_refund_link if present.
    """
    if not openupgrade.table_exists(env.cr, 'account_invoice_refunds_rel'):
        return
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_invoice ai
        SET refund_invoice_id = rel.original_invoice_id
        FROM account_invoice_refunds_rel rel
        WHERE rel.refund_invoice_id = ai.id"""
    )
    # TODO: Make a fuzzy match if the OCA module is not present


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
    openupgrade.logged_query(
        cr, """UPDATE account_payment ap
        SET move_name = am.name
        FROM account_move_line aml
        INNER JOIN account_move am ON am.id = aml.move_id
        WHERE ap.move_name IS NULL
            AND aml.payment_id = ap.id""",
    )
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
    openupgrade.logged_query(
        cr, """UPDATE account_bank_statement_line absl
        SET move_name = am.name
        FROM account_move am
        WHERE absl.id = am.statement_line_id
        AND absl.move_name IS NULL"""
    )
    fill_refund_invoice_id(env)
    openupgrade.load_data(
        cr, 'account', 'migrations/10.0.1.1/noupdate_changes.xml',
    )
