from openupgradelib import openupgrade


def _map_hr_employee_work_location_to_work_location_id(env):
    env.cr.execute(
        """
        WITH work_location_tmp AS (
            INSERT INTO hr_work_location (name, company_id, address_id, active)
            SELECT DISTINCT emp.work_location, emp.company_id, emp.address_id, true
            FROM hr_employee emp
            WHERE emp.address_id IS NOT NULL
                AND emp.work_location IS NOT NULL
            RETURNING id, name, address_id, company_id
        )
        UPDATE hr_employee emp
        SET work_location_id = wlt.id
        FROM work_location_tmp as wlt
        WHERE wlt.name = emp.work_location
            AND wlt.address_id = emp.address_id
            AND wlt.company_id = emp.company_id
        """
    )


def _map_hr_employee_departure_reason_to_departure_reason_id(env):
    openupgrade.logged_query(
        env.cr,
        """
            UPDATE hr_employee
            SET departure_reason_id=CASE departure_reason
                    WHEN 'fired' THEN % s
                    WHEN 'resigned' THEN % s
                    WHEN 'retired' THEN % s
                END
            WHERE departure_reason IN('fired', 'resigned', 'retired')
        """
        % (
            env.ref("hr.departure_fired").id,
            env.ref("hr.departure_resigned").id,
            env.ref("hr.departure_retired").id,
        ),
    )


@openupgrade.migrate()
def migrate(env, version):
    _map_hr_employee_work_location_to_work_location_id(env)
    _map_hr_employee_departure_reason_to_departure_reason_id(env)
