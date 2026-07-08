# Copyright 2026 Tecnativa - Pilar Vargas
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Migrate SIRET values to company_registry without overwriting existing data.
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner
           SET company_registry = siret
         WHERE siret IS NOT NULL
           AND siret != ''
           AND (company_registry IS NULL OR company_registry = '')
        """,
    )
