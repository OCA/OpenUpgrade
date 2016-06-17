# coding: utf-8
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(cr, version):
    openupgrade.rename_tables(cr, [('survey', 'survey_survey')])
    openupgrade.rename_models(cr, [('survey', 'survey.survey')])
