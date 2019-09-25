# -*- coding: utf-8 -*-
# Copyright 2016 Tecnativa - Vicent Cubells <vicent.cubells@tecnativa.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


column_renames = {
    'hr_applicant': [
        ('priority', None),
        ('availability', None),
    ]}

model_renames = [
    ('hr.applicant_category', 'hr.applicant.category'),
]

table_renames = [
    ('hr_recruitment_source', None),
]


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_models(cr, model_renames)
