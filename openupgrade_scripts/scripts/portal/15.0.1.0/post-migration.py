from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "portal", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "portal",
        [
            "mail_template_data_portal_welcome",
        ],
    )
