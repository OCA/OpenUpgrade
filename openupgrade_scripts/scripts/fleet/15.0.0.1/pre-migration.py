from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr,
        "fleet_vehicle",
        "description",
        "description",
    )
    openupgrade.convert_field_to_html(
        env.cr,
        "fleet_vehicle_log_contract",
        "notes",
        "notes",
    )
    openupgrade.copy_columns(
        env.cr,
        {"fleet_vehicle_log_services": [("state", None, None)]},
    )
