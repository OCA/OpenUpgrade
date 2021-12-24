# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


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
        env["website"].browse(website_id).write({"favicon": favicon.tobytes()})


@openupgrade.migrate()
def migrate(env, version):
    _fill_website_logo(env)
    _convert_favicon(env)
    openupgrade.load_data(env.cr, 'website', 'migrations/13.0.1.0/noupdate_changes.xml')
