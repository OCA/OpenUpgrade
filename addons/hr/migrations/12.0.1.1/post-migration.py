# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def fill_hr_employee_resource_calendar_and_user(cr):
    openupgrade.logged_query(
        cr, """
        UPDATE hr_employee he
        SET resource_calendar_id = rr.calendar_id,
            user_id = rr.user_id
        FROM resource_resource rr
        WHERE he.resource_id = rr.id
        """
    )


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    fill_hr_employee_resource_calendar_and_user(cr)
    openupgrade.load_data(
        cr, 'hr', 'migrations/12.0.1.1/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        cr, 'hr', [
            'mail_template_data_unknown_employee_email_address',
        ],
    )
