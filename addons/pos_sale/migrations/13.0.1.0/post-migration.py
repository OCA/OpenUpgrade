# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "pos_sale", "migrations/13.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            "point_of_sale.pos_config_main",
        ]
    )
