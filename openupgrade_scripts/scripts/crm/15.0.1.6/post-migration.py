from openupgradelib import openupgrade


def try_delete_noupdate_records(env):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "crm.mail_alias_lead_info",
            "crm.email_template_opportunity_mail",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "crm", "15.0.1.6/noupdate_changes.xml")
    try_delete_noupdate_records(env)
