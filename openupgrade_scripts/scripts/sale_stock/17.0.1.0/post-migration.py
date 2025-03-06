# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Fill delivery_date and incoterm_location according
    # https://github.com/odoo/odoo/blob/00818b7bfaf22635b0c40b3b9c7e37e0c9789da1/
    # addons/sale_stock/models/account_move.py#L116-L134
    openupgrade.logged_query(
        env.cr,
        """
        WITH sub AS (
            SELECT
                MAX(so.effective_date) as effective_date,
                MAX(COALESCE(so.incoterm_location, '')) as incoterm_location,
                am.id as move_id
            FROM sale_order so
            JOIN sale_order_line sol ON sol.order_id = so.id
            JOIN sale_order_line_invoice_rel rel ON rel.order_line_id = sol.id
            JOIN account_move_line aml ON rel.invoice_line_id = aml.id
            JOIN account_move am ON aml.move_id = am.id
            GROUP BY am.id
        )
        UPDATE account_move am
        SET delivery_date = sub.effective_date,
            incoterm_location = sub.incoterm_location
        FROM sub
        WHERE sub.move_id = am.id
        """,
    )
