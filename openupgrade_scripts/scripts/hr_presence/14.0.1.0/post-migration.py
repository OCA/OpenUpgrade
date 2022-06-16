from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr,
        "hr_presence",
        "14.0.1.0/noupdate_changes.xml",
    )
    openupgrade.delete_record_translations(
        env.cr,
        "hr_presence",
        ["mail_template_presence", "sms_template_data_hr_presence"],
    )
