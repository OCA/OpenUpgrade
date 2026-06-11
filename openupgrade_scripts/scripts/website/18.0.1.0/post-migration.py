# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def migrate_snippet_attribute(env, snippet_class, attribute, value):
    openupgrade.logged_query(
        env.cr,
        rf"""
        UPDATE ir_ui_view v
           SET arch_db = (
               SELECT jsonb_object_agg(
                          lang,
                          regexp_replace(
                              arch,
                              $$<section(?=[^>]*class="[^"]*{snippet_class}[^"]*")(?![^>]*{attribute}=)([^>]*)>$$,
                              $$<section\1 {attribute}="{value}">$$,
                              'g'
                          )
                      )
                 FROM jsonb_each_text(v.arch_db) AS translation(lang, arch)
           )
         WHERE v.website_id IS NOT NULL
           AND v.arch_db::text LIKE '%{snippet_class}%'
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    migrate_snippet_attribute(env, "s_carousel_wrapper", "data-vcss", "001")
    migrate_snippet_attribute(env, "s_three_columns", "data-vxml", "001")
    migrate_snippet_attribute(env, "s_features_grid", "data-vcss", "001")
    migrate_snippet_attribute(env, "s_comparisons", "data-vxml", "001")
    migrate_snippet_attribute(env, "s_comparisons", "data-vcss", "001")
