# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # survey.stage
    'survey.stage_closed',
    'survey.stage_draft',
    'survey.stage_in_progress',
    'survey.stage_permanent',
]


def fill_survey_survey_stage_id(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE survey_survey su
        SET state = CASE WHEN st.closed = TRUE THEN 'closed'
            WHEN st.name = 'Draft' or st.sequence = 1 THEN 'draft'
            ELSE 'open' END
        FROM survey_stage st
        WHERE su.{} = st.id
        """.format(openupgrade.get_legacy_name('stage_id')),
    )


def move_survey_page_to_survey_question(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE survey_question sq
        SET survey_id = sp.survey_id
        FROM survey_page sp
        WHERE sp.id = sq.{}
        """.format(openupgrade.get_legacy_name('page_id')),
    )
    openupgrade.logged_query(
        env.cr, """
        INSERT INTO survey_question (title, description, sequence, survey_id,
            is_page, old_page_id, create_uid, create_date, write_uid,
            write_date)
        SELECT title, description, sequence, survey_id, TRUE, id,
            create_uid, create_date, write_uid, write_date
        FROM survey_page""",
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE survey_user_input sui
        SET last_displayed_page_id = sq.id
        FROM survey_page sp
        JOIN survey_question sq ON sq.old_page_id = sp.id
        WHERE sui.{} = sp.id""".format(
            openupgrade.get_legacy_name('last_displayed_page_id')),
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE survey_question sq1
        SET page_id = sq2.id
        FROM survey_page sp
        JOIN survey_question sq2 ON sq2.old_page_id = sp.id
        WHERE sq1.{} = sp.id
        """.format(openupgrade.get_legacy_name('page_id')),
    )


def fill_survey_user_input_line_question_sequence(env):
    # needed again for old pages
    openupgrade.logged_query(
        env.cr, """
        UPDATE survey_user_input_line suil
        SET question_sequence = sq.sequence
        FROM survey_question sq
        WHERE suil.question_id = sq.id AND suil.question_sequence IS NULL"""
    )


@openupgrade.migrate()
def migrate(env, version):
    fill_survey_survey_stage_id(env)
    move_survey_page_to_survey_question(env)
    fill_survey_user_input_line_question_sequence(env)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'survey', 'migrations/13.0.3.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'survey', [
            'mail_template_user_input_invite',
        ],
    )
