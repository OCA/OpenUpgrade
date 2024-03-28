# Copyright 2023 Trần Trường Sơn
# Copyright 2023 Rémy Taymans
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_translations_to_delete = [
    "mail_template_data_project_task",
    "project_manager_all_project_tasks_rule",
    "project_message_user_assigned",
    "rating_project_request_email_template",
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "project", "16.0.1.3/noupdate_changes.xml")
    openupgrade.delete_record_translations(env.cr, "project", _translations_to_delete)
