# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_copies = {
    'survey_question': [
        ('validation_max_date', None, None),
        ('validation_min_date', None, None),
        ('type', None, None),
    ],
    'survey_user_input_line': [
        ('value_date', None, None),
    ],
}


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(env.cr, _column_copies)
    openupgrade.map_values(
        env.cr, openupgrade.get_legacy_name('type'), 'type',
        [('datetime', 'date')], table='survey_question',
    )
