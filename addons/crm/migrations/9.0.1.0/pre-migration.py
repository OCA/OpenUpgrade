# -*- coding: utf-8 -*-
# © 2016 Therp BV <http://therp.nl>
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
    'crm_case_categ': [
        ('section_id', 'team_id'),
    ],
    'crm_lead': [
        ('section_id', 'team_id'),
        ('ref', None),
        ('ref2', None),
    ],
    'section_stage_rel': [
        ('section_id', 'team_id'),
    ],
}

column_copys = {
    'crm_lead': [
        ('priority', None, None),
    ],
}


def migrate_tracking_campaign(cr):
    # we can't simply rename the table because it's already created when
    # installing utm. There's also a (quite academic) chance that it contains
    # more than demo data
    cr.execute(
        'alter table utm_campaign add column crm_tracking_campaign_id int')
    cr.execute(
        'insert into utm_campaign (name, crm_tracking_campaign_id) '
        'select name, id from crm_tracking_campaign')
    openupgrade.lift_constraints(cr, 'crm_lead', 'campaign_id')
    cr.execute(
        'update crm_lead set campaign_id=c.id '
        'from utm_campaign c where crm_tracking_campaign_id=campaign_id')


def migrate_tracking_medium(cr):
    # see above
    cr.execute(
        'alter table utm_medium add column crm_tracking_medium_id int')
    cr.execute(
        'insert into utm_medium (name, active, crm_tracking_medium_id) '
        'select name, active, id from crm_tracking_medium')
    openupgrade.lift_constraints(cr, 'crm_lead', 'medium_id')
    cr.execute(
        'update crm_lead set medium_id=m.id '
        'from utm_medium m where crm_tracking_medium_id=medium_id')


def migrate_tracking_source(cr):
    # see above
    cr.execute(
        'alter table utm_source add column crm_tracking_source_id int')
    cr.execute(
        'insert into utm_source (name, crm_tracking_source_id) '
        'select name, id from crm_tracking_source')
    openupgrade.lift_constraints(cr, 'crm_lead', 'source_id')
    cr.execute(
        'update crm_lead set source_id=s.id '
        'from utm_source s where crm_tracking_source_id=source_id')


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_columns(cr, column_renames)
    openupgrade.copy_columns(cr, column_copys)
    openupgrade.rename_tables(cr, table_renames)
    openupgrade.rename_models(cr, model_renames)
    migrate_tracking_campaign(cr)
    migrate_tracking_medium(cr)
    migrate_tracking_source(cr)
    openupgrade.map_values(
        cr, openupgrade.get_legacy_name('priority'), 'priority',
        [('4', '3')], table='crm_lead',
    )
    cr.execute("update crm_lead set type='opportunity' where type is null")
    # Needed for crm_lead_lost_reason migration
    cr.execute("ALTER TABLE IF EXISTS crm_lead_lost_reason "
               "RENAME TO crm_lost_reason")
