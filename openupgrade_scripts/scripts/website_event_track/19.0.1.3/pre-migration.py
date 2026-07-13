# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_new_columns = [("event.track", "is_seo_optimized", "boolean", False, "event_track")]


def _fill_event_track_is_seo_optimized(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE event_track
        SET is_seo_optimized = True
        WHERE website_meta_title IS NOT NULL
            AND website_meta_description IS NOT NULL
            AND website_meta_keywords IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.add_columns(env, _new_columns)
    _fill_event_track_is_seo_optimized(env)
