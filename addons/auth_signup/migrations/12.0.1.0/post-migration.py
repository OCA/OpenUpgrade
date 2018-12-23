# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(
        env.cr, 'auth_signup', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'auth_signup', [
            'set_password_email',
            'reset_password_email',
            'mail_template_user_signup_account_created',
        ],
    )
