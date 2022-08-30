# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
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
