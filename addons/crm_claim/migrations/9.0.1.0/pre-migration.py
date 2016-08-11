# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

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


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_tables(cr, table_renames)
