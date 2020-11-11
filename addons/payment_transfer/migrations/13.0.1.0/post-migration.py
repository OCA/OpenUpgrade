# Copyright 2020 ForgeFlow <http://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # We shouldn't load anything from noupdate_changes, as this may be changed
    # by users in v12 according their needs
    # openupgrade.load_data(
    #    env.cr, "payment_transfer", "migrations/13.0.1.0/noupdate_changes.xml")
    openupgrade.set_xml_ids_noupdate_value(
        env, "payment_transfer", ["transfer_form"], True,
    )
