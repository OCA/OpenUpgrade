# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _partner_create_vies_valid_column(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE res_partner
        ADD COLUMN IF NOT EXISTS vies_valid BOOLEAN;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _partner_create_vies_valid_column(env)
