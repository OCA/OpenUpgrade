from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(env.cr, "website_profile", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "website_profile",
        [
            "validation_email",
        ],
    )
