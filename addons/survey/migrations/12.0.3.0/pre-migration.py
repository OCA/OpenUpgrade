# Copyright 2019 Eficent <http://www.eficent.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.set_xml_ids_noupdate_value(
        env, 'survey', ['email_template_survey'], True)
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE survey_user_input
        DROP CONSTRAINT IF EXISTS survey_user_input_deadline_in_the_past
        """,
    )
