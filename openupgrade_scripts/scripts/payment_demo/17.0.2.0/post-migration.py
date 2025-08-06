# Copyright 2025 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo import Command


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env, "payment_demo", "17.0.2.0/noupdate_changes.xml")
    # Instead of loading from noupdate_changes we apply method_ids on all
    # payment.provider with custom code
    # (since in multi-company scenario, they can get duplicated)
    env["payment.provider"].search([("code", "=", "demo")]).write(
        {
            "payment_method_ids": [
                Command.set([env.ref("payment_demo.payment_method_demo").id])
            ],
        }
    )
