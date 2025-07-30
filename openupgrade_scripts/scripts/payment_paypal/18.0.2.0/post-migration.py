# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE payment_provider
        SET state = 'disabled'
        WHERE code = 'paypal'
        """,
    )
    openupgrade.load_data(env, "payment_paypal", "18.0.2.0/noupdate_changes.xml")
