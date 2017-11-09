# -*- coding: utf-8 -*-
# Copyright 2017 Opener B.V. <https://opener.amsterdam>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    env.cr.execute(
        """ UPDATE ir_model_data SET noupdate = false
        WHERE module = 'hr_attendance' AND name = 'hr_attendace_group' """)
