# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade

_field_renames = [("crm.lead", "crm_lead", "lost_reason", "lost_reason_id")]


def res_partner_compute_team_id(env):
    openupgrade.logged_query(
        env.cr,
        """
        UPDATE res_partner as p
        SET team_id = res.parent_team_id
        FROM(
            SELECT p.id, parent.team_id
            FROM res_partner p
              JOIN res_partner parent
              ON p.parent_id = parent.id
            WHERE p.team_id IS NULL
              AND NOT p.is_company
              AND parent.team_id IS NOT NULL
        ) as res(partner_id, parent_team_id)
        WHERE p.id = res.partner_id
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(env, _field_renames)
    res_partner_compute_team_id(env)
