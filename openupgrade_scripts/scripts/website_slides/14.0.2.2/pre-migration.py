from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_slides",
        [
            "rule_slide_channel_global",
            "rule_slide_channel_not_website",
            "rule_slide_slide_global",
            "rule_slide_slide_not_website",
        ],
        True,
    )
