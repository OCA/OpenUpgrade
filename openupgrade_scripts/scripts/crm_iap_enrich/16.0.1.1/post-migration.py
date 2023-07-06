from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "crm_iap_enrich.mail_message_lead_enrich_no_credit",
        ],
    )
