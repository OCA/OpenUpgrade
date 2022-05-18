# Copyright 2021 Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "base", "15.0.1.3/noupdate_changes.xml")
