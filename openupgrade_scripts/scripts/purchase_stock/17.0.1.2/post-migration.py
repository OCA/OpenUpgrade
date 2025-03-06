# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _fill_incoterm_location(env):
    # Fill incoterm_location according
    # https://github.com/odoo/odoo/blob/e73db7e5aa2603e3b7eff20cd630b13f8c215424/
    # addons/purchase_stock/models/account_invoice.py#L161-L169
    openupgrade.logged_query(
        env.cr,
        """
        WITH sub AS (
            SELECT
                MAX(COALESCE(po.incoterm_location, '')) as incoterm_location,
                am.id as move_id
            FROM purchase_order po
            JOIN purchase_order_line pol ON pol.order_id = po.id
            JOIN account_move_line aml ON aml.purchase_line_id = pol.id
            JOIN account_move am ON aml.move_id = am.id
            GROUP BY am.id
        )
        UPDATE account_move am
        SET incoterm_location = sub.incoterm_location
        FROM sub
        WHERE sub.move_id = am.id
        """,
    )


def _purchase_stock_convert_created_purchase_line_id_m2o_to_m2m(env):
    """
    Convert m2o to m2m in 'purchase.stock'
    """
    openupgrade.m2o_to_x2m(
        env.cr,
        env["stock.move"],
        "stock_move",
        "created_purchase_line_ids",
        "created_purchase_line_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_incoterm_location(env)
    _purchase_stock_convert_created_purchase_line_id_m2o_to_m2m(env)
