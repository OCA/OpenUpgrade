# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_xmlid_renames = [
    ('base.group_hr_user', 'hr.group_hr_user'),
    ('base.group_hr_manager', 'hr.group_hr_manager'),
    ('base.group_hr_attendance', 'hr.group_hr_attendance'),
]


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)
