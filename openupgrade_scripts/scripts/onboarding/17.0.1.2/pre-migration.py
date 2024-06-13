# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _onboarding_step_update_is_per_company(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE onboarding_onboarding_step
        ADD COLUMN IF NOT EXISTS is_per_company BOOLEAN;
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE onboarding_onboarding_step t1
            SET is_per_company = true
        FROM onboarding_onboarding t2
        WHERE t1.onboarding_id = t2.id AND t2.is_per_company = true
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _onboarding_step_update_is_per_company(env)
