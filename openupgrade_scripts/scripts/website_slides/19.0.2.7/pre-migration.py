# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _precompute_is_seo_optimized(env, model_name, table_name):
    openupgrade.add_columns(
        env,
        [(model_name, "is_seo_optimized", "boolean", False, table_name)],
    )
    openupgrade.logged_query(
        env.cr,
        f"""
        UPDATE {table_name}
        SET is_seo_optimized = TRUE
        WHERE website_meta_title IS NOT NULL
        AND website_meta_description IS NOT NULL
        AND website_meta_keywords IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    for model_name, table_name in [
        ("slide.channel", "slide_channel"),
        ("slide.slide", "slide_slide"),
    ]:
        _precompute_is_seo_optimized(env, model_name, table_name)
