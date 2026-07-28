# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from openupgradelib import openupgrade

deleted_xmlids = [
    "hr_fleet.fleet_rule_contract_visibility_user",
    "hr_fleet.fleet_rule_odometer_visibility_user",
    "hr_fleet.fleet_rule_service_visibility_user",
    "hr_fleet.fleet_rule_vehicle_visibility_user",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, deleted_xmlids)
