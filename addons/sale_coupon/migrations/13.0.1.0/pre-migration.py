# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Scripts coming from enterprise v12."""
    openupgrade.copy_columns(env.cr, {"sale_coupon_reward": [("discount_apply_on", None, None)]})
