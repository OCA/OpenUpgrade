# Copyright 2023 Coop IT Easy (https://coopiteasy.be)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "hr_contract", "16.0.1.0/noupdate_changes.xml")
