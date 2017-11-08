# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

column_renames = {
    'hr_employee': [
        ('image', None),
        ('image_medium', None),
        ('image_small', None),
    ],
}


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_columns(cr, column_renames)
    # Reset noupdate flag of base.group_hr_attendance
    env['ir.model.data'].search([
        ('module', '=', 'base'),
        ('name', '=', 'group_hr_attendance'),
    ]).write({'noupdate': 0})
