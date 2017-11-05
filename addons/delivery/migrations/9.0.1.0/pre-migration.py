# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_renames = {
    'delivery_grid_line': [
        ('price_type', None),
    ],
    'delivery_grid': [
        ('carrier_id', None),
    ],
    'delivery_grid_country_rel': [
        ('grid_id', 'carrier_id'),
    ],
    'delivery_grid_state_rel': [
        ('grid_id', 'carrier_id'),
    ],
}

field_renames = [
    ('delivery.grid.line', 'delivery_grid_line', 'type', 'variable'),
    ('delivery.grid.line', 'delivery_grid_line', 'grid_id', 'carrier_id'),
]

column_copies = {
    'delivery_grid_line': [
        ('list_price', 'list_base_price', None),
    ],
}

table_renames = [
    ('delivery_carrier', None),
    ('delivery_grid', 'delivery_carrier'),
    ('delivery_grid_line', 'delivery_price_rule'),
    ('delivery_grid_country_rel', 'delivery_carrier_country_rel'),
    ('delivery_grid_state_rel', 'delivery_carrier_state_rel'),
]


def correct_object_references(cr):
    """Point sale order and stock picking to grid records (that will be
    renamed as carrier objects)."""
    openupgrade.lift_constraints(cr, 'sale_order', 'carrier_id')
    openupgrade.logged_query(
        cr, """
        UPDATE sale_order so SET carrier_id = dg.id
        FROM delivery_grid dg, delivery_carrier dc
        WHERE dg.carrier_id = dc.id AND so.carrier_id = dc.id
        """,
    )
    openupgrade.lift_constraints(cr, 'stock_picking', 'carrier_id')
    openupgrade.logged_query(
        cr, """
        UPDATE stock_picking sp SET carrier_id = dg.id
        FROM delivery_grid dg, delivery_carrier dc
        WHERE dg.carrier_id = dc.id AND sp.carrier_id = dc.id
        """,
    )


def correct_rule_prices(cr):
    """Version 8 only allows to put a fixed or variable price, not both.
    Now version 9 have a field for each option. We copy the value on both
    fields and zero the field that doesn't correspond to the version in 8.
    """
    openupgrade.copy_columns(cr, column_copies)
    cr.execute(
        """
        UPDATE delivery_grid_line
        SET list_price = 0
        WHERE {0} = 'fixed'
        """.format(openupgrade.get_legacy_name('price_type'))
    )
    cr.execute(
        """
        UPDATE delivery_grid_line
        SET list_base_price = 0
        WHERE {0} = 'variable'
        """.format(openupgrade.get_legacy_name('price_type'))
    )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    correct_object_references(cr)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(env, field_renames)
    correct_rule_prices(cr)
    openupgrade.rename_tables(cr, table_renames)
    # TODO: if the same product is used for multiple carriers, duplicate it
    # for having a correct structure of 1 product = 1 carrier
