# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openupgradelib import openupgrade


column_copies = {
    'hr_expense_expense': [
        ('state', None, None),
    ],
}

field_renames = [
    ('product.template', 'product_template', 'hr_expense_ok',
     'can_be_expensed'),
    ('hr.expense', 'hr_expense', 'note', 'description'),
    ('hr.expense.line', 'hr_expense_line', 'unit_quantity', 'quantity'),
    ('hr.expense.line', 'hr_expense_line', 'date_value', 'date'),
]

table_renames = [
    ('hr_expense_expense', None),
    ('hr_expense_line', 'hr_expense'),
    ]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_fields(env, field_renames)
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_tables(cr, table_renames)
