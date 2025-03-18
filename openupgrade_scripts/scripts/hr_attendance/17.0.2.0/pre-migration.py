# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_xmlid_renames = [
    (
        "hr_attendance.group_hr_attendance_user",
        "hr_attendance.group_hr_attendance_officer",
    ),
    (
        "hr_attendance.group_hr_attendance_kiosk",
        "hr_attendance.group_hr_attendance_own_reader",
    ),
]


def _hr_attendance_geolocation(env):
    """Rename the fields if the hr_attendance_geolocation module was installed."""
    if openupgrade.column_exists(env.cr, "hr_attendance", "check_in_latitude"):
        openupgrade.rename_fields(
            env,
            [
                (
                    "hr.attendance",
                    "hr_attendance",
                    "check_in_latitude",
                    "in_latitude",
                ),
                (
                    "hr.attendance",
                    "hr_attendance",
                    "check_in_longitude",
                    "in_longitude",
                ),
                (
                    "hr.attendance",
                    "hr_attendance",
                    "check_out_latitude",
                    "out_latitude",
                ),
                (
                    "hr.attendance",
                    "hr_attendance",
                    "check_out_longitude",
                    "out_longitude",
                ),
            ],
        )


def pre_create_hr_attendance_overtime_hours(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE hr_attendance
        ADD COLUMN IF NOT EXISTS overtime_hours numeric
        """,
    )


def fill_res_company_attendance_from_systray(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_company
        ADD COLUMN IF NOT EXISTS attendance_from_systray boolean DEFAULT true
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_company ALTER COLUMN attendance_from_systray DROP DEFAULT
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
    _hr_attendance_geolocation(env)
    pre_create_hr_attendance_overtime_hours(env)
    fill_res_company_attendance_from_systray(env)
