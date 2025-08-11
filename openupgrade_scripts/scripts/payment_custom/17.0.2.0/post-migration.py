# Copyright 2024 Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib import openupgrade

from odoo import Command


@openupgrade.migrate()
def migrate(env, version):
    # Instead of loading noupdate_changes we apply method_ids on all payment.provider
    # with custom code (since in multi-company scenario, they can get duplicated)
    env["payment.provider"].search([("code", "=", "custom")]).write(
        {
            "payment_method_ids": [
                Command.set([env.ref("payment_custom.payment_method_wire_transfer").id])
            ],
        }
    )
