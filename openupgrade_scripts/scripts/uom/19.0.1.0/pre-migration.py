# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.copy_columns(
        env.cr,
        {
            "uom_uom": [
                ("category_id", None, None),
                ("factor", None, None),
                ("rounding", None, None),
                ("uom_type", None, None),
            ]
        },
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("product.decimal_product_uom", "uom.decimal_product_uom"),
            ("uom.uom_square_foot", "uom.product_uom_square_foot"),
            ("uom.uom_square_meter", "uom.product_uom_square_meter"),
        ],
    )
    # this would be cleaned up after the migration, but we can't have it during
    # migration
    openupgrade.delete_sql_constraint_safely(
        env, "uom", "uom_uom", "factor_reference_is_one"
    )
