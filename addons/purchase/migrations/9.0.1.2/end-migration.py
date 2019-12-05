# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - Jairo Llopis
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from openupgradelib import openupgrade


@openupgrade.logging()
def deferred_pol_qty_received_compute(env):
    """Complete migration of purchase.order.line#qty_received

    Skip records that were optimized in SQL in post-migration.
    """
    # Execute https://bit.ly/2PgUKaT for matching records
    pol_todo = env["purchase.order.line"].search([
        ("order_id.state", "in", ['purchase', 'done']),
        ("product_id.type", "in", ['consu', 'product']),
    ])
    pol_todo._compute_qty_received()


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    deferred_pol_qty_received_compute(env)
