from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(
        env.cr,
        "website_sale",
        "15.0.1.1/noupdate_changes.xml",
    )
    openupgrade.delete_record_translations(
        env.cr,
        "website_sale",
        [
            "mail_template_sale_cart_recovery",
        ],
    )
