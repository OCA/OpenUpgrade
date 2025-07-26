# Copyright 2025 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.rename_fields(
        env, [("product.product", "product_product", "ribbon_id", "variant_ribbon_id")]
    )
    openupgrade.logged_query(
        env.cr, "UPDATE product_ribbon SET bg_color='' WHERE bg_color IS NULL"
    )
    openupgrade.logged_query(
        env.cr, "UPDATE product_ribbon SET text_color='' WHERE text_color IS NULL"
    )
