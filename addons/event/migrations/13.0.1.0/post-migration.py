# Copyright 2020 Payam Yasaie <https://www.tashilgostar.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, 'event', 'migrations/13.0.1.0/noupdate_changes.xml')
    openupgrade.delete_record_translations(
        env.cr, 'event', [
            'event_reminder',
            'event_subscription',
        ],
    )
