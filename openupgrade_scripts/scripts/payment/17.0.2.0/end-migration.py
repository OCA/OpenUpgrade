# Copyright 2024 Viindoo Technology Joint Stock Company (Viindoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    activated_providers = env["payment.provider"].search([("state", "!=", "disabled")])
    activated_providers._activate_default_pms()
