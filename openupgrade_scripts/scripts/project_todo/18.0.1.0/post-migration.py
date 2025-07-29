# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade, openupgrade_merge_records


def _change_activity_type(env):
    """
    Change activity records from `reminder` to `todo`.
    """
    old_activity_type = env.ref(
        "project_todo.mail_activity_data_reminder", raise_if_not_found=False
    )
    new_activity_type = env.ref(
        "mail.mail_activity_data_todo", raise_if_not_found=False
    )
    if old_activity_type and new_activity_type:
        openupgrade_merge_records.merge_records(
            env,
            "mail.activity.type",
            [old_activity_type.id],
            new_activity_type.id,
            {"openupgrade_other_fields": "preserve"},
            delete=True,
        )


@openupgrade.migrate()
def migrate(env, version):
    _change_activity_type(env)
    openupgrade.load_data(env, "project_todo", "18.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        ["project_todo.mail_activity_data_reminder"],
    )
