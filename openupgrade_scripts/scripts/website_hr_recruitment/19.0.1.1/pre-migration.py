# Copyright 2026 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _precreate_hr_job_is_seo_optimized(env):
    openupgrade.add_columns(
        env, [("hr.job", "is_seo_optimized", "boolean", False, "hr_job")]
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE hr_job
        SET is_seo_optimized = True
        WHERE website_meta_title IS NOT NULL
            AND website_meta_description IS NOT NULL
            AND website_meta_keywords IS NOT NULL
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _precreate_hr_job_is_seo_optimized(env)
