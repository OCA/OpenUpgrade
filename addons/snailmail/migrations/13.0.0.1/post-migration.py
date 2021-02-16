# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_snailmail_letter_state(env):
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name('state'),
        'state',
        [('draft', 'pending'),
         ],
        table='snailmail_letter',
    )


@openupgrade.migrate()
def migrate(env, version):
    map_snailmail_letter_state(env)
