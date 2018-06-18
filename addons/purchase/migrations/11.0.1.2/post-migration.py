# -*- coding: utf-8 -*-
# Copyright 2017 bloopark systems (<http://bloopark.de>)
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_procurement_fields(env):
    # Update new field created_purchase_line_id at stock.move
    openupgrade.logged_query(
        env.cr, """
        UPDATE stock_move sm
        SET created_purchase_line_id = po.purchase_line_id
        FROM procurement_order po
        WHERE sm.procurement_id = po.id
            AND po.purchase_line_id IS NOT NULL"""
    )
    # Update new field orderpoint_id at purchase.order.line
    openupgrade.logged_query(
        env.cr, """
        UPDATE purchase_order_line pol
        SET orderpoint_id = po.orderpoint_id
        FROM procurement_order po
        WHERE pol.id = po.purchase_line_id
            AND po.orderpoint_id IS NOT NULL"""
    )


@openupgrade.migrate()
def migrate(env, version):
    update_procurement_fields(env)
    openupgrade.load_data(
        env.cr, 'purchase', 'migrations/11.0.1.2/noupdate_changes.xml',
    )
