from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_membership",
        [
            "membership_membership_line_public",
            "membership_product_product_public",
        ],
        True,
    )
