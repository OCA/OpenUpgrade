# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

XMLID_RENAMES = [
    # Mail templates
    ('hr_recruitment.hr_welcome_new_employee',
     'hr_recruitment.email_template_data_applicant_employee'),
    ('hr_recruitment.applicant_interest',
     'hr_recruitment.email_template_data_applicant_interest'),
    ('hr_recruitment.applicant_refuse',
     'hr_recruitment.email_template_data_applicant_refuse'),
    # Data
    ('hr_recruitment.rcol_3_1_1', 'hr_recruitment_survey.rcol_3_1_1'),
    ('hr_recruitment.rcol_3_1_2', 'hr_recruitment_survey.rcol_3_1_2'),
    ('hr_recruitment.rcol_3_1_3', 'hr_recruitment_survey.rcol_3_1_3'),
    ('hr_recruitment.rcol_3_1_4', 'hr_recruitment_survey.rcol_3_1_4'),
    ('hr_recruitment.rcol_3_1_5', 'hr_recruitment_survey.rcol_3_1_5'),
    ('hr_recruitment.recruitment_1_2_1',
     'hr_recruitment_survey.recruitment_1_2_1'),
    ('hr_recruitment.recruitment_1_2_2',
     'hr_recruitment_survey.recruitment_1_2_2'),
    ('hr_recruitment.recruitment_1_3_1',
     'hr_recruitment_survey.recruitment_1_3_1'),
    ('hr_recruitment.recruitment_1_3_2',
     'hr_recruitment_survey.recruitment_1_3_2'),
    ('hr_recruitment.recruitment_1_3_3',
     'hr_recruitment_survey.recruitment_1_3_3'),
    ('hr_recruitment.recruitment_1_3_4',
     'hr_recruitment_survey.recruitment_1_3_4'),
    ('hr_recruitment.recruitment_1_3_5',
     'hr_recruitment_survey.recruitment_1_3_5'),
    ('hr_recruitment.recruitment_1_3_6',
     'hr_recruitment_survey.recruitment_1_3_6'),
    ('hr_recruitment.recruitment_1_3_7',
     'hr_recruitment_survey.recruitment_1_3_7'),
    ('hr_recruitment.recruitment_1_3_8',
     'hr_recruitment_survey.recruitment_1_3_8'),
    ('hr_recruitment.rrow_2_1_1', 'hr_recruitment_survey.rrow_2_1_1'),
    ('hr_recruitment.rrow_2_1_10', 'hr_recruitment_survey.rrow_2_1_10'),
    ('hr_recruitment.rrow_2_1_11', 'hr_recruitment_survey.rrow_2_1_11'),
    ('hr_recruitment.rrow_2_1_12', 'hr_recruitment_survey.rrow_2_1_12'),
    ('hr_recruitment.rrow_2_1_13', 'hr_recruitment_survey.rrow_2_1_13'),
    ('hr_recruitment.rrow_2_1_2', 'hr_recruitment_survey.rrow_2_1_2'),
    ('hr_recruitment.rrow_2_1_3', 'hr_recruitment_survey.rrow_2_1_3'),
    ('hr_recruitment.rrow_2_1_4', 'hr_recruitment_survey.rrow_2_1_4'),
    ('hr_recruitment.rrow_2_1_5', 'hr_recruitment_survey.rrow_2_1_5'),
    ('hr_recruitment.rrow_2_1_6', 'hr_recruitment_survey.rrow_2_1_6'),
    ('hr_recruitment.rrow_2_1_7', 'hr_recruitment_survey.rrow_2_1_7'),
    ('hr_recruitment.rrow_2_1_8', 'hr_recruitment_survey.rrow_2_1_8'),
    ('hr_recruitment.rrow_2_1_9', 'hr_recruitment_survey.rrow_2_1_9'),
    ('hr_recruitment.recruitment_1', 'hr_recruitment_survey.recruitment_1'),
    ('hr_recruitment.recruitment_2', 'hr_recruitment_survey.recruitment_2'),
    ('hr_recruitment.recruitment_3', 'hr_recruitment_survey.recruitment_3'),
    ('hr_recruitment.recruitment_1_1',
     'hr_recruitment_survey.recruitment_1_1'),
    ('hr_recruitment.recruitment_1_2',
     'hr_recruitment_survey.recruitment_1_2'),
    ('hr_recruitment.recruitment_1_3',
     'hr_recruitment_survey.recruitment_1_3'),
    ('hr_recruitment.recruitment_2_1',
     'hr_recruitment_survey.recruitment_2_1'),
    ('hr_recruitment.recruitment_2_2',
     'hr_recruitment_survey.recruitment_2_2'),
    ('hr_recruitment.recruitment_2_3',
     'hr_recruitment_survey.recruitment_2_3'),
    ('hr_recruitment.recruitment_2_4',
     'hr_recruitment_survey.recruitment_2_4'),
    ('hr_recruitment.recruitment_3_1',
     'hr_recruitment_survey.recruitment_3_1'),
    ('hr_recruitment.recruitment_form',
     'hr_recruitment_survey.recruitment_form'),
]


def update_field_module(cr):
    """Rename references for moved fields"""
    new_name = 'hr_recruitment'
    old_name = 'hr_recruitment_survey'
    # get moved model fields
    moved_fields = tuple(['response_id', 'survey_id'])
    cr.execute(
        """
        SELECT id
        FROM ir_model_fields
        WHERE model IN ('hr.applicant', 'hr.job') AND name in %s
        """, (moved_fields,))
    field_ids = tuple([r[0] for r in cr.fetchall()])
    # update ir_model_data, the subselect allows to avoid duplicated XML-IDs
    query = ("UPDATE ir_model_data SET module = %s "
             "WHERE module = %s AND res_id IN %s AND name NOT IN "
             "(SELECT name FROM ir_model_data WHERE module = %s)")
    openupgrade.logged_query(
        cr, query, (new_name, old_name, field_ids, new_name)
    )
    # update ir_translation
    query = ("UPDATE ir_translation SET module = %s "
             "WHERE module = %s AND res_id IN %s")
    openupgrade.logged_query(cr, query, (new_name, old_name, field_ids))


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_xmlids(env.cr, XMLID_RENAMES)
    update_field_module(env.cr)
