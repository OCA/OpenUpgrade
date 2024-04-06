# SPDX-FileCopyrightText: 2024 Tecnativa - Pedro M. Baeza
# SPDX-License-Identifier: AGPL-3.0-or-later
from openupgradelib import openupgrade


def _precreate_stock_move_line_carrier_name(env):
    """It seems Odoo doesn't handle with a SQL related fields with more than one path
    (several dots), so let's do it here for optimizing times.
    """
    openupgrade.logged_query(
        env.cr, "ALTER TABLE stock_move_line ADD carrier_name VARCHAR"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE stock_move_line sml
        SET carrier_name = dc.name
        FROM stock_picking sp
        JOIN delivery_carrier dc ON dc.id = sp.carrier_id
        WHERE sml.picking_id = sp.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _precreate_stock_move_line_carrier_name(env)
