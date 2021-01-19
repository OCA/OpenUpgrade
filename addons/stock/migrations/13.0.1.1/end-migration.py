# Copyright 2020 ForgeFlow <https://www.forgeflow.com>
# Copyright 2020 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    env["ir.model.data"].search([
        ("module", "=", "stock"),
        ("model", "=", "stock.location"),
        ("name", "in", ("location_production", "location_inventory",
                        "stock_location_scrapped", "location_procurement")),
    ]).unlink()
