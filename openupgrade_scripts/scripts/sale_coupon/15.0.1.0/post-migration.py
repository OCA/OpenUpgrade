# Copyright 2023 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # no differences detected
    # openupgrade.load_data(env.cr, "sale_coupon", "15.0.1.0/noupdate_changes.xml")
    pass
