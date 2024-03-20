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
        UPDATE fleet_vehicle_assignation_log log
            SET driver_employee_id = emp.id
        FROM hr_employee emp
        WHERE log.driver_id IS NOT NULL and log.driver_id = emp.address_home_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    create_drive_employee(env)
