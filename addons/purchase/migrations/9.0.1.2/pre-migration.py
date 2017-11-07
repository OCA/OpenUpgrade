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


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.copy_columns(cr, column_copies)
    openupgrade.rename_fields(env, field_renames)
    map_order_state(cr)
