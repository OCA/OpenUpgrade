# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def switch_noupdate_records(env):
    openupgrade.set_xml_ids_noupdate_value(
        env,
        "payment_adyen",
        [
            "adyen_form",
        ],
        True,
    )


@openupgrade.migrate()
def migrate(env, version):
    switch_noupdate_records(env)
