# Copyright 2022 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE product_template
        SET detailed_type = 'event'
        WHERE event_ok""",
    )
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "event_sale",
        [
            "product_product_event",
        ],
        True,
    )
