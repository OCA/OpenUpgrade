import re

from markupsafe import Markup
from openupgradelib import openupgrade


def extract_footer_copyright_company_name(env):
    """Replace Copyright content in the new v15 template so as not to lose
    content from previous versions if it has been customised, or directly put
    the company name if not customized (which is the previous value).
    """
    for website in env["website"].search([]):
        main_copyright_view = website.with_context(website_id=website.id).viewref(
            "website.footer_copyright_company_name"
        )
        main_copyright_arch = main_copyright_view.arch_db
        main_copyright_pattern = (
            r'<span class="o_footer_copyright_name mr-2">(.*?)<\/span>'
        )
        main_copyright_matches = re.findall(
            main_copyright_pattern,
            main_copyright_arch,
            re.DOTALL,
        )
        if main_copyright_matches:
            website_layout_view = website.with_context(website_id=website.id).viewref(
                "website.layout"
            )
            website_layout_arch = website_layout_view.arch_db or ""
            website_layout_pattern = (
                r'<span class="o_footer_copyright_name mr-2">(.*?)<\/span>'
            )
            website_layout_matches = re.findall(
                website_layout_pattern, website_layout_arch, re.DOTALL
            )
            new_arch = re.sub(
                main_copyright_pattern,
                website_layout_matches[0]
                if website_layout_matches
                else f'<span class="o_footer_copyright_name mr-2">'
                f"Copyright © {Markup.escape(website.company_id.name)}</span>",
                main_copyright_arch,
            )
            main_copyright_view.with_context(website_id=website.id).arch = new_arch


def update_website_form_call(env):
    # Update website views containing calls to "/website_form/" to "/website/form/"
    views = env["ir.ui.view"].search([("arch_db", "like", 'action="/website_form/"')])
    for view in views:
        new_arch_db = view.arch_db.replace(
            'action="/website_form/"', 'action="/website/form/"'
        )
        view.write({"arch_db": new_arch_db})


def update_contact_form_company_description(env):
    """This script updates the Contact Us form on the website with information from the
    company model. It retrieves the necessary data such as company name, address, phone,
    email, and Google Maps link. It then updates the HTML structure of the Contact Us
    form to display this information."""
    common_html_block = """
            <ul class="list-unstyled mb-0 pl-2">
                <li>%s</li>
                <li>
                    <i class="fa fa-map-marker fa-fw mr-2"/>
                    <span class="o_force_ltr">%s<br/>
                    &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; %s %s<br/>
                    &amp;nbsp; &amp;nbsp; &amp;nbsp; &amp;nbsp; %s</span>
                </li>
                <li>
                    <i class="fa fa-phone fa-fw mr-2"/><span class="o_force_ltr">%s </span>
                </li>
                <li><i class="fa fa-1x fa-fw fa-envelope mr-2"/><span>%s</span></li>
                %s
            </ul>
        """
    for website in env["website"].search([]):
        website_contactus_view = website.with_context(website_id=website.id).viewref(
            "website.contactus"
        )
        company = website.company_id
        google_maps_link = (
            (
                f'<li><i class="fa fa-1x fa-fw fa-map-marker mr-2"/>'
                f'<a href="{Markup.escape(company.google_map_link())}" target="_BLANK">'
                f" Google Maps</a></li>"
            )
            if company.google_map_link()
            else ""
        )
        company_info_html = common_html_block % (
            Markup.escape(company.name),
            Markup.escape(company.street),
            Markup.escape(company.city),
            Markup.escape(company.zip),
            Markup.escape(company.country_id.name),
            Markup.escape(company.phone),
            Markup.escape(company.email),
            google_maps_link,
        )
        company_description_pattern = r'<div class="col-lg-4 mt-4 mt-lg-0">(.*?)<\/div>'
        website_contactus_arch = website_contactus_view.arch_db
        new_arch = re.sub(
            company_description_pattern,
            lambda match: company_info_html,
            website_contactus_arch,
            flags=re.DOTALL,
        )
        website_contactus_view.with_context(website_id=website.id).arch = new_arch


def handle_domain_protocol(env):
    """We need to ensure the website protocol prefix to ensure each site correct
    redirection"""
    for website in env["website"].search([("domain", "!=", False)]):
        if website.domain.startswith("http"):
            continue
        website.domain = f"https://{website.domain.rstrip('/')}"


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.logged_query(env.cr, "UPDATE website SET configurator_done = True")
    openupgrade.load_data(env.cr, "website", "15.0.1.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, ["website.action_website_edit"])
    update_website_form_call(env)
    extract_footer_copyright_company_name(env)
    update_contact_form_company_description(env)
    handle_domain_protocol(env)
