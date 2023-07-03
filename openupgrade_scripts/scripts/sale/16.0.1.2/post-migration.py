from openupgradelib import openupgrade


def try_delete_noupdate_records(env):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "sale.mail_notification_paynow_online",
            "sale.sale_payment_acquirer_onboarding_wizard_rule",
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "sale", "16.0.1.2/noupdate_changes.xml")
    try_delete_noupdate_records(env)
