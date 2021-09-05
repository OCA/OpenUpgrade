# Copyright 2021 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openupgradelib import openupgrade


def _adjust_reward_specific_products(env):
    """Now the value is `specific_products` instead of `specific_product`, and
    the many2one is now a many2many.
    """
    openupgrade.map_values(
        env.cr,
        openupgrade.get_legacy_name("discount_apply_on"),
        "discount_apply_on",
        [("specific_product", "specific_product")],
        table="sale_coupon_reward",
    )
    openupgrade.m2o_to_x2m(
        env.cr,
        env["sale.coupon.reward"],
        "sale_coupon_reward",
        "discount_specific_product_ids",
        "discount_specific_product_id",
    )


@openupgrade.migrate()
def migrate(env, version):
    """Scripts coming from enterprise v12."""
    openupgrade.load_data(
        env.cr, 'sale_coupon', 'migrations/13.0.1.0/noupdate_changes.xml',
    )
    openupgrade.delete_record_translations(env.cr, "sale_coupon", ["mail_template_sale_coupon"])
    _adjust_reward_specific_products(env)
