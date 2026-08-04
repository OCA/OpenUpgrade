# Copyright 2026 Heliconia Solutions Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    reassign_alert_date_activities(env)


def reassign_alert_date_activities(env):
    """Reassign alert-date activities to the standard To-do type
    before the old activity type record is removed by the data sync."""
    old_type = env.ref("product_expiry.mail_activity_type_alert_date_reached", False)
    new_type = env.ref("mail.mail_activity_data_todo", False)
    if old_type and new_type:
        env.cr.execute(
            """
            UPDATE mail_activity
            SET activity_type_id = %s,
                summary = COALESCE(summary, 'Alert Date Reached')
            WHERE activity_type_id = %s
            """,
            (new_type.id, old_type.id),
        )
