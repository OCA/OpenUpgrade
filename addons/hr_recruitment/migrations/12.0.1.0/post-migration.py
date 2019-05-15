# Copyright 2019 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'hr_recruitment', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'hr_recruitment', [
            'email_template_data_applicant_interest',
            'email_template_data_applicant_congratulations',
            'email_template_data_applicant_refuse',
        ],
    )
    openupgrade.delete_records_safely_by_xml_id(
        env, [
            'hr_recruitment.email_template_data_applicant_employee',
        ],
    )
