from openupgradelib import openupgrade


def _map_fleet_vehicle_log_services_state(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("state"),
        "state",
        [("todo", "new")],
        table="fleet_vehicle_log_services",
    )


@openupgrade.migrate()
def migrate(env, version):
    _map_fleet_vehicle_log_services_state(env)
    openupgrade.load_data(env.cr, "fleet", "15.0.0.1/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "fleet.ir_rule_fleet_log_contract",
        ],
    )
