# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).
from openupgradelib import openupgrade


def _fill_website_logo(env):
    """V13 introduces website.logo, where v12 used res.company.logo."""
    websites = env["website"].search([])
    for website in websites:
        website.logo = website.company_id.logo


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    _fill_website_logo(env)
