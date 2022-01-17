from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_customer",
        ["website_customer_res_partner_tag_public"],
        True,
    )
