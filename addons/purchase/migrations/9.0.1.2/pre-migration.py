# -*- coding: utf-8 -*-
# Copyright 2015 Eficent Business and IT Consulting Services S.L. -
# Jordi Ballester Alomar
# Copyright 2015 Serpent Consulting Services Pvt. Ltd. - Sudhir Arya
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_copies = {
    'purchase_order': [
        ('state', None, None),
    ],
}

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('purchase.order', 'purchase_order', 'fiscal_position',
     'fiscal_position_id'),
]

column_renames = {
    'purchase_order_taxe': [
        ('ord_id', 'purchase_order_line_id'),
        ('tax_id', 'account_tax_id'),
    ]
}

table_renames = [
    ('purchase_order_taxe', 'account_tax_purchase_order_line_rel'),
]


def map_order_state(cr):
    """ Map values for state field in purchase.order and purchase.order.line.
    Do this in the pre script because it influences the automatic calculation
    of the computed fields wrt. invoicing """
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('state'), 'state',
        [('approved', 'purchase'), ('bid', 'sent'),
         ('confirmed', 'to approve'), ('draft', 'draft'),
         ('except_invoice', 'purchase'), ('except_picking', 'purchase')],
        table='purchase_order')

    cr.execute("""
        UPDATE purchase_order_line l
        SET state = o.state
        FROM purchase_order o
        WHERE l.order_id = o.id""")


def purchase_invoice_lines(cr):
    """ odoo 8.0 introduced account.invoice.line's Many2one 'purchase_line_id'
    but was not used until 9.0. Here, the 'invoice_lines' counterpart on the
    purchase order line is migrated to a One2many field. The field already
    exists, so it is easy to do in the pre-script so that the computation of
    the invoiced quantities will be correct. """
    openupgrade.logged_query(
        cr,
        """ UPDATE account_invoice_line ail
        SET purchase_line_id = rel.order_line_id
        FROM purchase_order_line_invoice_rel rel
        WHERE rel.invoice_id = ail.id """)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_fields(env, field_renames)
    # This should be run before table renames
    openupgrade.rename_columns(env.cr, column_renames)
    openupgrade.rename_tables(env.cr, table_renames)
    map_order_state(cr)
    purchase_invoice_lines(cr)
