# -*- coding: utf-8 -*-
# © 2016 Sylvain LE GAL <https://twitter.com/legalsylvain>
# © 2016 Serpent Consulting Services Pvt. Ltd.
# © 2016 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

column_renames = {
    'account_bank_statement': [
        ('closing_date', 'date_done'),
    ],
    'account_account_type': [
        ('close_method', None),
    ],
    'account_bank_statement_line': [
        ('journal_entry_id', None),
    ],
    'account_account': [
        ('type', None),
    ],
    'account_cashbox_line': [
        ('pieces', 'coin_value'),
        ('number_opening', None),
        ('number_closing', None),
        ('bank_statement_id', None),
    ]
}

column_copies = {
    'account_bank_statement': [
        ('state', None, None),
    ],
    'account_journal': [
        ('type', None, None),
    ],
    'account_tax': [
        ('type_tax_use', None, None),
    ],
    'account_tax_template': [
        ('type_tax_use', None, None),
    ],
}

table_renames = [
    ('account_statement_operation_template', 'account_operation_template'),
    ('account_tax_code', 'account_tax_group')]

PROPERTY_FIELDS = {
    ('product.category', 'property_account_expense_categ',
     'property_account_expense_categ_id'),
    ('product.category', 'property_account_income_categ',
     'property_account_income_categ_id'),
    ('res.partner', 'property_account_payable', 'property_account_payable_id'),
    ('res.partner', 'property_account_receivable',
     'property_account_receivable_id'),
}


def migrate_properties(cr):
    for model, name_v8, name_v9 in PROPERTY_FIELDS:
        openupgrade.logged_query(cr, """
            update ir_model_fields
            set name = '{name_v9}'
            where name = '{name_v8}'
            and model = '{model}'
            """.format(model=model, name_v8=name_v8, name_v9=name_v9))
        openupgrade.logged_query(cr, """
            update ir_property
            set name = '{name_v9}'
            where name = '{name_v8}'
            """.format(name_v8=name_v8, name_v9=name_v9))


@openupgrade.migrate()
def migrate(cr, version):
    # 9.0 introduces a constraint enforcing this
    cr.execute(
        "update account_account set reconcile=True "
        "where type in ('receivable', 'payable')"
    )
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.copy_columns(cr, column_copies)
    migrate_properties(cr)
