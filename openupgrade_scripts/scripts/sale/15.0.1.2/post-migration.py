from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr, "sale_order", openupgrade.get_legacy_name("note"), "note", verbose=False
    )
    openupgrade.load_data(env.cr, "sale", "15.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "sale",
        [
            "email_template_edi_sale",
            "mail_template_sale_confirmation",
        ],
    )
