# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.m2o_to_x2m(
        env.cr,
        env['hr.recruitment.stage'], 'hr_recruitment_stage',
        'job_ids', openupgrade.get_legacy_name('job_id')
    )
    openupgrade.load_data(env.cr, 'hr_recruitment', 'migrations/13.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'hr_recruitment', [
            'email_template_data_applicant_congratulations',
            'email_template_data_applicant_interest',
            'email_template_data_applicant_refuse',
        ],
    )
