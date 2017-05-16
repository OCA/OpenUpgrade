# -*- coding: utf-8 -*-
# © 2017 Therp BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

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
