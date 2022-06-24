from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(env, "website", ["action_website"], False)
    openupgrade.convert_field_to_html(
        env.cr, "website", "custom_code_footer", "custom_code_footer"
    )
    openupgrade.convert_field_to_html(
        env.cr, "website", "custom_code_head", "custom_code_head"
    )
    openupgrade.convert_field_to_html(env.cr, "website", "robots_txt", "robots_txt")
