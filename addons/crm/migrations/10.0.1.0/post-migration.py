# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def _convert_next_activities(env):
    columns = [
        'activity_1_id',
        'activity_2_id',
        'activity_3_id',
    ]
    for column in columns:
        openupgrade.m2o_to_x2m(
            env.cr, env['crm.activity'], 'crm_activity',
            'recommended_activity_ids', openupgrade.get_legacy_name(column),
        )


def _assign_stage_team(env):
    """Assign the team on the stage if there was previously only one team
    assigned.
    """
    env.cr.execute(
        """UPDATE crm_stage
        SET team_id=team_stage_rel.team_id
        FROM (
            SELECT team_id, stage_id
            FROM (
                SELECT team_id, stage_id,
                    row_number()
                    OVER (partition BY stage_id ORDER BY stage_id) AS rnum
                FROM crm_team_stage_rel
            ) t
            WHERE t.rnum = 1
        ) AS team_stage_rel
        WHERE id=team_stage_rel.stage_id
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_next_activities(env)
    _assign_stage_team(env)
