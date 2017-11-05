# -*- coding: utf-8 -*-
# Copyright 2016 Therp BV <http://therp.nl>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

field_renames = [
    # renamings with oldname attribute - They also need the rest of operations
    ('crm.claim', 'crm_claim', 'section_id', 'team_id'),
]

column_renames = {
    'crm_claim': [
        ('categ_id', None),
    ],
    'section_claim_stage_rel': [
        ('section_id', 'team_id'),
    ],
}

table_renames = [
    ('section_claim_stage_rel', 'crm_team_claim_stage_rel'),
]


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_fields(env, field_renames)
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, table_renames)
