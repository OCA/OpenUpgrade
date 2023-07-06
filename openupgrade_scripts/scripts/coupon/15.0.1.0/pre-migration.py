# Copyright 2023 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    # Delete old template translations before the new template is renamed to ensure that
    # we remove the terms properly
    openupgrade.delete_record_translations(
        env.cr,
        "coupon",
        [
            "mail_template_sale_coupon",
        ],
    )
    openupgrade.rename_xmlids(
        env.cr,
        [("coupon.mail_template_sale_coupon", "sale_coupon.mail_template_sale_coupon")],
    )
