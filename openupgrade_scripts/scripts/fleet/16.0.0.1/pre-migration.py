from openupgradelib import openupgrade


def update_fuel_type(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE fleet_vehicle
        SET fuel_type = %s
        WHERE fuel_type = %s or fuel_type = %s
        """,
        ("full_hybrid", "full_hybrid_gasoline", "hybrid"),
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE fleet_vehicle_model
        SET default_fuel_type = %s
        WHERE default_fuel_type = %s or default_fuel_type = %s
        """,
        ("full_hybrid", "full_hybrid_gasoline", "hybrid"),
    )


@openupgrade.migrate()
def migrate(env, version):
    update_fuel_type(env)
