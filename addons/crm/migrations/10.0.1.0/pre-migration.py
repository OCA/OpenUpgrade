# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

_column_renames = {
    'crm_activity': [
        ('activity_1_id', None),
        ('activity_2_id', None),
        ('activity_3_id', None),
    ],
    'crm_lead': [
        ('last_activity_id', None),
    ],
    'crm_lead_tag': [
        ('team_id', None),
    ],
    'crm_stage': [
        ('type', None),
    ],
}

_xmlid_renames = [
    ('crm.stage_lead5', 'crm.stage_lead4'),
]


def _rename_xml_ids(env):
    # As v9 demo data contains already a crm.stage_lead4, we need to remove
    # previously that XML-ID in case it exists
    env.cr.execute(
        "DELETE FROM ir_model_data WHERE module='crm' AND name='stage_lead4'"
    )
    openupgrade.rename_xmlids(env.cr, _xmlid_renames)


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_columns(env.cr, _column_renames)
    _rename_xml_ids(env)
