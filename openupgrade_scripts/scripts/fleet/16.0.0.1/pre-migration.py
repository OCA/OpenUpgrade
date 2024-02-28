# Copyright 2023 Viindoo - Nguyễn Việt Lâm
# Copyright 2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _prefill_fleet_vehicle_category_id(env):
    openupgrade.logged_query(
        env.cr, "ALTER TABLE fleet_vehicle ADD COLUMN IF NOT EXISTS category_id INT4"
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE fleet_vehicle fv
        SET category_id = fvm.category_id
        FROM fleet_vehicle_model fvm
        WHERE fvm.id = fv.model_id AND fvm.category_id IS NOT NULL
        """,
    )


def _update_fuel_type(env):
    for table, column in (
        ("fleet_vehicle", "fuel_type"),
        ("fleet_vehicle_model", "default_fuel_type"),
    ):
        openupgrade.logged_query(
            env.cr,
            f"""
            UPDATE {table}
            SET {column} = 'full_hybrid'
            WHERE {column} IN ('full_hybrid_gasoline', 'hybrid')
            """,
        )


@openupgrade.migrate()
def migrate(env, version):
    _prefill_fleet_vehicle_category_id(env)
    _update_fuel_type(env)
