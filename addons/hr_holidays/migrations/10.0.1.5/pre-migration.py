# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - Jairo Llopis
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.delete_model_workflow(env.cr, "hr.holidays")
