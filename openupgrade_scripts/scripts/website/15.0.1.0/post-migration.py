from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(env.cr, "UPDATE website SET configurator_done = True")
    openupgrade.load_data(env.cr, "website", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, ["website.action_website_edit"])
