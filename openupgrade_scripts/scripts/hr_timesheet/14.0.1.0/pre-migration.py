# Copyright 2021 Open Source Integrators
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _fill_task_overtime(env):
    openupgrade.logged_query(env.cr, "ALTER TABLE project_task ADD overtime NUMERIC")
    openupgrade.logged_query(
        env.cr,
        """UPDATE project_task SET overtime =
        CASE WHEN planned_hours > 0 THEN GREATEST(
            effective_hours + subtask_effective_hours - planned_hours, 0.0
        )
        ELSE 0 END""",
    )


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
    _fill_task_overtime(env)
    # Remove obsolete view from "hr_timesheet_analysis" module that would
    # collide with the new "timesheet_action_view_all_pivot" view
    openupgrade.delete_records_safely_by_xml_id(
        env, ["hr_timesheet_analysis.act_hr_timesheet_line_view_all_pivot"]
    )
