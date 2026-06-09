# Copyright 2026 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_renamed_models = [
    ("hr.attendance.overtime", "hr.attendance.overtime.line"),
]

_renamed_tables = [
    ("hr_attendance_overtime", "hr_attendance_overtime_line"),
]

_renamed_fields = [
    ("hr.attendance", "hr_attendance", "in_city", "in_location"),
    ("hr.attendance", "hr_attendance", "out_city", "out_location"),
    (
        "hr.attendance.overtime.line",
        "hr_attendance_overtime_line",
        "duration_real",
        "manual_duration",
    ),
]

SQL_EMPLOYEE2TZ = """
(
    SELECT
    hr_employee.id employee_id,
    COALESCE(
        MIN(resource_calendar.tz),
        MIN(resource_resource.tz),
        MIN(company_resource_calendar.tz)
    ) zone
    FROM
    hr_employee
    JOIN
    resource_resource
    ON
    hr_employee.resource_id=resource_resource.id
    LEFT JOIN
    resource_calendar
    ON
    resource_resource.calendar_id=resource_calendar.id
    JOIN
    res_company
    ON
    hr_employee.company_id=res_company.id
    LEFT JOIN
    resource_calendar company_resource_calendar
    ON
    res_company.resource_calendar_id=company_resource_calendar.id
    GROUP BY
    hr_employee.id
) employee2zone
"""


def hr_attendance_date(env):
    """
    Pre-fill hr.attendance#date
    """
    openupgrade.add_fields(
        env, [("date", "hr.attendance", "hr_attendance", "date", None, "hr_attendance")]
    )
    env.cr.execute(
        f"""
        UPDATE
        hr_attendance
        SET date=(check_in AT TIME ZONE COALESCE(employee2zone.zone, 'utc'))::date
        FROM
        {SQL_EMPLOYEE2TZ}
        WHERE
        employee2zone.employee_id=hr_attendance.employee_id
        AND date IS NULL
        """
    )


def hr_attendance_overtime_line_fields(env):
    """
    Pre-fill new fields of  hr.attendance.overtime.line
    """
    openupgrade.add_fields(
        env,
        [
            (
                "status",
                "hr.attendance.overtime.line",
                "hr_attendance_overtime_line",
                "char",
                None,
                "hr_attendance",
                "approved",
            ),
            (
                "time_start",
                "hr.attendance.overtime.line",
                "hr_attendance_overtime_line",
                "datetime",
                None,
                "hr_attendance",
            ),
            (
                "time_stop",
                "hr.attendance.overtime.line",
                "hr_attendance_overtime_line",
                "datetime",
                None,
                "hr_attendance",
            ),
        ],
    )
    # date is required in v19, fill with create_date if empty, possibly wrong
    env.cr.execute(
        f"""
        UPDATE hr_attendance_overtime_line SET date=(
            create_date AT TIME ZONE COALESCE(employee2zone.zone, 'utc')
        )::date
        FROM
        {SQL_EMPLOYEE2TZ}
        WHERE
        employee2zone.employee_id=hr_attendance_overtime_line.employee_id
        AND
        date IS NULL
        """
    )
    # time_start, time_stop need to match some check_in, check_out from hr_attendance
    env.cr.execute(
        """
        UPDATE
        hr_attendance_overtime_line
        SET
        time_start=hr_attendance.check_in,
        time_stop=hr_attendance.check_out
        FROM
        hr_attendance
        WHERE
        hr_attendance.employee_id=hr_attendance_overtime_line.employee_id
        AND
        hr_attendance.date=hr_attendance_overtime_line.date
        """
    )
    # for companies with manager approval, set status from state on attendance
    env.cr.execute(
        """
        UPDATE
        hr_attendance_overtime_line
        SET
        status=hr_attendance.overtime_status
        FROM
        hr_employee, res_company, hr_attendance
        WHERE
        hr_attendance.check_in=hr_attendance_overtime_line.time_start
        AND
        hr_attendance.employee_id=hr_attendance_overtime_line.employee_id
        AND
        hr_attendance_overtime_line.employee_id=hr_employee.id
        AND
        hr_employee.company_id=res_company.id
        AND
        res_company.attendance_overtime_validation = 'by_manager'
        """
    )


def hr_attendance_validated_overtime_hours(env):
    """
    Pre-fill hr.attendance#validated_overtime_hours
    """
    openupgrade.add_fields(
        env,
        [
            (
                "validated_overtime_hours",
                "hr.attendance",
                "hr_attendance",
                "float",
                None,
                "hr_attendance",
            )
        ],
    )
    # validated_overtime_hours is the sum of approved overtime lines
    env.cr.execute(
        """
        UPDATE
        hr_attendance
        SET
        validated_overtime_hours=grouped_overtime_lines.sum_duration
        FROM
        (
            SELECT
            employee_id, time_start, SUM(manual_duration) sum_duration
            FROM
            hr_attendance_overtime_line
            WHERE
            status='approved'
            GROUP BY
            employee_id, time_start
        ) grouped_overtime_lines
        WHERE
        grouped_overtime_lines.employee_id=hr_attendance.employee_id AND
        grouped_overtime_lines.time_start=hr_attendance.check_in
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_models(env.cr, _renamed_models)
    openupgrade.rename_tables(env.cr, _renamed_tables)
    openupgrade.rename_fields(env, _renamed_fields)
    # order matters
    hr_attendance_date(env)
    hr_attendance_overtime_line_fields(env)
    hr_attendance_validated_overtime_hours(env)
