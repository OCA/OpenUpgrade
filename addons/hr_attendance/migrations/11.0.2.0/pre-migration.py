# -*- coding: utf-8 -*-
# Copyright 2017 Bloopark (<http://www.bloopark.de>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('hr.group_hr_attendance', 'hr_attendance.group_hr_attendance'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
