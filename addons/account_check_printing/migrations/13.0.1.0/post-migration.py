# Copyright 2021 Tecnativa - Sergio Teruel
# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def map_account_payment_check_number(env):
    openupgrade.logged_query(
        env.cr, """
        UPDATE account_payment
        SET check_number = '' || %s
        WHERE %s IS NOT NULL
        """, (openupgrade.get_legacy_name('check_number'),
              openupgrade.get_legacy_name('check_number'))
    )


@openupgrade.migrate()
def migrate(env, version):
    map_account_payment_check_number(env)
    openupgrade.load_data(
        env.cr, "account_check_printing", "migrations/13.0.1.0/noupdate_changes.xml",
    )
