from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(env.cr, "website_slides", "15.0.2.4/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_slides",
        [
            "mail_template_slide_channel_invite",
            "slide_template_published",
            "slide_template_shared",
        ],
    )
