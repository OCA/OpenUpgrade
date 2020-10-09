# -*- coding: utf-8 -*-
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_fifo_cost_method(env):
    """The real costing method doesn't exist anymore, so the most similar one
    is 'average'. Values mapped according this.
    """
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_default
        SET json_value = '"fifo"'
        WHERE field_id in (SELECT id FROM ir_model_fields
                        WHERE model = 'product.template'
                            AND name = 'cost_method'
                            AND json_value = '"real"')""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_property
        SET value_text = 'fifo'
        WHERE name='property_cost_method'
            AND value_text = 'real'
            AND (res_id LIKE 'product.category,%%'
                 OR res_id LIKE 'product.template,%%')""",
    )


def rename_to_refund_so(env):
    """Rename `to_refund_so` if exists and update field definition."""
    if openupgrade.column_exists(env.cr, 'stock_move', 'to_refund_so'):
        openupgrade.rename_fields(
            env, [('stock.move', 'stock_move', 'to_refund_so', 'to_refund')],
        )


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.update_module_moved_fields(
        env.cr, 'stock.move', ['remaining_qty'], 'stock', 'stock_account',
    )
    update_fifo_cost_method(env)
    rename_to_refund_so(env)
