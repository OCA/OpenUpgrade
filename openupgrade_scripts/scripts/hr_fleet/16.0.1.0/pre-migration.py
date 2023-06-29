from openupgradelib import openupgrade


def create_drive_employee(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE fleet_vehicle_assignation_log
        ADD IF NOT EXISTS driver_employee_id INT
        """,
    )

    openupgrade.logged_query(
        env.cr,
        """
        UPDATE fleet_vehicle_assignation_log AS fval
        SET driver_employee_id = fv.driver_employee_id
        FROM fleet_vehicle AS fv
        WHERE fval.vehicle_id = fv.id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    create_drive_employee(env)
