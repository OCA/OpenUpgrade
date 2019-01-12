# Copyright 2018 Eficent <http://www.eficent.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate(use_env=False)
def migrate(cr, version):
    openupgrade.load_data(
        cr, 'event', 'migrations/12.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        cr, 'event', [
            'event_reminder',
            'event_registration_mail_template_badge',
            'event_subscription',
        ],
    )
