from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "website_slides", "14.0.2.2/noupdate_changes.xml")
    env["slide.channel.partner"].search([])._recompute_completion()
    openupgrade.copy_fields_multilang(
        env.cr,
        "slide.channel",
        "slide_channel",
        ["description_short"],
        "id",
        "slide.channel",
        "slide_channel",
        ["description"],
        False,
    )
