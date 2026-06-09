# Copyright 2026 Tecnativa - Eduardo Ezerouali
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _won_status_set(env):
    # Precreate won_status and set with sql
    openupgrade.add_columns(
        env,
        [
            ("crm.lead", "won_status", "selection", "pending", "crm_lead"),
        ],
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE crm_lead cl
        SET won_status = 'won'
        FROM crm_stage cs
        WHERE cs.id = cl.stage_id
        AND cs.is_won
        AND cl.probability = 100
        """,
    )
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE crm_lead cl
        SET won_status = 'lost'
        WHERE NOT cl.active
        AND cl.probability = 0
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _won_status_set(env)
