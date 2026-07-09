# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _rename_location_menu_type(env):
    openupgrade.copy_columns(
        env.cr,
        {
            "website_event_menu": [
                ("menu_type", None, None),
            ],
        },
    )
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("menu_type"),
        "menu_type",
        [("location", "other")],
        table="website_event_menu",
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(
        env,
        [("event.event", "is_seo_optimized", "boolean", False, "event_event")],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_event
        SET is_seo_optimized = TRUE
        WHERE website_meta_title IS NOT NULL
           AND website_meta_description IS NOT NULL
           AND website_meta_keywords IS NOT NULL
        """,
    )
    _rename_location_menu_type(env)
