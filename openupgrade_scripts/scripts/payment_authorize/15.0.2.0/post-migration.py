from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "payment_authorize", "15.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "payment_authorize.assets_frontend",
            "payment_authorize.authorize_form",
            "payment_authorize.authorize_s2s_form",
            "ayment_authorize.payment_authorize_redirect",
        ],
    )
