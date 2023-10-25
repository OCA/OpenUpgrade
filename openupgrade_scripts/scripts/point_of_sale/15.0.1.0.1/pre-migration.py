# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def merge_pos_order_return_module(env):
    """
    The pos_order_return module is now merged into point_of_sale. We can hook into
    the new core functionality just renaming the proper fields.
    """
    if openupgrade.column_exists(env.cr, "pos_order", "returned_order_id"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "pos.order.line",
                    "pos_order_line",
                    "returned_line_id",
                    "refunded_orderline_id",
                ),
                (
                    "pos.order.line",
                    "pos_order_line",
                    "refund_line_ids",
                    "refund_orderline_ids",
                ),
            ],
        )


@openupgrade.migrate()
def migrate(env, version):
    merge_pos_order_return_module(env)
    openupgrade.rename_fields(
        env,
        [
            (
                "pos.config",
                "pos_config",
                "iface_customer_facing_display",
                "iface_customer_facing_display_via_proxy",
            ),
            (
                "pos.payment.method",
                "pos_payment_method",
                "cash_journal_id",
                "journal_id",
            ),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE pos_config ADD COLUMN IF NOT EXISTS warehouse_id INTEGER
        """,
    )
