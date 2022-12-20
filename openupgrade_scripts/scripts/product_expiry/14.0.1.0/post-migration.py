# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET use_expiration_date = TRUE
        WHERE expiration_time > 0""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template pt
        SET use_expiration_date = TRUE
        FROM stock_production_lot spl
        JOIN product_product pp ON spl.product_id = pp.id
        WHERE pp.product_tmpl_id = pt.id AND (
            spl.expiration_date IS NOT NULL OR spl.removal_date IS NOT NULL
            OR spl.use_date IS NOT NULL OR spl.alert_date IS NOT NULL)""",
    )
    openupgrade.logged_query(
        # sml has lot_it
        env.cr,
        """
        UPDATE stock_move_line sml
        SET expiration_date = spl.expiration_date
        FROM stock_production_lot spl
        WHERE spl.id = sml.lot_id AND spl.expiration_date IS NOT NULL
        """,
    )
    openupgrade.logged_query(
        # use sml.create_date
        env.cr,
        """
        UPDATE stock_move_line sml
        SET expiration_date = sml.create_date + make_interval(
            days => pt.expiration_time)
        FROM product_product pp
        JOIN product_template pt ON pp.product_tmpl_id = pt.id, stock_picking sp
        JOIN stock_picking_type spt ON sp.picking_type_id = spt.id
        WHERE
            sml.product_id = pp.id
            AND sml.picking_id = sp.id
            AND spt.use_create_lots
            AND pt.use_expiration_date
            AND pt.expiration_time IS NOT NULL
            AND sml.expiration_date IS NULL""",
    )
