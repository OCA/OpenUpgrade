import re

from openupgradelib import openupgrade


def extract_footer_copyright_company_name(env):
    """Replace Copyright content in the new v15 template so as not to lose
    content from previous versions if it has been customised, or directly put
    the company name if not customized (which is the previous value).
    """
    main_copyright_view = env.ref("website.footer_copyright_company_name")
    if not main_copyright_view:
        return
    main_copyright_arch = main_copyright_view.arch_db
    main_copyright_pattern = r'<span class="o_footer_copyright_name mr-2">(.*?)<\/span>'
    main_copyright_matches = re.findall(
        main_copyright_pattern,
        main_copyright_arch,
        re.DOTALL,
    )
    for website in env["website"].search([]):
        view = env["ir.ui.view"].search(
            [("key", "=", "website.layout"), ("website_id", "=", website.id)]
        )
        website_layout_arch = view.arch_db or ""
        website_layout_pattern = (
            r'<span class="o_footer_copyright_name mr-2">(.*?)<\/span>'
        )
        website_layout_matches = re.findall(
            website_layout_pattern, website_layout_arch, re.DOTALL
        )
        new_arch = main_copyright_arch.replace(
            main_copyright_matches[0],
            website_layout_matches
            and website_layout_matches[0]
            or f"Copyright © {website.company_id.name}",
        )
        main_copyright_view.with_context(website_id=website.id).arch_db = new_arch


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
    extract_footer_copyright_company_name(env)
