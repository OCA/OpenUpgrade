# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'project', 'migrations/12.0.1.1/noupdate_changes.xml',
        mode='init_no_create')
    openupgrade.load_data(
        env.cr, 'project', 'migrations/12.0.1.1/noupdate_changes2.xml')
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'project.msg_task_data_14_attach',
            'project.msg_task_data_8_attach',
            'project.msg_task_data_14',
            'project.msg_task_data_8',
            'project.project_task_data_8',
        ],
    )
    openupgrade.logged_query(
        env.cr, """
        UPDATE ir_model_data
        SET noupdate = TRUE
        WHERE  module = 'project' AND (name = 'ir_cron_rating_project'
            OR name = 'rating_project_request_email_template')
        """
    )
