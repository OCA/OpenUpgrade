# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2019 Tecnativa - Jairo Llopis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade, openupgrade_120


@openupgrade.migrate()
def migrate(env, version):
    cr = env.cr
    openupgrade.load_data(
        cr, 'event', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        cr, 'event', [
            'event_reminder',
            'event_registration_mail_template_badge',
            'event_subscription',
        ],
    )
    openupgrade_120.convert_field_bootstrap_3to4(
        env, "event.event", "description")
