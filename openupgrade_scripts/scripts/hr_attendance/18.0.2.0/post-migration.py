# Copyright 2025 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _hr_attendance_autoclose(env):
    """If the hr_attendance_autoclose module was installed, we will define
    the appropriate values in res.company: auto_check_out +
    auto_check_out_tolerance fields.
    """
    if not openupgrade.column_exists(
        env.cr, "res_company", "hr_attendance_autoclose_reason"
    ):
        return
    env.cr.execute(
        """
        UPDATE res_company
        SET auto_check_out = true, auto_check_out_tolerance = (
            attendance_maximum_hours_per_day - calendar.hours_per_day
        )
        FROM resource_calendar AS calendar
        WHERE res_company.resource_calendar_id = calendar.id
        AND res_company.attendance_maximum_hours_per_day IS NOT NULL
        """
    )
    env.cr.execute(
        """
        UPDATE hr_attendance ha
        SET out_mode = 'auto_check_out'
        FROM hr_employee he, res_company rc,
            hr_attendance_hr_attendance_reason_rel rel
        WHERE ha.employee_id = he.id
        AND he.company_id = rc.id
        AND rel.hr_attendance_id = ha.id
        AND rel.hr_attendance_reason_id = rc.hr_attendance_autoclose_reason
        AND rc.hr_attendance_autoclose_reason IS NOT NULL
        """
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "hr_attendance.check_attendance_cron",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    _hr_attendance_autoclose(env)
