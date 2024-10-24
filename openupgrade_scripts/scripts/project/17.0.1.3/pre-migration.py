# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _rename_fields(env):
    openupgrade.rename_fields(
        env,
        [
            (
                "project.task",
                "project_task",
                "planned_hours",
                "allocated_hours",
            ),
            (
                "project.task.type",
                "project_task_type",
                "auto_validation_kanban_state",
                "auto_validation_state",
            ),
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    _rename_fields(env)
