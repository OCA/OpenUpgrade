# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    copy_subcontracting_dropshipping_to_resupply(env)
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["mrp_subcontracting_dropshipping.route_subcontracting_dropshipping"],
    )


def copy_subcontracting_dropshipping_to_resupply(env):
    legacy_col = openupgrade.get_legacy_name("subcontracting_dropshipping_to_resupply")
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE stock_warehouse
        SET subcontracting_to_resupply = TRUE
        WHERE {legacy_col}
        """,
    )
