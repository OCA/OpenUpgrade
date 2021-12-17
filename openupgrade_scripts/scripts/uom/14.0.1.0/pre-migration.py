# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Disappeared constraint
    openupgrade.logged_query(
        env.cr,
        """ALTER TABLE uom_category
           DROP CONSTRAINT IF EXISTS uom_category_uom_category_unique_type""",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, ["uom.constraint_uom_category_uom_category_unique_type"]
    )
