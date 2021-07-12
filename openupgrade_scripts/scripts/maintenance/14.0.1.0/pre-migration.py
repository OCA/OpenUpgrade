# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "maintenance",
        [
            "equipment_request_rule_admin_user",
            "equipment_request_rule_user",
            "equipment_rule_admin_user",
            "equipment_rule_user",
            "maintenance_equipment_category_comp_rule",
            "maintenance_equipment_comp_rule",
            "maintenance_request_comp_rule",
            "maintenance_team_comp_rule",
        ],
        True,
    )
