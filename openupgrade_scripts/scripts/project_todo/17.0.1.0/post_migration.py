# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # convert users from mail_followers -> user_ids
    # (new feature, users in user_ids can see to do tasks on kanban or list)
    # and fill missing personal stages (_populate_missing_personal_stages)
    todo_tasks = env["project.task"].search([("project_id", "=", False)])
    for task in todo_tasks:
        task.user_ids = task.message_follower_ids.partner_id.user_id
