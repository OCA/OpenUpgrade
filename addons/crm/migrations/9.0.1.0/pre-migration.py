# -*- coding: utf-8 -*-
# Copyright 2016 Therp BV <http://therp.nl>
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

model_renames = [
    ('crm.case.categ', 'crm.lead.tag'),
    ('crm.case.stage', 'crm.stage'),
]
table_renames = [
    ('crm_case_categ', 'crm_lead_tag'),
    ('crm_case_stage', 'crm_stage'),
    ('section_stage_rel', 'crm_team_stage_rel'),
]

column_renames = {
    'crm_lead': [
        ('ref', None),
        ('ref2', None),
    ],
    'section_stage_rel': [
        ('section_id', 'team_id'),
    ],
}

field_renames = [
    ('crm.case.categ', 'crm_case_categ', 'section_id', 'team_id'),
    # renamings with oldname attribute - They also need the rest of operations
    ('crm.lead', 'crm_lead', 'section_id', 'team_id'),
]

column_copys = {
    'crm_lead': [
        ('priority', None, None),
    ],
}

xmlid_renames = [
    ('crm.stage_lead3', 'crm.stage_lead2'),
    ('crm.stage_lead4', 'crm.stage_lead3'),
    ('crm.stage_lead6', 'crm.stage_lead5'),
]


def _adjust_crm_stages(cr):
    """Delete XML-IDs of deprecated stages (for not conflicting with new ones
    with same name), and rename those of the equivalent ones.
    """
    openupgrade.logged_query(
        cr,
        "DELETE FROM ir_model_data WHERE module = 'crm' AND name IN "
        "('stage_lead2', 'stage_lead5', 'stage_lead_7')",
    )
    openupgrade.rename_xmlids(cr, xmlid_renames)


@openupgrade.migrate(use_env=True)
def migrate(env, version):
    cr = env.cr
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.rename_fields(env, field_renames)
    openupgrade.copy_columns(cr, column_copys)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_models(cr, model_renames)
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('priority'), 'priority',
        [('4', '3')], table='crm_lead',
    )
    cr.execute("update crm_lead set type='opportunity' where type is null")
    if openupgrade.table_exists(cr, 'crm_lead_lost_reason'):
        openupgrade.rename_tables(cr, [('crm_lead_lost_reason', 'crm_lost_reason')])
    _adjust_crm_stages(cr)
