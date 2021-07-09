# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):

    openupgrade.set_xml_ids_noupdate_value(
        env,
        "hr_timesheet",
        [
            "timesheet_line_rule_user",
            "group_timesheet_manager",
            "group_hr_timesheet_approver",
        ],
        True,
    )
