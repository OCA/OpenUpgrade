from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "calendar", "15.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "calendar",
        [
            "calendar_template_meeting_changedate",
            "calendar_template_meeting_invitation",
            "calendar_template_meeting_reminder",
        ],
    )
