from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(env.cr, "gamification", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "gamification",
        [
            "email_template_badge_received",
            "email_template_goal_reminder",
            "mail_template_data_new_rank_reached",
        ],
    )
