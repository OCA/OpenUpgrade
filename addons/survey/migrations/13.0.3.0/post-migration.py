# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade

_unlink_by_xmlid = [
    # survey.stage
    'survey.stage_closed',
    'survey.stage_draft',
    'survey.stage_in_progress',
    'survey.stage_permanent',
]


def update_survey_user_input_last_displayed_page_id(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE survey_user_input sui
        SET last_displayed_page_id = sq.id
        FROM survey_question sq
        WHERE sui.{last_displayed_page_id} = sq.{page_id}
        """.format(last_displayed_page_id=openupgrade.get_legacy_name('last_displayed_page_id'),
                   page_id=openupgrade.get_legacy_name('page_id'))
    )


@openupgrade.migrate()
def migrate(env, version):
    update_survey_user_input_last_displayed_page_id(env.cr)
    openupgrade.delete_records_safely_by_xml_id(env, _unlink_by_xmlid)
    openupgrade.load_data(env.cr, 'survey', 'migrations/13.0.3.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'survey', [
            'module_category_marketing_survey',
            'mail_template_user_input_invite',
        ],
    )
