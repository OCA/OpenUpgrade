# -*- coding: utf-8 -*-
# Copyright 2017
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):

    env.ref('project.portal_project_rule').unlink()
    env.ref('project.portal_task_rule').unlink()
    env.ref('project.action_client_project_menu').unlink()
