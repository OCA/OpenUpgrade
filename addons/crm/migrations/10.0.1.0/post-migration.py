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
        """UPDATE crm_stage s
        SET team_id=t.team_id
        FROM (
            SELECT stage_id, MAX(team_id) as team_id, COUNT(stage_id) as count
            FROM crm_team_stage_rel GROUP BY stage_id
        ) t
        WHERE t.count = 1 AND t.stage_id = s.id;
        """
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_next_activities(env)
    _assign_stage_team(env)
    openupgrade.load_data(
        env.cr, 'crm', 'migrations/10.0.1.0/noupdate_changes.xml',
        mode='init_no_create',
    )
