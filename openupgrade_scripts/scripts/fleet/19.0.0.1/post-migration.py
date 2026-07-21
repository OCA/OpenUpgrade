# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

deleted_xmlids = [
    "fleet.fleet_rule_contract_visibility_user",
    "fleet.fleet_rule_odometer_visibility_user",
    "fleet.fleet_rule_service_visibility_user",
    "fleet.fleet_rule_vehicle_visibility_user",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env,
        "fleet",
        "19.0.0.1/noupdate_changes.xml",
    )
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
