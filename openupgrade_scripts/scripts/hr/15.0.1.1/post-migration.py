from openupgradelib import openupgrade


def _map_hr_employee_work_location_to_work_location_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        WITH work_location_tmp AS (
            INSERT INTO hr_work_location AS hwl (name, company_id, address_id,
                active, create_uid, write_uid, create_date, write_date)
            SELECT emp.work_location, emp.company_id, emp.address_id, TRUE,
                min(emp.create_uid), min(emp.write_uid), min(emp.create_date),
                min(emp.write_date)
            FROM hr_employee emp
            WHERE emp.address_id IS NOT NULL AND emp.work_location IS NOT NULL
            GROUP BY emp.work_location, emp.company_id, emp.address_id
            RETURNING hwl.id, hwl.name, hwl.address_id, hwl.company_id
        )
        UPDATE hr_employee emp
        SET work_location_id = wlt.id
        FROM work_location_tmp as wlt
        WHERE wlt.name = emp.work_location
            AND wlt.address_id = emp.address_id
            AND wlt.company_id = emp.company_id""",
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_work_location hwl
        SET active = FALSE
        WHERE hwl.id NOT IN (
            SELECT DISTINCT emp.work_location_id
            FROM hr_employee emp
            WHERE emp.work_location_id IS NOT NULL
                AND emp.active)""",
    )


def _map_hr_employee_departure_reason_to_departure_reason_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_employee
        SET departure_reason_id = CASE
                WHEN departure_reason = 'fired' THEN %s
                WHEN departure_reason = 'resigned' THEN %s
                WHEN departure_reason = 'retired' THEN %s
            END
        WHERE departure_reason IN ('fired', 'resigned', 'retired')
        """,
        (
            env.ref("hr.departure_fired").id,
            env.ref("hr.departure_resigned").id,
            env.ref("hr.departure_retired").id,
        ),
    )


@openupgrade.migrate()
def migrate(env, version):
    _map_hr_employee_work_location_to_work_location_id(env)
    _map_hr_employee_departure_reason_to_departure_reason_id(env)
    openupgrade.load_data(env.cr, "hr", "15.0.1.1/noupdate_changes.xml")
