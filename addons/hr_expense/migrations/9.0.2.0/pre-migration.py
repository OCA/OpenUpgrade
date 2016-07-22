# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L.
# © 2016 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from openupgradelib import openupgrade


column_copies = {
    'hr_expense': [
        ('state', None, None),
    ],
}

column_renames = {
    'product_template': [
        ('hr_expense_ok', 'can_be_expensed'),
    ],
    'hr_expense': [
        ('note', 'description'),
    ],
}

table_renames = [
    ('hr_expense_expense', 'hr_expense'),
    ]

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.copy_columns(cr, column_copies)
