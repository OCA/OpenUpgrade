# Copyright 2026 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _precreate_res_partner_is_seo_optimized(env):
    openupgrade.add_columns(
        env, [("res.partner", "is_seo_optimized", "boolean", False, "res_partner")]
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner
        SET is_seo_optimized = True
        WHERE website_meta_title IS NOT NULL
            AND website_meta_description IS NOT NULL
            AND website_meta_keywords IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _precreate_res_partner_is_seo_optimized(env)
