# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "hr_attendance.menu_hr_attendance_kiosk_mode",
                "hr_attendance.menu_hr_attendance_kiosk_no_user_mode",
            )
        ],
    )
