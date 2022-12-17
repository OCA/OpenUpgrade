from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "hr_timesheet", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "hr_timesheet",
        [
            "group_hr_timesheet_approver",
            "group_hr_timesheet_user",
        ],
    )
