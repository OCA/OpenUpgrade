from openupgradelib import openupgrade

_xmlids_to_delete = [
    "hr_fleet.fleet_rule_contract_visibility_user",
    "hr_fleet.fleet_rule_odometer_visibility_user",
    "hr_fleet.fleet_rule_service_visibility_user",
    "hr_fleet.fleet_rule_vehicle_visibility_user",
    "hr_fleet.res_users_view_form_preferences",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(env, _xmlids_to_delete)
