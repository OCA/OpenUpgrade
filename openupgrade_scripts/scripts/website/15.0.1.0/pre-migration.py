from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(env, "website", ["action_website"], False)
    openupgrade.cow_templates_mark_if_equal_to_upstream(env.cr)
