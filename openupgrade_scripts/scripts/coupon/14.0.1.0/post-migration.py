# Copyright 2021 ForgeFlow S.L.  <https://www.forgeflow.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.load_data(env.cr, "coupon", "14.0.1.0/noupdate_changes.xml")
    openupgrade.delete_record_translations(
        env.cr, "coupon", ["mail_template_sale_coupon"]
    )
