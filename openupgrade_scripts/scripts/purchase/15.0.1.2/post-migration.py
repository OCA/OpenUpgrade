from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.convert_field_to_html(
        env.cr,
        "purchase_order",
        openupgrade.get_legacy_name("notes"),
        "notes",
        verbose=False,
    )
    openupgrade.load_data(env.cr, "purchase", "15.0.1.2/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "purchase",
        [
            "email_template_edi_purchase",
            "email_template_edi_purchase_done",
            "email_template_edi_purchase_reminder",
        ],
    )
