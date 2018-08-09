# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_record_translations(
        env.cr, 'hr_recruitment', [
            'email_template_data_applicant_refuse',
            'email_template_data_applicant_interest',
        ]
    )
