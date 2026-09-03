# Copyright 2025 Tecnativa - Carlos Lopez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _partner_create_vies_valid_column(env):
    if openupgrade.column_exists(env.cr, "res_partner", "vies_passed"):
        # coming from base_vat_optional_vies module
        openupgrade.rename_fields(
            env,
            [
                (
                    "res.partner",
                    "res_partner",
                    "vies_passed",
                    "vies_valid",
                ),
            ],
        )
        return
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
