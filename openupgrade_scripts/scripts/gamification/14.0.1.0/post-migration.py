# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def create_karma_trackings(env):
    openupgrade.logged_query(
        env.cr,
        """
        INSERT INTO gamification_karma_tracking (user_id, old_value, new_value,
            tracking_date, create_uid, write_uid, create_date, write_date)
        SELECT id, 0, karma, create_date::date, create_uid, write_uid,
            create_date, write_date
        FROM res_users
        WHERE karma IS NOT NULL AND karma != 0""",
    )


@openupgrade.migrate()
def migrate(env, version):
    create_karma_trackings(env)
    openupgrade.load_data(env.cr, "gamification", "14.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "gamification",
        ["email_template_badge_received", "email_template_goal_reminder"],
    )
