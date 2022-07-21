from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "website_livechat",
        ["im_livechat_channel_rule_public"],
        True,
    )
