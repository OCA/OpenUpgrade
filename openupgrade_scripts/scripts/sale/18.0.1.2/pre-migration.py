# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env,
        [("product.document", "product_document", "attached_on", "attached_on_sale")],
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "sale.sale_order_action_view_quotation_kanban",
                "sale.action_quotations_kanban",
            ),
            (
                "sale.sale_order_action_view_quotation_tree",
                "sale.action_quotations_tree",
            ),
        ],
    )
    openupgrade.add_columns(
        env,
        [("sale.order.line", "technical_price_unit", "float", None, "sale_order_line")],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE sale_order_line
        SET technical_price_unit = price_unit
        """,
    )
    openupgrade.delete_sql_constraint_safely(
        env, "sale", "sale_order_line", "accountable_required_fields"
    )
