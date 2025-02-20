from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "crm_iap_enrich", "16.0.1.1/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "crm_iap_enrich",
        [
            "mail_message_lead_enrich_no_email",
            "mail_message_lead_enrich_notfound",
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "crm_iap_enrich.mail_message_lead_enrich_no_credit",
        ],
    )
