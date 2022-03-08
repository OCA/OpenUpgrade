# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml.html import fromstring
from openupgradelib import openupgrade
from openupgradelib.openupgrade_tools import convert_html_fragment
import logging

_logger = logging.getLogger(__name__)


def _fill_website_logo(env):
    """V13 introduces website.logo, where v12 used res.company.logo."""
    default_logo = env["website"]._default_logo()
    websites_with_default_logo = env["website"].search([
        ('logo', '=', default_logo),
    ])
    for website in websites_with_default_logo:
        website.logo = website.company_id.logo


def _convert_favicon(env):
    """Version 13 only admits for the favicon ICO files of a size of 256x256, and in
    fact, it converts any input image to this format. We force then a write of this
    field to convert existing favicon to the expected format.
    """
    env.cr.execute("SELECT id, favicon FROM website WHERE favicon IS NOT NULL")
    for website_id, favicon in env.cr.fetchall():
        try:
            env["website"].browse(website_id).write({"favicon": favicon.tobytes()})
        except Exception as e:
            _logger.error(
                "Error while recomputing favicon for website %s: %s",
                website_id,
                repr(e),
            )


def _set_data_anchor_xml_attribute(env):
    """Ensures all anchors in the website (including those in elements
    inserted from the website editor) have a smooth scrolling and easy link
    to them using website editor"""
    website_views = (
        env["ir.ui.view"]
        .with_context(active_test=False)
        .search([("page_ids", "!=", False)])
    )
    for view in website_views:
        doc = fromstring(view.arch_db)
        links = doc.cssselect("a[href^=\#]:not([href=\#])")
        if links:
            replacement = {
                "selector": ", ".join([link.attrib["href"] for link in links]),
                "attr_add": {"data-anchor": "true"},
            }
            view.arch_db = convert_html_fragment(view.arch_db, [replacement])


@openupgrade.migrate()
def migrate(env, version):
    _fill_website_logo(env)
    _convert_favicon(env)
    openupgrade.load_data(env.cr, 'website', 'migrations/13.0.1.0/noupdate_changes.xml')
    _set_data_anchor_xml_attribute(env)
