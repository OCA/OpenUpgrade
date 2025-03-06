# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _maintenance_request_company_id(env):
    """We set the company_id value for requests that do not have it.
    We get the value of what will be deductively most appropriate (equipment, team or
    user).
    """
    openupgrade.logged_query(
        env.cr,
        """UPDATE maintenance_request AS request
        SET company_id = equipment.company_id
        FROM maintenance_equipment AS equipment
        WHERE request.company_id IS NULL AND request.equipment_id = equipment.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE maintenance_request AS request
        SET company_id = team.company_id
        FROM maintenance_team AS team
        WHERE request.company_id IS NULL AND request.maintenance_team_id = team.id""",
    )
    openupgrade.logged_query(
        env.cr,
        """UPDATE maintenance_request AS request
        SET company_id = u.company_id
        FROM res_users AS u
        WHERE request.company_id IS NULL AND request.user_id = u.id""",
    )


@openupgrade.migrate()
def migrate(env, version):
    _maintenance_request_company_id(env)
