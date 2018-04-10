# -*- coding: utf-8 -*-
# Copyright 2017 Bloopark (<https://bloopark.de>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

field_renames = [
    ('hr.contract', 'hr_contract', 'working_hours', 'resource_calendar_id')
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    openupgrade.rename_fields(env, field_renames)
