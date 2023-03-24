# Copyright 2023 Hunki Enterprises BV (https://hunki-enterprises.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "base", "16.0.1.3/noupdate_changes.xml")
    env.cr.execute(
        "UPDATE res_partner p SET company_registry=c.company_registry "
        "FROM res_company c WHERE c.partner_id=p.id"
    )
