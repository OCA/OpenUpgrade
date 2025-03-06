# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _fill_event_registration_company_name(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE event_registration
        ADD COLUMN IF NOT EXISTS company_name VARCHAR
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE event_registration AS r
        SET company_name = p.company_name
        FROM res_partner AS p
        WHERE r.partner_id IS NOT NULL
        AND p.type = 'contact'
        AND p.company_name IS NOT NULL;""",
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE event_registration AS r
        SET company_name = p2.company_name
        FROM res_partner AS p
        JOIN res_partner AS p2 ON (p2.parent_id = p.id AND p2.type = 'contact')
        WHERE r.partner_id IS NOT NULL
        AND p2.company_name IS NOT NULL
        AND r.company_name IS NULL;""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _fill_event_registration_company_name(env)
