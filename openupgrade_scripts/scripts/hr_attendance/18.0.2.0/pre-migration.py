# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade

_new_columns = [
    ("hr.attendance", "expected_hours", "float"),
    ("hr.attendance", "overtime_status", "selection", "approved"),
    ("hr.attendance", "validated_overtime_hours", "float"),
    ("res.company", "absence_management", "boolean", False),
    ("res.company", "attendance_overtime_validation", "selection", "no_validation"),
    ("res.company", "auto_check_out", "boolean", False),
    ("res.company", "auto_check_out_tolerance", "float", 2),
]


def fill_hr_attendance_expected_hours(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_attendance
        SET expected_hours = COALESCE(worked_hours, 0) - COALESCE(overtime_hours, 0)
        """,
    )


def fill_hr_attendance_validated_overtime_hours(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_attendance
        SET validated_overtime_hours = COALESCE(overtime_hours, 0)
        """,
    )


@openupgrade.migrate()
def migrate(env, version=None):
    openupgrade.add_columns(env, _new_columns)
    fill_hr_attendance_expected_hours(env)
    fill_hr_attendance_validated_overtime_hours(env)
