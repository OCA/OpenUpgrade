from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "event", "18.0.1.9/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "event",
        [
            "event_registration_mail_template_badge",
            "event_reminder",
            "event_subscription",
        ],
    )
