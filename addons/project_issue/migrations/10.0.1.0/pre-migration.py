# -*- coding: utf-8 -*-
# Copyright 2017
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):

    env.ref('project_issue.portal_issue_rule').unlink()
