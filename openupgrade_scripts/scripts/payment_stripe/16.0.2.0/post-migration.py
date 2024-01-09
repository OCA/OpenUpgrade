# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "payment_stripe.payment_method_stripe",
        ],
    )
    openupgrade.load_data(env.cr, "payment_stripe", "16.0.2.0/noupdate_changes.xml")
