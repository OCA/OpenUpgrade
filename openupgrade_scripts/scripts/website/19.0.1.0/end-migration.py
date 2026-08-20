# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def preserve_footer_color_combination(env):
    for website in env["website"].search([]):
        env["website.assets"].with_context(
            website_id=website.id
        ).make_scss_customization(
            "/website/static/src/scss/options/colors/user_color_palette.scss",
            {"footer": 5},
        )


@openupgrade.migrate()
def migrate(env, version):
    preserve_footer_color_combination(env)
