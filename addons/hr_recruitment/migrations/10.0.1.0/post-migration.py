# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


def fill_hr_recruitment_stage_job_id(env):
    """Fill the existing stage record with the first job found, and then
    duplicate this stage for each successive job found.
    """
    env.cr.execute("SELECT job_id, stage_id FROM job_stage_rel")
    stages = {}
    stage_obj = env['hr.recruitment.stage']
    for row in env.cr.fetchall():
        job_id = row[0]
        stage_id = row[1]
        if stage_id in stages:
            # This is not the first time this stage is assigned
            stages[stage_id].copy({'job_id': job_id})
        else:
            stage = stage_obj.browse(stage_id)
            stage.job_id = job_id
            stages[stage_id] = stage


def assign_recruitment_groups(env):
    """Assign users with group group_hr_user also to the new
    group_hr_recruitment_user and make the same for manager ones.
    """
    env.ref('hr.group_hr_user').users.write({
        'groups_id': [
            (4, env.ref('hr_recruitment.group_hr_recruitment_user').id)
        ]
    })
    env.ref('hr.group_hr_manager').users.write({
        'groups_id': [
            (4, env.ref('hr_recruitment.group_hr_recruitment_manager').id)
        ]
    })


@openupgrade.migrate()
def migrate(env, version):
    fill_hr_recruitment_stage_job_id(env)
    assign_recruitment_groups(env)
    openupgrade.load_data(
        env.cr, 'hr_recruitment', 'migrations/10.0.1.0/noupdate_changes.xml',
    )
