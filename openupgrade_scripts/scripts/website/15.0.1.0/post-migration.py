from openupgradelib import openupgrade


def update_website_form_call(env):
    # Update website views containing calls to "/website_form/" to "/website/form/"
    views = env["ir.ui.view"].search([("arch_db", "like", 'action="/website_form/"')])
    for view in views:
        new_arch_db = view.arch_db.replace(
            'action="/website_form/"', 'action="/website/form/"'
        )
        view.write({"arch_db": new_arch_db})


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(env.cr, "UPDATE website SET configurator_done = True")
    openupgrade.load_data(env.cr, "website", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, ["website.action_website_edit"])
    update_website_form_call(env)
