# -*- coding: utf-8 -*-
# © 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# © 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_renames = {
    'sale_order': [
        ('section_id', 'team_id'),
    ],
    'account_invoice': [
        ('section_id', 'team_id'),
    ],
    'sale_order_line_invoice_rel': [
        ('invoice_id', 'invoice_line_id'),
    ],
    # These columns are moved to product_uos module so they are kept to be recovered later.
    'sale_order_line': [
        ('product_uos', None),
    ],
    'sale_order_line': [
        ('product_uos_qty', None),
    ]
}

column_copies = {
    'sale_order': [
        ('state', None, None),
    ],
    'sale_order_line': [
        ('state', None, None),
    ],
}

@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.delete_model_workflow(cr, 'sale.order')
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.copy_columns(cr, column_copies)
