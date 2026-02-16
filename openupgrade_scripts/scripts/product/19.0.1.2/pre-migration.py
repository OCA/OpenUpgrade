# Copyright 2025 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from openupgradelib import openupgrade


def _product_product_is_favorite(env):
    """
    Precreate product.product#is_favorite and set with sql
    """
    openupgrade.add_columns(
        env, [("product.product", "is_favorite", "boolean", False, "product_product")]
    )
    env.cr.execute(
        """
        UPDATE product_product
        SET is_favorite=product_template.is_favorite
        FROM product_template
        WHERE
        product_product.product_tmpl_id=product_template.id
        AND product_template.is_favorite
        """
    )


def _product_supplierinfo_product_tmpl_id(env):
    """
    Precreate product.supplierinfo#{product_tmpl_id,product_uom_id} and set with sql
    """
    openupgrade.add_columns(
        env,
        [
            (
                "product.supplierinfo",
                "product_tmpl_id",
                "many2one",
                None,
                "product_supplierinfo",
            ),
            (
                "product.supplierinfo",
                "product_uom_id",
                "many2one",
                None,
                "product_supplierinfo",
            ),
        ],
    )
    env.cr.execute(
        """
        UPDATE product_supplierinfo
        SET product_tmpl_id=product_product.product_tmpl_id
        FROM product_product
        WHERE
        product_supplierinfo.product_id=product_product.id
        AND product_supplierinfo.product_tmpl_id IS NULL
        """
    )
    env.cr.execute(
        """
        UPDATE product_supplierinfo
        SET product_uom_id=product_template.uom_id
        FROM product_template
        WHERE
        product_supplierinfo.product_tmpl_id=product_template.id
        AND product_supplierinfo.product_uom_id IS NULL
        """
    )


def _prepare_product_packaging_migration(env):
    """
    product.packaging is replaced by UOMs being pointed at by records of product.uom
    Rename product_packaging here to product_uom, and amend with data in post-migration
    Set uom_id to dummy UOM to have the ORM set up the not null constraint correctly
    """
    openupgrade.rename_tables(env.cr, [("product_packaging", "product_uom")])
    openupgrade.rename_models(env.cr, [("product.packaging", "product.uom")])
    openupgrade.add_columns(
        env,
        [
            (
                "product.uom",
                "uom_id",
                "many2one",
                env.ref("uom.product_uom_unit").id,
                "product_uom",
            ),
        ],
    )


@openupgrade.migrate()
def migrate(env, version):
    openupgrade.delete_sql_constraint_safely(
        env,
        "product",
        "product_packaging",
        "positive_qty",
    )
    openupgrade.delete_records_safely_by_xml_id(
        env,
        [
            "product.product_packaging_comp_rule",
        ],
    )
    openupgrade.rename_xmlids(
        env.cr,
        [
            ("product.cat_expense", "product.product_category_expenses"),
            ("product.product_category_all", "product.product_category_goods"),
        ],
    )
    openupgrade.rename_fields(
        env,
        [
            ("product.product", "product_product", "packaging_ids", "product_uom_ids"),
        ],
    )
    _product_product_is_favorite(env)
    _product_supplierinfo_product_tmpl_id(env)
    _prepare_product_packaging_migration(env)
