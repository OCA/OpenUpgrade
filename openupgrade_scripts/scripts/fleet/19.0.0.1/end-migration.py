# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def model_year(env):
    """
    fleet.vehicle{,.model}#model_year has been changed to a selection field.
    As the ORM chokes on values not in the selection, null those values, but
    copy the original values first
    """
    openupgrade.copy_columns(
        env.cr,
        {
            "fleet_vehicle": [
                ("model_year", None, None),
            ],
            "fleet_vehicle_model": [
                ("model_year", None, None),
            ],
        },
    )
    selection_values = tuple(
        value for value, _display in env["fleet.vehicle"]._get_year_selection()
    )
    for table in ("fleet_vehicle", "fleet_vehicle_model"):
        openupgrade.logged_query(
            env.cr,
            f"UPDATE {table} SET model_year=NULL WHERE model_year NOT IN %s",
            (selection_values,),
        )


@openupgrade.migrate()
def migrate(env, version):
    model_year(env)
