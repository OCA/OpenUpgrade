from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, "website_slides_survey", "15.0.1.0/noupdate_changes.xml"
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides_survey",
        [
            "mail_template_user_input_certification_failed",
        ],
    )
