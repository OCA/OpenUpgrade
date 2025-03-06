# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def update_tracking_date(env):
    openupgrade.date_to_datetime_tz(
        env.cr,
        "gamification_karma_tracking",
        "user_id",
        openupgrade.get_legacy_name("tracking_date"),
        "tracking_date",
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE gamification_karma_tracking
        SET tracking_date = create_date
        WHERE {openupgrade.get_legacy_name("tracking_date")} IS NULL;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    update_tracking_date(env)
    openupgrade.load_data(env, "gamification", "17.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "gamification",
        [
            "email_template_badge_received",
            "mail_template_data_new_rank_reached",
        ],
    )
