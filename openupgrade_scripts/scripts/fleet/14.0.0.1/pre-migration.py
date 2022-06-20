# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(
        env.cr,
        {"fleet_vehicle_log_contract": [("state", None, None), ("name", None, None)]},
    )
    openupgrade.remove_tables_fks(
        env.cr, ["fleet_vehicle_cost", "fleet_vehicle_log_fuel"]
    )
