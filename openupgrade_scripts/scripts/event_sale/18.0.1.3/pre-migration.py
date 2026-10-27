# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Preserve event products by migrating their type to service tracking.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET service_tracking = 'event'
        WHERE detailed_type = 'event'
        """,
    )
