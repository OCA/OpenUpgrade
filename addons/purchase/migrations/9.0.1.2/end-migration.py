# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - Jairo Llopis
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade


@openupgrade.logging()
def deferred_pol_qty_received_compute(env):
    """Complete migration of purchase.order.line#qty_received for products
    with BoMs. We don't go further in initial filtering, as this number should
    be low and it's not going to be heavy to be computed.
    """
    if 'mrp.bom' not in env:
        return  # mrp not installed
    pol_todo = env["purchase.order.line"].search([
        ("order_id.state", "in", ['purchase', 'done']),
        ("product_id.type", "in", ['consu', 'product']),
        ("product_id.product_tmpl_id.bom_ids", "!=", False),
    ])
    pol_todo._compute_qty_received()


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    deferred_pol_qty_received_compute(env)
