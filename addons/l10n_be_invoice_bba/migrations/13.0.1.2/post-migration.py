# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "l10n_be_invoice_bba", "migrations/13.0.1.2/noupdate_changes.xml")
