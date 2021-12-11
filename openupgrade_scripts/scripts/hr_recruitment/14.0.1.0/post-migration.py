# Copyright 2021 Open Source Integrators
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Load noupdate changes
    openupgrade.load_data(env.cr, "hr_recruitment", "14.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr,
        "hr_recruitment",
        [
            "email_template_data_applicant_congratulations",
            "email_template_data_applicant_interest",
        ],
    )
